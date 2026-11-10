import unittest

from yaptex.directives import PragmaDirective


class TestEngine(unittest.TestCase):
    def test_pragma_args(self):
        pd = PragmaDirective()
        texts = [
            "(2)",
            "(2, 3)",
            "(2, depth=1)",
            "(start=2, depth=1)",
            "(push)",
            "(push, 2)",
            "(push, 2, 3)",
            "(push, start=2, end=3)",
            "(push, 2, depth=1)",
            "(push, start=2, depth=1)"
        ]
        expected = [
            ([],       {'start': '2',  'end': None, 'depth': None}),
            ([],       {'start': '2',  'end': '3',  'depth': None}),
            ([],       {'start': '2',  'end': None, 'depth': '1'}),
            ([],       {'start': '2',  'end': None, 'depth': '1'}),
            (['push'], {'start': None, 'end': None, 'depth': None}),
            (['push'], {'start': '2',  'end': None, 'depth': None}),
            (['push'], {'start': '2',  'end': '3',  'depth': None}),
            (['push'], {'start': '2',  'end': '3',  'depth': None}),
            (['push'], {'start': '2',  'end': None, 'depth': '1'}),
            (['push'], {'start': '2',  'end': None, 'depth': '1'}),
        ]

        for i, (t, exp) in enumerate(zip(texts, expected)):
            r = pd._parse_bracketed_args([i.strip() for i in t.strip("()").split(",")],
                                     ["push", "pop", "reset"],
                                     ["start", "end"],
                                     ["depth"])
            assert r == exp, f"index {i}"
