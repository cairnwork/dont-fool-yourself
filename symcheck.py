#!/usr/bin/env python3
"""symcheck: zero-model symmetry check for two arms of an A/B.

Compare two prompt/config files (or two directories of them) and list every
difference that is NOT registered as intended. Exit code 0 = only registered
differences, 1 = unexpected differences, 2 = usage/input error.

A difference is registered (allowed) when either:
  * the differing line sits between marker lines containing
    ARM-SPECIFIC-START and ARM-SPECIFIC-END in the file the line lives in.
    A replaced block must therefore be marked in BOTH files; a block that
    exists in only one file needs the marker only there. An unpaired,
    nested or stray marker is an error (exit 2), never a silent allow-all.
  * a differing line matches an --allow REGEX (an invalid regex is exit 2).

JSON files (*.json) are flattened to "path.to.key = value" lines first, so
key order and whitespace do not matter. JSON cannot carry markers: use
--allow for them. In directory mode, hidden files and directories (.git,
.DS_Store) are ignored and files that are not UTF-8 are skipped and listed.
Python 3.10+, standard library only.
"""
import argparse
import difflib
import json
import re
import sys
from pathlib import Path

START, END = "ARM-SPECIFIC-START", "ARM-SPECIFIC-END"


def _flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for k in sorted(obj):
            yield from _flatten(obj[k], f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _flatten(v, f"{prefix}[{i}]")
    else:
        yield f"{prefix} = {json.dumps(obj, ensure_ascii=False)}"


def load_lines(path):
    text = Path(path).read_text(encoding="utf-8")
    if str(path).endswith(".json"):
        return list(_flatten(json.loads(text)))
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


def _pairs(a, b):
    pa, pb = Path(a), Path(b)
    if pa.is_dir() != pb.is_dir():
        raise ValueError("both inputs must be files or both directories")
    if not pa.is_dir():
        return [(str(pa), pa, pb)], []
    def files(root):
        out = {}
        for p in root.rglob("*"):
            rel = p.relative_to(root)
            if p.is_file() and not any(part.startswith(".") for part in rel.parts):
                out[rel.as_posix()] = p
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
    args = ap.parse_args(argv)
    try:
        for p in args.allow:
            re.compile(p)
        pairs, missing = _pairs(args.a, args.b)
        total = 0
        is_dir = Path(args.a).is_dir()
        for name, pa, pb in pairs:
            try:
                la, lb = load_lines(pa), load_lines(pb)
            except UnicodeDecodeError:
                if not is_dir:
                    raise
                print(f"SKIPPED {name}: not UTF-8")
                continue
            bad = compare(la, lb, args.allow)
            for kind, la, lb in bad:
                print(f"UNEXPECTED {name}: {kind}: {la if la is not None else lb}")
            total += len(bad)
        for m in missing:
            print(f"UNEXPECTED file: {m}")
            total += 1
    except (OSError, ValueError, UnicodeDecodeError, re.error) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"symcheck: {total} unexpected difference(s) in {len(pairs)} file pair(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
