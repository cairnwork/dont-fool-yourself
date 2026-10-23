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

    def test_start_without_end_is_error(self):
        a = "t\n# ARM-SPECIFIC-START\nhint\nsecret hint: answer is 42\n"
        b = "t\nhint\n"
        self.assertEqual(self.run_pair(a, b), 2)

    def test_end_without_start_and_nested(self):
        self.assertEqual(self.run_pair("t\n# ARM-SPECIFIC-END\n", "t\n"), 2)
        self.assertEqual(self.run_pair("# ARM-SPECIFIC-START\n# ARM-SPECIFIC-START\n# ARM-SPECIFIC-END\n", "x\n"), 2)

    def test_hidden_line_after_closed_block_caught(self):
        a = "t\n# ARM-SPECIFIC-START\nh\n# ARM-SPECIFIC-END\nsecret hint: 42\n"
        self.assertEqual(self.run_pair(a, "t\n"), 1)

    def test_replaced_block_needs_both_marks(self):
        a = "# ARM-SPECIFIC-START\nhint A\n# ARM-SPECIFIC-END\n"
        b = "hint B\n"
        self.assertEqual(self.run_pair(a, b), 1)
        b2 = "# ARM-SPECIFIC-START\nhint B\n# ARM-SPECIFIC-END\n"
        self.assertEqual(self.run_pair(a, b2), 0)

    def test_bad_regex(self):
        self.assertEqual(self.run_pair("a\n", "a\n", allow=["("]), 2)

    def test_dir_ignores_hidden_and_skips_binary(self):
        with tempfile.TemporaryDirectory() as d:
            for arm in ("A", "B"):
                Path(d, arm, ".git").mkdir(parents=True)
                Path(d, arm, "p.txt").write_text("same")
                Path(d, arm, ".DS_Store").write_bytes(bytes([arm == "A"]))
                Path(d, arm, ".git", "x").write_text(arm)
                Path(d, arm, "img.bin").write_bytes(b"\xff\xfe" + arm.encode())
            self.assertEqual(symcheck.main([f"{d}/A", f"{d}/B"]), 0)

    def test_missing_input(self):
        self.assertEqual(symcheck.main(["/nonexistent/a", "/nonexistent/b"]), 2)


if __name__ == "__main__":
    unittest.main()
