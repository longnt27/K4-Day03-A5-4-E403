import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import run_react_agent
from providers import MockProvider


class ReactAgentToolSelectionTests(unittest.TestCase):
    def test_general_advice_query_does_not_call_tool(self):
        result = run_react_agent(
            "Sinh viên nên cân nhắc những yếu tố nào khi lựa chọn môn học cho học kỳ tới?",
            MockProvider(),
        )
        self.assertEqual(result["steps"], [])


if __name__ == "__main__":
    unittest.main()
