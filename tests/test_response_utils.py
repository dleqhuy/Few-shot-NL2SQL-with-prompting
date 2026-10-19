import unittest
from response_utils import classification_parts, sql_response

class ResponseTest(unittest.TestCase):
    def test_labels_and_missing_subquestion(self):
        self.assertEqual(classification_parts('Label: "NON-NESTED"', 'question'), ('NON-NESTED', 'question'))
        self.assertEqual(classification_parts('Label: EASY', 'q')[0], 'EASY')
        self.assertEqual(classification_parts('No usable label', 'q'), ('NESTED', 'q'))

    def test_sql_formatting(self):
        self.assertEqual(sql_response('SELECT count(*) FROM singer', True), 'SELECT count(*) FROM singer')
        self.assertEqual(sql_response('count(*) FROM singer', True), 'SELECT count(*) FROM singer')
        self.assertEqual(sql_response('```sql\nSELECT 1\n```', True), 'SELECT 1')
        self.assertEqual(sql_response('SQL: `SELECT 1`'), 'SELECT 1')
        self.assertEqual(sql_response('SELECT `Name`'), 'SELECT `Name`')
