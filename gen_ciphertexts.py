#!/usr/bin/env python3
import os, subprocess

SIZES = {"1kb": 1024, "10kb": 10240, "100kb": 102400}
BASE = "dataset"
PLAIN = f"{BASE}/plaintext"
ENC   = f"{BASE}/encrypted"
KEYS  = f"{BASE}/keys"

os.makedirs(PLAIN, exist_ok=True)
os.makedirs(ENC, exist_ok=True)

# 1) Plaintexts
for name, size in SIZES.items():
    path = f"{PLAIN}/plain_{name}.txt"
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(os.urandom(size))
    print(f"[+] Plaintext ready: {path}")

# 2) Symmetric
SYMMETRIC = {
    "DES":      ("des-ecb",      8),
    "3DES":     ("des3",        24),
    "AES128":   ("aes-128-cbc", 16),
    "AES256":   ("aes-256-cbc", 32),
    "ChaCha20": ("chacha20",    32),
}

for algo_name, (cipher, keylen) in SYMMETRIC.items():
    key = os.urandom(keylen).hex()
    iv  = os.urandom(8).hex() if algo_name != "ChaCha20" else os.urandom(16).hex()
    for size_name in SIZES:
        plain = f"{PLAIN}/plain_{size_name}.txt"
        out   = f"{ENC}/{algo_name}_{size_name}.bin"
        if os.path.exists(out):
            print(f"[~] Skip existing: {out}")
            continue
        cmd = ["openssl","enc",f"-{cipher}","-K",key,"-iv",iv,
               "-in",plain,"-out",out,"-nosalt"]
        res = subprocess.run(cmd, capture_output=True)
        print(f"[{'✓' if res.returncode==0 else '✗'}] {algo_name} {size_name} → {out}")

# 3) RSA Hybrid (unchanged)
def rsa_hybrid(label, pubkey_path, size_name):
    aes_key = os.urandom(32)
    iv = os.urandom(16).hex()
    plain = f"{PLAIN}/plain_{size_name}.txt"
    cipher_out = f"{ENC}/{label}_AES256_{size_name}.bin"
    key_out    = f"{ENC}/{label}_KEY_{size_name}.bin"
    if os.path.exists(key_out):
        print(f"[~] Skip existing: {key_out}")
        return
    subprocess.run(["openssl","enc","-aes-256-cbc",
                    "-K",aes_key.hex(),"-iv",iv,
                    "-in",plain,"-out",cipher_out,"-nosalt"],
                   capture_output=True)
    res = subprocess.run(["openssl","pkeyutl","-encrypt",
                          "-inkey",pubkey_path,"-pubin",
                          "-in","-","-out",key_out],
                         input=aes_key, capture_output=True)
    print(f"[{'✓' if res.returncode==0 else '✗'}] {label} KEY {size_name} → {key_out}")

# 4) ECC Hybrid — ECDH-based (الحل الصح)
def ecc_hybrid(size_name):
    label = "ECC256"
    plain      = f"{PLAIN}/plain_{size_name}.txt"
    cipher_out = f"{ENC}/{label}_AES256_{size_name}.bin"
    key_out    = f"{ENC}/{label}_KEY_{size_name}.bin"
    eph_priv   = f"{KEYS}/eph_{size_name}.pem"
    eph_pub    = f"{KEYS}/eph_{size_name}_pub.pem"
    shared     = f"{KEYS}/eph_shared_{size_name}.bin"

    if os.path.exists(key_out):
        print(f"[~] Skip existing: {key_out}")
        return

    # Generate ephemeral EC keypair (same curve)
    subprocess.run(["openssl","ecparam","-name","prime256v1",
                    "-genkey","-noout","-out",eph_priv], capture_output=True)
    subprocess.run(["openssl","pkey","-in",eph_priv,
                    "-pubout","-out",eph_pub], capture_output=True)

    # ECDH: derive shared secret between ephemeral priv + recipient pub
    res_dh = subprocess.run([
        "openssl","pkeyutl","-derive",
        "-inkey", eph_priv,
        "-peerkey", f"{KEYS}/ecc_256_pub.pem",
        "-out", shared
    ], capture_output=True)

    if res_dh.returncode != 0:
        print(f"[✗] ECC ECDH derive failed ({size_name}): {res_dh.stderr.decode()}")
        return

    # Use shared secret as AES key (SHA-256 of it)
    with open(shared, "rb") as f:
        raw = f.read()
    import hashlib
    aes_key = hashlib.sha256(raw).hexdigest()
    iv = os.urandom(16).hex()

    # Save wrapped key = ephemeral public key (receiver uses ECDH to recover it)
    subprocess.run(["cp", eph_pub, key_out])

    # Encrypt with derived AES key
    res_enc = subprocess.run([
        "openssl","enc","-aes-256-cbc",
        "-K", aes_key, "-iv", iv,
        "-in", plain, "-out", cipher_out, "-nosalt"
    ], capture_output=True)

    print(f"[{'✓' if res_enc.returncode==0 else '✗'}] ECC256 ECDH hybrid {size_name} → {cipher_out}")
    print(f"[{'✓' if res_enc.returncode==0 else '✗'}] ECC256 KEY (eph_pub) {size_name} → {key_out}")

    # Cleanup temp files
    for f in [eph_priv, shared]:
        os.remove(f) if os.path.exists(f) else None

# Run RSA
for size in SIZES:
    rsa_hybrid("RSA2048", f"{KEYS}/rsa_2048_pub.pem", size)
    rsa_hybrid("RSA4096", f"{KEYS}/rsa_4096_pub.pem", size)

# Run ECC
for size in SIZES:
    ecc_hybrid(size)

print("\n[+] All done:", ENC)
