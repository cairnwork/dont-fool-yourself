#!/usr/bin/env python3
"""symcheck: zero-model symmetry check for two arms of an A/B.

Compare two prompt/config files (or two directories of them) and list every
difference that is NOT registered as intended.

Exit codes:
  0  every compared file pair matched, apart from registered differences
  1  unexpected differences (listed)
  2  usage or input error (bad regex, unpaired marker, missing path ...)
  3  INCOMPLETE: something could not be compared (a skipped or undecodable
     file, an unparsable or ambiguous JSON file, or zero file pairs). Listed.
     Never treat 3 as success.
A 0 means "no unexpected difference within the checked scope", NOT "the arms
are proven symmetric": anything outside the compared files is not looked at.

A difference is registered (allowed) when either:
  * the differing line sits between marker lines containing
    ARM-SPECIFIC-START and ARM-SPECIFIC-END in the file the line lives in.
    A replaced block must therefore be marked in BOTH files; a block that
    exists in only one file needs the marker only there. An unpaired,
    nested or stray marker is an error (exit 2), never a silent allow-all.
  * a differing line matches an --allow REGEX (an invalid regex is exit 2).

Directory mode compares files with the same relative path. Only ".git"
directories and names given with --ignore (fnmatch against any path part or
the relative path, repeatable) are skipped by default; every other dotfile
and directory (for example .claude/) is compared. A file present on one side
only is an unexpected difference.

JSON files (*.json) are flattened to JSON-pointer lines ("/a/b = 1"), with a
line for every object and array ("/a : object", "/a : array") so empty
containers and object-versus-array differences are kept. Duplicate keys make
the file ambiguous and are reported as INCOMPLETE. JSON cannot carry
markers: use --allow. Python 3.10+, standard library only.
"""
import argparse
import difflib
import fnmatch
import json
import re
import sys
from pathlib import Path

START, END = "ARM-SPECIFIC-START", "ARM-SPECIFIC-END"


class Incomplete(Exception):
    """A file could not be compared safely."""


def _esc(k):
    return str(k).replace("~", "~0").replace("/", "~1")


def _flatten(obj, ptr=""):
    if isinstance(obj, dict):
        yield f"{ptr} : object"
        for k in sorted(obj):
            yield from _flatten(obj[k], f"{ptr}/{_esc(k)}")
    elif isinstance(obj, list):
        yield f"{ptr} : array"
        for i, v in enumerate(obj):
            yield from _flatten(v, f"{ptr}/{i}")
    else:
        yield f"{ptr} = {json.dumps(obj, ensure_ascii=False)}"


def _no_dup_keys(pairs):
    keys = [k for k, _ in pairs]
    dup = {k for k in keys if keys.count(k) > 1}
    if dup:
        raise Incomplete(f"duplicate JSON key(s) {sorted(dup)}: ambiguous")
    return dict(pairs)


def load_lines(path):
    try:
        text = Path(path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise Incomplete("not UTF-8, not compared")
    if str(path).endswith(".json"):
        try:
            return list(_flatten(json.loads(text, object_pairs_hook=_no_dup_keys)))
        except json.JSONDecodeError as e:
            raise Incomplete(f"invalid JSON ({e.msg}), not compared")
    return text.splitlines()


def _marked(lines):
    """Return the set of line indexes inside ARM-SPECIFIC blocks (markers included)."""
    inside, out = False, set()
    for i, ln in enumerate(lines):
        if START in ln:
            if inside:
                raise ValueError(f"nested {START} at line {i + 1}")
            inside = True
        elif END in ln and not inside:
            raise ValueError(f"{END} without {START} at line {i + 1}")
        if inside:
            out.add(i)
        if END in ln and inside:
            inside = False
    if inside:
        raise ValueError(f"{START} without {END}")
    return out


def compare(a_lines, b_lines, allow=()):
    """Return a list of unexpected differences as (kind, a_line, b_line)."""
    pats = [re.compile(p) for p in allow]
    ma, mb = _marked(a_lines), _marked(b_lines)
    ok = lambda ln: any(p.search(ln) for p in pats)
    bad = []
    sm = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        a_chunk = [(i, a_lines[i]) for i in range(i1, i2)]
        b_chunk = [(j, b_lines[j]) for j in range(j1, j2)]
        for i, ln in a_chunk:
            if i not in ma and not ok(ln):
                bad.append(("only-in-A" if tag == "delete" else "changed-A", ln, None))
        for j, ln in b_chunk:
            if j not in mb and not ok(ln):
                bad.append(("only-in-B" if tag == "insert" else "changed-B", None, ln))
    return bad


def _skipped(rel, ignore):
    parts = rel.split("/")
    if ".git" in parts:
        return True
    return any(fnmatch.fnmatch(rel, g) or any(fnmatch.fnmatch(p, g) for p in parts)
               for g in ignore)


def _pairs(a, b, ignore=()):
    pa, pb = Path(a), Path(b)
    if not pa.exists() or not pb.exists():
        raise ValueError("input path does not exist")
    if pa.is_dir() != pb.is_dir():
        raise ValueError("both inputs must be files or both directories")
    if not pa.is_dir():
        return [(str(pa), pa, pb)], []

    def files(root):
        out = {}
        for p in root.rglob("*"):
            rel = p.relative_to(root).as_posix()
            if p.is_file() and not _skipped(rel, ignore):
                out[rel] = p
        return out

    fa, fb = files(pa), files(pb)
    pairs = [(k, fa[k], fb[k]) for k in sorted(fa.keys() & fb.keys())]
    missing = [f"{k} (only in A)" for k in sorted(fa.keys() - fb.keys())]
    missing += [f"{k} (only in B)" for k in sorted(fb.keys() - fa.keys())]
    return pairs, missing


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--allow", action="append", default=[], metavar="REGEX",
                    help="registered difference: a differing line matching REGEX is allowed (repeatable)")
    ap.add_argument("--ignore", action="append", default=[], metavar="GLOB",
                    help="skip paths matching GLOB in directory mode (repeatable); only .git is skipped by default")
    args = ap.parse_args(argv)
    incomplete = []
    try:
        for p in args.allow:
            re.compile(p)
        pairs, missing = _pairs(args.a, args.b, args.ignore)
        total = compared = 0
        for name, pa, pb in pairs:
            try:
                la, lb = load_lines(pa), load_lines(pb)
            except Incomplete as e:
                incomplete.append(f"{name}: {e}")
                continue
            compared += 1
            bad = compare(la, lb, args.allow)
            for kind, x, y in bad:
                print(f"UNEXPECTED {name}: {kind}: {x if x is not None else y}")
            total += len(bad)
        for m in missing:
            print(f"UNEXPECTED file: {m}")
            total += 1
    except (OSError, ValueError, re.error) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if compared == 0 and not incomplete:
        incomplete.append("no file pairs were compared")
    for i in incomplete:
        print(f"INCOMPLETE {i}")
    print(f"symcheck: {total} unexpected difference(s), {compared} file pair(s) compared, "
          f"{len(incomplete)} incomplete")
    if total:
        return 1
    return 3 if incomplete else 0


if __name__ == "__main__":
    sys.exit(main())
