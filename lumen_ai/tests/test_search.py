

import unittest

from astra_ai import load_tool

from .test_tools import ToolTesterMixin


class DuckDuckGoSearchToolTester(unittest.TestCase, ToolTesterMixin):
    def setUp(self):
        self.tool = load_tool("web_search")
        self.tool.setup()

    def test_exact_match_arg(self):
        result = self.tool("Agents")
        assert isinstance(result, str)
