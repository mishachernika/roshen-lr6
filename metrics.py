"""Підрахунок метрик Холстеда та Спен для файлу roshen_shop.py (ЛР №4).

Запуск:  python3 metrics.py [файл.py]
Правила підрахунку операторів і операндів описано в розділі 2.1 звіту.
"""
import io
import keyword
import math
import sys
import tokenize
from collections import Counter

PAIRS = {"(": ")", "[": "]", "{": "}"}
SKIP = (tokenize.NEWLINE, tokenize.NL, tokenize.INDENT, tokenize.DEDENT,
        tokenize.ENDMARKER, tokenize.COMMENT)


def read_tokens(src):
    return [t for t in tokenize.generate_tokens(io.StringIO(src).readline)
            if t.type not in SKIP]


def halstead(tokens):
    ops, operands = Counter(), Counter()
    i = 0
    while i < len(tokens):
        t, s = tokens[i], tokens[i].string
        nxt = tokens[i + 1].string if i + 1 < len(tokens) else ""
        if t.type == tokenize.NAME and keyword.iskeyword(s) and s not in ("None", "True", "False"):
            if s == "not" and nxt == "in":          # «not in» — один оператор
                ops["not in"] += 1
                i += 2
                continue
            ops[s] += 1
        elif t.type == tokenize.NAME:
            if nxt == "(":
                ops[s + "()"] += 1                  # ім'я функції + дужки — один оператор
            else:
                operands[s] += 1
        elif t.type in (tokenize.NUMBER, tokenize.STRING) or s in ("None", "True", "False"):
            operands[s] += 1
        elif t.type == tokenize.OP:
            if s in PAIRS:
                ops[s + PAIRS[s]] += 1
            elif s not in PAIRS.values():
                ops[s] += 1
        i += 1
    calls = sum(c for k, c in ops.items() if k.endswith("()") and len(k) > 2)
    ops["()"] -= calls                               # дужки викликів уже враховано в імені функції
    if ops["()"] == 0:
        del ops["()"]
    n1, n2, N1, N2 = len(ops), len(operands), sum(ops.values()), sum(operands.values())
    n, N = n1 + n2, N1 + N2
    V = N * math.log2(n)
    D = (n1 / 2) * (N2 / n2)
    return {"n1": n1, "n2": n2, "N1": N1, "N2": N2, "n": n, "N": N,
            "N_theory": n1 * math.log2(n1) + n2 * math.log2(n2),
            "V": V, "D": D, "L": 1 / D, "E": D * V, "T_sec": D * V / 18, "B": V / 3000}


def functions(lines):
    result, cur = {}, None
    for no, line in enumerate(lines, 1):
        if line.startswith("def "):
            cur = line[4:line.index("(")]
            result[cur] = [no, no]
        elif cur and line.startswith(" ") and line.strip():
            result[cur][1] = no
    return result


def spen(tokens, funcs):
    out = {}
    for name, (a, b) in funcs.items():
        c = Counter()
        for idx, t in enumerate(tokens):
            if a <= t.start[0] <= b and t.type == tokenize.NAME and not keyword.iskeyword(t.string):
                nxt = tokens[idx + 1].string if idx + 1 < len(tokens) else ""
                if nxt != "(":
                    c[t.string] += 1
        out[name] = c
    return out


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "roshen_shop.py"
    src = open(path, encoding="utf-8").read()
    toks = read_tokens(src)
    print("== Холстед ==")
    for k, v in halstead(toks).items():
        print(f"{k:9} = {v:.3f}" if isinstance(v, float) else f"{k:9} = {v}")
    funcs = functions(src.split("\n"))
    print("== Спен (sp = n - 1) ==")
    total = ids = 0
    for f, c in spen(toks, funcs).items():
        s = sum(v - 1 for v in c.values())
        total, ids = total + s, ids + len(c)
        print(f"{f}: {dict(c)} -> {s}")
    print(f"Σsp = {total}, ідентифікаторів = {ids}, середній = {total / ids:.2f}")
