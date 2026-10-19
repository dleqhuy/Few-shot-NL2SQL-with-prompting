"""Provider contract tests; no external API calls or credentials required."""

import json
import os
import threading
import tempfile
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch

from llm_provider import LLMConfig, generate


class ConfigTests(unittest.TestCase):
    def config(self, env, **kwargs):
        with patch.dict(os.environ, env, clear=True), patch("llm_provider.load_dotenv"):
            return LLMConfig.from_env(**kwargs)

    def test_custom_provider_takes_precedence(self):
        config = self.config({
            "LLM_API_KEY": "local-key", "OPENAI_API_KEY": "other-key",
            "LLM_BASE_URL": "http://localhost:20128/v1/",
            "OPENAI_BASE_URL": "https://example.org/v1",
            "LLM_MODEL": "cx/gpt-6-luna", "OPENAI_MODEL": "other-model",
        })
        self.assertEqual(config, LLMConfig(
            "local-key", "http://localhost:20128/v1", "cx/gpt-6-luna"))

    def test_openai_aliases_and_defaults(self):
        config = self.config({"OPENAI_API_KEY": "test-key"})
        self.assertEqual(config.base_url, "https://api.openai.com/v1")
        self.assertEqual(config.model, "gpt-4")
        config = self.config({"OPENAI_API_KEY": "test-key",
                              "OPENAI_API_BASE": "http://localhost/v1"},
                             default_model="gpt-4-32k")
        self.assertEqual(config.base_url, "http://localhost/v1")
        self.assertEqual(config.model, "gpt-4-32k")

    def test_missing_key_fails_before_generation(self):
        with self.assertRaisesRegex(ValueError, "LLM_API_KEY"):
            self.config({})

    def test_dotenv_loads_without_overriding_exported_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text(
                "LLM_API_KEY=file-key\nLLM_BASE_URL=http://localhost:20128/v1\n"
                "LLM_MODEL=file-model\n")
            with patch("llm_provider.__file__", str(root / "llm_provider.py")), \
                    patch.dict(os.environ, {"LLM_MODEL": "exported-model"}, clear=True):
                config = LLMConfig.from_env()
            self.assertEqual(config.api_key, "file-key")
            self.assertEqual(config.base_url, "http://localhost:20128/v1")
            self.assertEqual(config.model, "exported-model")


class RequestTests(unittest.TestCase):
    def test_spider_and_bird_use_custom_endpoint(self):
        captured = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                captured.append((self.path, self.headers["Authorization"], body))
                payload = json.dumps({"choices": [{"message": {
                    "role": "assistant", "content": "SELECT 1"}}],
                    "usage": {"prompt_tokens": 5, "completion_tokens": 3,
                              "total_tokens": 8}}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            config = LLMConfig("test-key", f"http://127.0.0.1:{server.server_port}/v1",
                               "cx/gpt-6-luna")
            self.assertEqual(generate(config, "Question", max_tokens=350,
                                      stop=["#", ";", "\n\n"]), "SELECT 1")
            from langchain.chat_models import ChatOpenAI
            from langchain.chains import LLMChain
            from langchain.prompts import (
                ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate,
            )

            chat = ChatOpenAI(openai_api_key=config.api_key,
                              openai_api_base=config.base_url,
                              model=config.model, temperature=0, max_tokens=2000)
            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template("Generate SQL"),
                HumanMessagePromptTemplate.from_template("{question}")])
            self.assertEqual(LLMChain(llm=chat, prompt=prompt).run(question="Question"),
                             "SELECT 1")
        finally:
            server.shutdown()
            server.server_close()
            worker.join()
        for path, auth, body in captured:
            self.assertEqual(path, "/v1/chat/completions")
            self.assertEqual(auth, "Bearer test-key")
            self.assertEqual(body["model"], "cx/gpt-6-luna")
        self.assertEqual(len(captured), 2)
        self.assertEqual(captured[0][2]["stop"], ["#", ";", "\n\n"])
        self.assertEqual(captured[0][2]["max_tokens"], 350)
        self.assertEqual(captured[1][2]["max_tokens"], 2000)
        self.assertEqual(captured[1][2]["messages"][0]["role"], "system")


if __name__ == "__main__":
    unittest.main()
