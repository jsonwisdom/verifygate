"""FC-2 seed: strict Python byte-parser policy tests only. No claim about JS/Go."""
import json
import unittest

MAX_BYTES = 4096
MAX_DEPTH = 32

def strict_parse(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ValueError("invalid input size/type")
    text = raw.decode("utf-8", "strict")
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError("duplicate key")
            out[k] = v
        return out
    def bad_constant(value):
        raise ValueError("non-finite number")
    value = json.loads(text, object_pairs_hook=pairs, parse_constant=bad_constant)
    def visit(item, depth):
        if depth > MAX_DEPTH:
            raise ValueError("maximum nesting depth")
        if isinstance(item, str):
            if any(0xD800 <= ord(c) <= 0xDFFF for c in item):
                raise ValueError("lone surrogate")
        elif isinstance(item, list):
            for child in item:
                visit(child, depth + 1)
        elif isinstance(item, dict):
            for k, child in item.items():
                visit(k, depth + 1)
                visit(child, depth + 1)
    visit(value, 0)
    return value

class FC2SeedTests(unittest.TestCase):
    def test_accept_valid_utf8_and_valid_surrogate_pair(self):
        for raw in [b'{"ok":true}', '{"v":"é"}'.encode("utf-8"), b'{"v":"\\ud83d\\ude00"}']:
            self.assertIsNotNone(strict_parse(raw))

    def test_reject_bad_utf8(self):
        for raw in [b'\xff', b'{"x":"\xc0\xaf"}', b'{"x":"\xed\xa0\x80"}', b'{"x":"\xf0\x9f\x98"}']:
            with self.subTest(raw=raw), self.assertRaises((UnicodeDecodeError, ValueError)):
                strict_parse(raw)

    def test_reject_parser_ambiguity(self):
        for raw in [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1,}', b'{"x":', b'{}{}']:
            with self.subTest(raw=raw), self.assertRaises((ValueError, json.JSONDecodeError)):
                strict_parse(raw)

    def test_reject_lone_surrogates(self):
        for raw in [b'{"x":"\\ud800"}', b'{"x":"\\udc00"}', b'{"\\ud800":1}']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                strict_parse(raw)

    def test_resource_limits(self):
        with self.assertRaises(ValueError):
            strict_parse(b" " * (MAX_BYTES + 1))
        with self.assertRaises(ValueError):
            strict_parse(b"[" * (MAX_DEPTH + 1) + b"0" + b"]" * (MAX_DEPTH + 1))

if __name__ == "__main__":
    unittest.main(verbosity=2)
