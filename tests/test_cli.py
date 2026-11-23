import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from buffettvalue.__main__ import evaluate

ROOT = Path(__file__).resolve().parents[1]
GOOD = json.loads((ROOT / "examples/dcf-example.json").read_text())

class DCFCLITests(unittest.TestCase):
    def test_research_never_trades(self):
        result = evaluate(GOOD)
        self.assertEqual(result["mode"], "RESEARCH_ONLY")
        self.assertFalse(result["paper_eligible"])
        self.assertGreater(result["intrinsic_per_share"], 0)

    def test_extra_fields_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({**GOOD, "paper_eligible": True})

    def test_boolean_numeric_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({**GOOD, "years": True})

    def test_invalid_discount_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({**GOOD, "discount": 0.01})

    def test_command_line_success(self):
        p = subprocess.run([sys.executable, "-m", "buffettvalue", "--input",
                            str(ROOT / "examples/dcf-example.json")],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["mode"], "RESEARCH_ONLY")

    def test_command_line_failure(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bad.json"
            path.write_text('{"years": 10}')
            p = subprocess.run([sys.executable, "-m", "buffettvalue", "--input", str(path)],
                               cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertIn("DCF_ERROR", p.stderr)
