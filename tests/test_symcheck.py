import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import symcheck


class T(unittest.TestCase):
    def run_pair(self, a, b, name="p.txt", allow=()):
        with tempfile.TemporaryDirectory() as d:
            pa, pb = Path(d, "a_" + name), Path(d, "b_" + name)
            pa.write_text(a, encoding="utf-8"); pb.write_text(b, encoding="utf-8")
            argv = [str(pa), str(pb)]
            for x in allow:
                argv += ["--allow", x]
            return symcheck.main(argv)

    def test_identical(self):
        self.assertEqual(self.run_pair("x\ny\n", "x\ny\n"), 0)

    def test_unexpected(self):
        self.assertEqual(self.run_pair("x\ny\n", "x\nz\n"), 1)

    def test_allow_regex(self):
        self.assertEqual(self.run_pair("model: a\nt\n", "model: b\nt\n", allow=[r"^model:"]), 0)

    def test_marker_block(self):
        a = "t\n# ARM-SPECIFIC-START\nhint list\n# ARM-SPECIFIC-END\nu\n"
        b = "t\nu\n"
        self.assertEqual(self.run_pair(a, b), 0)

    def test_marker_does_not_hide_outside(self):
        a = "t\n# ARM-SPECIFIC-START\nh\n# ARM-SPECIFIC-END\nu\n"
        b = "t\nCHANGED\n"
        self.assertEqual(self.run_pair(a, b), 1)

    def test_json_order_insensitive(self):
        a = json.dumps({"a": 1, "b": {"c": 2}}); b = json.dumps({"b": {"c": 2}, "a": 1})
        self.assertEqual(self.run_pair(a, b, name="c.json"), 0)

    def test_json_difference(self):
        a = json.dumps({"a": 1}); b = json.dumps({"a": 2})
        self.assertEqual(self.run_pair(a, b, name="c.json"), 1)

    def test_directories(self):
        with tempfile.TemporaryDirectory() as d:
            for arm, extra in (("A", ""), ("B", "extra")):
                Path(d, arm).mkdir(); Path(d, arm, "p.txt").write_text("same")
                if extra: Path(d, arm, extra).write_text("x")
            self.assertEqual(symcheck.main([f"{d}/A", f"{d}/B"]), 1)

    def test_missing_input(self):
        self.assertEqual(symcheck.main(["/nonexistent/a", "/nonexistent/b"]), 2)


if __name__ == "__main__":
    unittest.main()
