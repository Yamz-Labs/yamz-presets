#!/usr/bin/env python3
"""Check a steering preset on CPU: schema, direction tensor, sha256.

usage: python3 verify.py glm-5.3-flash [more preset dirs]
Needs only the Python standard library.
"""
import hashlib, json, math, os, struct, sys


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_r(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        head = json.loads(f.read(n))
        base = 8 + n
        if "r" not in head:
            raise ValueError("tensor 'r' missing")
        t = head["r"]
        if t["dtype"] != "F32" or len(t["shape"]) != 1:
            raise ValueError(f"'r' must be 1-D F32, got {t['dtype']} {t['shape']}")
        a, b = t["data_offsets"]
        f.seek(base + a)
        raw = f.read(b - a)
    if len(raw) != 4 * t["shape"][0]:
        raise ValueError("'r' byte length does not match its shape")
    return struct.unpack(f"<{t['shape'][0]}f", raw)


def check(d):
    errs = []
    sums = os.path.join(d, "SHA256SUMS")
    if not os.path.isfile(sums):
        return [f"{d}: no SHA256SUMS (a preset without a hash file is not valid)"]
    listed = {}
    for line in open(sums):
        if line.strip():
            h, name = line.split(None, 1)
            listed[name.strip().lstrip("*")] = h
    for need in ("edit_spec.json", "edit_spec.safetensors"):
        if need not in listed:
            errs.append(f"{need} not listed in SHA256SUMS")
        elif not os.path.isfile(os.path.join(d, need)):
            errs.append(f"{need} missing")
        elif sha256(os.path.join(d, need)) != listed[need]:
            errs.append(f"{need}: sha256 mismatch")
    if errs:
        return errs
    spec = json.load(open(os.path.join(d, "edit_spec.json")))
    hidden, n = spec.get("hidden"), spec.get("n_layers")
    if not (isinstance(hidden, int) and hidden > 0 and isinstance(n, int) and n > 0):
        return ["hidden / n_layers must be positive integers"]
    for k in ("attn_w", "mlp_w"):
        w = spec.get(k)
        if not isinstance(w, list) or len(w) != n:
            errs.append(f"{k}: need a list of n_layers={n} numbers")
        elif not all(isinstance(x, (int, float)) and math.isfinite(x) for x in w):
            errs.append(f"{k}: non-finite or non-numeric entry")
        elif max(abs(x) for x in w) > 4.0:
            errs.append(f"{k}: weight above 4.0, refusing to call this a preset")
        elif not any(abs(x) > 1e-9 for x in w):
            errs.append(f"{k}: all zero")
    try:
        r = read_r(os.path.join(d, "edit_spec.safetensors"))
    except Exception as e:
        return errs + [f"direction file: {e}"]
    if len(r) != hidden:
        errs.append(f"r has {len(r)} values, hidden is {hidden}")
    norm = math.sqrt(sum(x * x for x in r))
    if not (math.isfinite(norm) and norm > 0):
        errs.append("r has zero or non-finite norm")
    elif abs(norm - 1.0) > 1e-3:
        errs.append(f"r is not a unit vector (norm {norm:.6f}); the engine renormalises, but a preset should ship it unit")
    return errs


if __name__ == "__main__":
    dirs = sys.argv[1:]
    if not dirs:
        sys.exit(__doc__)
    bad = 0
    for d in dirs:
        e = check(d)
        print(("OK   " if not e else "FAIL ") + d)
        for m in e:
            print("     - " + m)
        bad += bool(e)
    sys.exit(1 if bad else 0)
