#!/usr/bin/env python3
import oqs, os

SIZES = {"1kb": 1024, "10kb": 10240, "100kb": 102400}
PLAIN = "dataset/plaintext"
ENC   = "dataset/encrypted"
os.makedirs(ENC, exist_ok=True)

PQC_KEMS = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]

for kem_name in PQC_KEMS:
    kem = oqs.KeyEncapsulation(kem_name)
    public_key = kem.generate_keypair()

    for size_name, size in SIZES.items():
        plain_path = f"{PLAIN}/plain_{size_name}.txt"
        out_path   = f"{ENC}/{kem_name.replace('-','_')}_{size_name}.bin"

        if os.path.exists(out_path):
            print(f"[~] Skip: {out_path}")
            continue

        # Encapsulate — generates shared secret + ciphertext
        ciphertext, shared_secret = kem.encap_secret(public_key)

        # Use shared secret as AES-256 key to encrypt plaintext
        import subprocess, hashlib
        aes_key = hashlib.sha256(shared_secret).hexdigest()
        iv      = os.urandom(16).hex()

        res = subprocess.run([
            "openssl", "enc", "-aes-256-cbc",
            "-K", aes_key, "-iv", iv,
            "-in", plain_path, "-out", out_path, "-nosalt"
        ], capture_output=True)

        # Save KEM ciphertext (the "key wrapper")
        key_path = f"{ENC}/{kem_name.replace('-','_')}_KEY_{size_name}.bin"
        with open(key_path, "wb") as f:
            f.write(ciphertext)

        status = "✓" if res.returncode == 0 else "✗"
        print(f"[{status}] {kem_name} {size_name} → {out_path}")
        print(f"[{status}] {kem_name} KEY {size_name} → {key_path}")

print("\n[+] PQC Layer complete")
