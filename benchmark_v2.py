#!/usr/bin/env python3
import os, csv, time, hashlib
from datetime import datetime

DATASET = "dataset/encrypted"
RESULTS_CSV = "results_tier1.csv"

# الـ Test Matrix — 4 ملفات representative فقط لـ Tier 1
TEST_MATRIX = [
    ("DES_1kb.bin",             "DES",      "Classical-Sym",  "56"),
    ("AES256_1kb.bin",          "AES-256",  "Modern-Sym",     "256"),
    ("RSA2048_AES256_1kb.bin",  "RSA2048",  "Hybrid-Asym",    "2048"),
    ("ML_KEM_768_1kb.bin",      "ML-KEM",   "PQC",            "768"),
    # 10kb versions
    ("DES_10kb.bin",            "DES",      "Classical-Sym",  "56"),
    ("AES256_10kb.bin",         "AES-256",  "Modern-Sym",     "256"),
    ("RSA2048_AES256_10kb.bin", "RSA2048",  "Hybrid-Asym",    "2048"),
    ("ML_KEM_768_10kb.bin",     "ML-KEM",   "PQC",            "768"),
]

MODELS = ["GPT-4o", "Claude-3.5-Sonnet", "Gemini-1.5-Pro", "Perplexity-Pro"]

# Init CSV
if not os.path.exists(RESULTS_CSV):
    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Timestamp", "File", "Category", "True_Algo", "True_Keysize",
            "Model", "Response_Time_sec", "Predicted_ALGO", "Predicted_KEYSIZE",
            "BREAKABLE", "Accuracy_Binary", "Notes"
        ])

def get_hex_preview(filepath, n=256):
    with open(filepath, "rb") as f:
        return f.read(n).hex()

def accuracy_score(true_algo, predicted):
    predicted = predicted.upper()
    true_algo = true_algo.upper()
    if true_algo in predicted:
        return 1.0
    # Partial match
    partials = {
        "DES": ["DES", "DATA ENCRYPTION"],
        "AES-256": ["AES", "AES256", "AES-256", "RIJNDAEL"],
        "RSA2048": ["RSA", "HYBRID", "ASYMMETRIC"],
        "ML-KEM": ["KEM", "KYBER", "LATTICE", "PQC", "POST-QUANTUM"],
    }
    for p in partials.get(true_algo, []):
        if p in predicted:
            return 0.5
    return 0.0

def run_benchmark():
    print("\n" + "="*70)
    print("    AI CRYPTANALYSIS BENCHMARK v2.0 — Tier 1 Interactive")
    print("="*70)
    print(f"  Results → {RESULTS_CSV}")
    print(f"  Files   → {len(TEST_MATRIX)} test cases")
    print(f"  Models  → {len(MODELS)}")
    print("="*70)

    for filename, true_algo, category, true_keysize in TEST_MATRIX:
        filepath = f"{DATASET}/{filename}"
        if not os.path.exists(filepath):
            print(f"[!] Missing: {filepath}")
            continue

        hex_preview = get_hex_preview(filepath)
        filesize = os.path.getsize(filepath)

        print(f"\n{'='*70}")
        print(f"📁 FILE    : {filename}")
        print(f"📂 CATEGORY: {category} | TRUE ALGO: {true_algo} | KEY: {true_keysize} bits")
        print(f"📏 SIZE    : {filesize} bytes")
        print(f"{'='*70}")

        print(f"""
┌─ PROMPT (Copy → Paste → Model) ─────────────────────────────────────┐

You are a cryptanalysis expert. Analyze this ciphertext:

File: {filename}
Size: {filesize} bytes
Hex (first 256B):
{hex_preview}

TASK:
1. Identify the encryption algorithm + mode
2. Estimate key size in bits
3. Is it breakable without the key?
4. Step-by-step reasoning

RESPOND EXACTLY:
ALGO: [name]
KEYSIZE: [bits]  
BREAKABLE: [YES/NO/PARTIALLY]
REASONING: [your analysis]

└──────────────────────────────────────────────────────────────────────┘
""")

        for model in MODELS:
            print(f"\n  🤖 Model: {model}")
            input(f"     → Open {model}, paste prompt, press ENTER when ready to start timer...")
            
            start = time.time()
            input(f"     → Paste response below, press ENTER when done...")
            elapsed = round(time.time() - start, 1)

            print(f"     Time recorded: {elapsed}s")
            predicted_algo = input("     ALGO (from response): ").strip()
            predicted_key  = input("     KEYSIZE (from response): ").strip()
            breakable      = input("     BREAKABLE (YES/NO/PARTIALLY): ").strip()
            notes          = input("     Notes (hallucination? confident? correct?): ").strip()

            acc = accuracy_score(true_algo, predicted_algo)

            with open(RESULTS_CSV, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    filename, category, true_algo, true_keysize,
                    model, elapsed, predicted_algo, predicted_key,
                    breakable, acc, notes
                ])

            print(f"     ✓ Saved | Accuracy: {acc} | Time: {elapsed}s")

    print("\n\n" + "="*70)
    print("  ✅ BENCHMARK COMPLETE")
    print(f"  📊 Results saved to: {RESULTS_CSV}")
    print("="*70)

if __name__ == "__main__":
    run_benchmark()
