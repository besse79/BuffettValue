import json
import tempfile
import unittest
from pathlib import Path
from buffettvalue.sec_download import fetch_companyfacts

class Response:
    def __init__(self, data):
        self.data = data
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, size):
        return self.data

class DownloadTests(unittest.TestCase):
    def test_valid_download_cache_and_headers(self):
        seen = []
        def opener(request, timeout):
            seen.append((request.full_url, request.get_header("User-agent"), timeout))
            return Response(json.dumps({"cik": 123, "facts": {}}).encode())
        with tempfile.TemporaryDirectory() as temp:
            doc, path = fetch_companyfacts(123, "BuffettValue Research contact@example.org", temp, opener)
            self.assertEqual(doc["cik"], 123)
            self.assertEqual(json.loads(Path(path).read_text())["cik"], 123)
            self.assertIn("CIK0000000123", seen[0][0])
            self.assertIn("contact@example.org", seen[0][1])

    def test_reject_bad_user_agent(self):
        with self.assertRaises(ValueError):
            fetch_companyfacts(123, "anonymous", "/tmp/unused")

    def test_reject_wrong_cik_without_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                fetch_companyfacts(123, "Research contact@example.org", temp,
                                   lambda req, timeout: Response(b'{"cik":124,"facts":{}}'))
            self.assertEqual(list(Path(temp).glob("*.json")), [])

    def test_reject_missing_facts(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                fetch_companyfacts(123, "Research contact@example.org", temp,
                                   lambda req, timeout: Response(b'{"cik":123}'))

    def test_reject_fractional_cik(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                fetch_companyfacts(123, "Research contact@example.org", temp,
                                   lambda req, timeout: Response(b'{"cik":123.5,"facts":{}}'))
            self.assertEqual(list(Path(temp).glob("*.json")), [])
