# Few-shot-NL2SQL-with-prompting

## Table of contents
* [Dataset](#dataset)
* [Setup](#setup)
* [Citation](#citation)


## dataset
To reproduce the results reported in the paper, please download the Spider dataset from the link below and create a data directory containing the tables.json and dev.json files.

```
$ Spider dataset = "https://drive.google.com/uc?export=download&id=1TqleXec_OykOYFREKKtschzY29dUcVAQ"
```


## setup
Use Python 3.9 or 3.10 for this repository's pinned dependencies.

The Spider and BIRD scripts support OpenAI and OpenAI-compatible providers.
Copy `.env.example` to `.env` and set your credentials:

```sh
cp .env.example .env
```

```dotenv
LLM_BASE_URL=http://localhost:20128/v1
LLM_API_KEY=your-api-key
LLM_MODEL=cx/gpt-6-luna
```

The scripts load `.env` from the repository directory. Exported environment
variables override this file. `.env` is ignored by Git; do not commit API keys.
The base URL must include `/v1` when required by your provider.

For the official OpenAI API, use `LLM_BASE_URL=https://api.openai.com/v1`
and set `LLM_MODEL` to a chat model available to your account. The aliases
`OPENAI_API_KEY`, `OPENAI_BASE_URL` (or `OPENAI_API_BASE`), and `OPENAI_MODEL`
are also supported; `LLM_*` values take precedence. Without a model override,
Spider uses `gpt-4` and BIRD uses `gpt-4-32k`.

To run this project, use the following commands:

```
$ pip3 install -r requirements.txt
$ echo "Start running DIN-SQL.py"
$ python3 DIN-SQL.py --dataset ./data/ --output predicted_sql.txt
$ echo "Finished running DIN-SQL.py"
```

For BIRD, prepare `dev/dev.json` and `dev/dev_databases`, then run
`python3 DIN-SQL_BIRD.py`. It uses the same provider configuration.

Run the provider tests with `python3 -m unittest discover -s tests -v`.
These tests use a temporary local HTTP server and do not contact your provider.
## citation 

``` 
@article{pourreza2023din,
  title={DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction},
  author={Pourreza, Mohammadreza and Rafiei, Davood},
  journal={arXiv preprint arXiv:2304.11015},
  year={2023}
}
```

