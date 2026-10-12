import hashlib, json, re
from pathlib import Path

LANGS = ["en", "fr", "es"]
TOKEN_RE = re.compile(r"\w+|[^\w\s]+", re.UNICODE)

def byte_encoder():
    base = list(range(ord("!"), ord("~") + 1)) + list(range(0xA1, 0xAD)) + list(range(0xAE, 0x100))
    values = base[:]; extra = 0
    for value in range(256):
        if value not in base:
            base.append(value); values.append(256 + extra); extra += 1
    return dict(zip(base, map(chr, values)))

ENC = byte_encoder()

def pretokenize(text):
    # tokenizers.Whitespace splits Unicode words and punctuation groups; the
    # following ByteLevel(use_regex=False) defaults to add_prefix_space=True.
    return ["".join(ENC[b] for b in (" " + match.group(0)).encode("utf-8")) for match in TOKEN_RE.finditer(text)]

def replay(text, merges):
    output = []
    for word in pretokenize(text):
        pieces = list(word)
        for left, right in merges:
            new = []; index = 0
            while index < len(pieces):
                if index + 1 < len(pieces) and pieces[index] == left and pieces[index + 1] == right:
                    new.append(left + right); index += 2
                else:
                    new.append(pieces[index]); index += 1
            pieces = new
        output.extend(pieces)
    return output

root = Path(__file__).resolve().parents[2]
prior = root / "wake16b"
rows = json.loads((prior / "inputs/dev.json").read_text())
stored = json.loads((prior / "output/evaluation.json").read_text())
checks = 0; mismatches = []
for name in ["classical", "base", "window", "hybrid", "ratio"]:
    code_path = Path("inputs") / f"{name}.codes"
    merges = [tuple(line.split()) for line in code_path.read_text().splitlines() if line and not line.startswith("#")]
    expected = stored["arms"][name]["paired_costs"]
    for row_index, row in enumerate(rows):
        actual = [len(replay(row[lang], merges)) for lang in LANGS]
        checks += 3
        if actual != expected[row_index]:
            mismatches.append({"arm": name, "row": row_index, "actual": actual, "expected": expected[row_index]})
            if len(mismatches) >= 20: break
    if mismatches: break
result = {
    "status": "PASS" if not mismatches else "FAIL",
    "integer_cost_checks": checks,
    "rows": len(rows), "arms": 5, "mismatches": mismatches,
    "scope": "Independent pure-Python reconstruction of tokenizers Whitespace + ByteLevel(use_regex=False) and sequential BPE replay, compared to all persisted wake16 TICO integer costs.",
    "code_hashes": {name: hashlib.sha256((Path('inputs')/f'{name}.codes').read_bytes()).hexdigest() for name in ["classical", "base", "window", "hybrid", "ratio"]}
}
Path("output/pure_replay_verification.json").write_text(json.dumps(result, indent=2)+"\n")
print(json.dumps(result, indent=2))
assert not mismatches
