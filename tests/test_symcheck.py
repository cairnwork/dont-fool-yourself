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

    def dirs(self, d, files_a, files_b):
        for arm, files in (("A", files_a), ("B", files_b)):
            Path(d, arm).mkdir(exist_ok=True)
            for name, data in files.items():
                p = Path(d, arm, name); p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data if isinstance(data, bytes) else data.encode())
        return [f"{d}/A", f"{d}/B"]

    # Issue #1 case 1: hidden files and dirs are compared, only .git skipped
    def test_dot_claude_difference_is_caught(self):
        with tempfile.TemporaryDirectory() as d:
            args = self.dirs(d, {"p.txt": "s", ".claude/settings.json": '{"x": 1}'},
                             {"p.txt": "s", ".claude/settings.json": '{"x": 2}'})
            self.assertEqual(symcheck.main(args), 1)

    def test_dotfile_difference_is_caught_and_ignore_list_works(self):
        with tempfile.TemporaryDirectory() as d:
            args = self.dirs(d, {"p.txt": "s", ".env": "a"}, {"p.txt": "s", ".env": "b"})
            self.assertEqual(symcheck.main(args), 1)
            self.assertEqual(symcheck.main(args + ["--ignore", ".env"]), 0)

    def test_git_dir_skipped_by_default(self):
        with tempfile.TemporaryDirectory() as d:
            args = self.dirs(d, {"p.txt": "s", ".git/x": "a"}, {"p.txt": "s", ".git/x": "b"})
            self.assertEqual(symcheck.main(args), 0)

    # Issue #1 case 2: JSON flattening must not make different structures equal
    def test_json_empty_object_not_equal_to_missing(self):
        self.assertEqual(self.run_pair('{"a": {}}', "{}", name="c.json"), 1)

    def test_json_empty_array_not_equal_to_empty_object(self):
        self.assertEqual(self.run_pair('{"a": []}', '{"a": {}}', name="c.json"), 1)

    def test_json_dotted_key_not_equal_to_nested(self):
        self.assertEqual(self.run_pair('{"a.b": 1}', '{"a": {"b": 1}}', name="c.json"), 1)

    def test_json_index_like_key_not_equal_to_list(self):
        self.assertEqual(self.run_pair('{"a": {"0": 1}}', '{"a": [1]}', name="c.json"), 1)

    def test_json_slash_key_not_equal_to_nested(self):
        self.assertEqual(self.run_pair('{"a/b": 1}', '{"a": {"b": 1}}', name="c.json"), 1)

    def test_json_duplicate_keys_incomplete(self):
        self.assertEqual(self.run_pair('{"a": 1, "a": 2}', '{"a": 2}', name="c.json"), 3)

    def test_json_invalid_incomplete(self):
        self.assertEqual(self.run_pair("{oops", "{oops", name="c.json"), 3)

    # Issue #1 case 3: nothing skipped or empty may exit 0
    def test_non_utf8_in_directory_is_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            args = self.dirs(d, {"p.txt": "s", "img.bin": b"\xff\xfeA"},
                             {"p.txt": "s", "img.bin": b"\xff\xfeB"})
            self.assertEqual(symcheck.main(args), 3)

    def test_non_utf8_single_file_is_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            pa, pb = Path(d, "a"), Path(d, "b")
            pa.write_bytes(b"\xff"); pb.write_bytes(b"\xff")
            self.assertEqual(symcheck.main([str(pa), str(pb)]), 3)

    def test_zero_files_compared_is_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            args = self.dirs(d, {}, {})
            self.assertEqual(symcheck.main(args), 3)
            args = self.dirs(d, {".git/x": "a"}, {".git/x": "a"})
            self.assertEqual(symcheck.main(args), 3)

    def test_unexpected_diff_wins_over_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            args = self.dirs(d, {"p.txt": "a", "i.bin": b"\xff"}, {"p.txt": "b", "i.bin": b"\xff"})
            self.assertEqual(symcheck.main(args), 1)

    def test_missing_input(self):
        self.assertEqual(symcheck.main(["/nonexistent/a", "/nonexistent/b"]), 2)


if __name__ == "__main__":
    unittest.main()
