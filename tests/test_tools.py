import unittest
import importlib.util
from pathlib import Path
module_path = Path(__file__).resolve().parents[1] / "campuspulse_agent" / "tools.py"
spec = importlib.util.spec_from_file_location("campuspulse_tools", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
get_deadlines = module.get_deadlines
get_weekly_schedule = module.get_weekly_schedule

class TestTools(unittest.TestCase):
    def test_deadlines(self):
        result = get_deadlines("2026-10-19", 7)
        self.assertEqual(len(result["assignments"]), 3)
        self.assertEqual(result["assignments"][0]["due_date"], "2026-10-20")
    def test_completed_excluded(self):
        result = get_deadlines("2026-10-01", 30)
        self.assertTrue(all(a["status"] == "pending" for a in result["assignments"]))
    def test_invalid_input(self):
        self.assertIn("error", get_deadlines("bad-date"))
    def test_schedule(self):
        self.assertEqual(len(get_weekly_schedule()["classes"]), 3)

if __name__ == "__main__":
    unittest.main()
