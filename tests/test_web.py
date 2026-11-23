import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.parse import urlencode
from buffettvalue.web import Handler, EXAMPLE, page

class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, method, path, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        headers = {"Content-Type": "application/x-www-form-urlencoded"} if body is not None else {}
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        result = (response.status, response.read().decode(), dict(response.getheaders()))
        conn.close()
        return result

    def test_health(self):
        status, body, _ = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertIn("RESEARCH_ONLY", body)

    def test_home(self):
        status, body, _ = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("valeur intrinsèque", body)

    def test_calculate(self):
        status, body, headers = self.request("POST", "/calculate", urlencode(EXAMPLE))
        self.assertEqual(status, 200)
        self.assertIn("intrinsic_per_share", body)
        self.assertIn("no-store", headers["Cache-Control"])

    def test_reject_duplicate(self):
        status, _, _ = self.request("POST", "/calculate", urlencode(EXAMPLE) + "&price=100")
        self.assertEqual(status, 400)

    def test_reject_invalid(self):
        status, _, _ = self.request("POST", "/calculate", urlencode({**EXAMPLE, "discount": 0.01}))
        self.assertEqual(status, 400)

    def test_escape(self):
        self.assertIn("&lt;script&gt;", page(error="<script>"))
