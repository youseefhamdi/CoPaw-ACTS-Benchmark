#!/usr/bin/env python3
import os, base64, hashlib

DATASET = "dataset/encrypted"
SIZES = ["1kb", "10kb", "100kb"]
TIER1_MODELS = ["GPT-4o", "Claude-3.5-Sonnet", "Gemini-1.5-Pro", "Perplexity-Pro"]

print("=== AI CRYPTANALYSIS BENCHMARK ===")
print(f"Dataset: {len(os.listdir(DATASET))} files ready\n")

for size in SIZES:
    print(f"\n## SIZE: {size.upper()}")
    print("-" * 60)
    
    for file in sorted(os.listdir(DATASET)):
        if size in file:
            path = f"{DATASET}/{file}"
            size_bytes = os.path.getsize(path)
            
            # Hex dump لأول 128 bytes (للـ prompt)
            with open(path, 'rb') as f:
                data = f.read(128)
            hex_dump = data.hex()
            
            print(f"\n### FILE: {file} ({size_bytes} bytes)")
            print("=" * 60)
            print(f"Ciphertext (first 128 bytes):")
            print(f"```{hex_dump}```")
            print("\n**PROMPT TEMPLATE** (Copy & paste):")
            print()
            print(f"""```
You are a cryptanalysis expert. Analyze this ciphertext:

Filename: {file}
Size: {size_bytes} bytes
Hex (first 128B): {hex_dump}

TASK:
1. Identify the encryption algorithm/mode
2. Estimate key size
3. Can it be broken? If yes, how?
4. Show your reasoning step-by-step.

Respond in this exact format:
ALGO: [your guess]
KEYSIZE: [bits]
BREAKABLE: [YES/NO/PARTIALLY]
REASONING: [detailed steps]
```""")
            
            print("-" * 60)
            print("Results for this file:")
            print("Model | Time | ALGO | KEYSIZE | BREAKABLE | Notes")
            print("-" * 60)

print("\n[+] Ready for manual Tier 1 benchmarking!")
print("Start with DES_1kb.bin → copy prompt → GPT/Claude → record results")
