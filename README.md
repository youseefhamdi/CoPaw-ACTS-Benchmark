# CoPaw-ACTS-Benchmark

**ACTS: AI Cryptanalysis Testing System**

A reproducible four-tier benchmark for evaluating LLM cipher identification under controlled metadata and tool-augmentation conditions.

## Dataset
Seven encryption families: DES, 3DES, AES-128, AES-256, ChaCha20, RSA-2048+AES-256, ML-KEM-768  
Generated using OpenSSL v3.1 and liboqs v0.10. All files are 1KB nominal plaintext size.

## Results
- `results_tier1.csv` — Tier-1 metadata-aided results (4 frontier models)
- `results_blind_v3.csv` — Tier-2/3 blind results (15 models)
- `results_agentic_blind.csv` — Tier-4B CoPaw agentic-blind results
- `results_ollama_available.csv` — Extended Ollama evaluation

## Usage
```bash
pip install -r requirements.txt
python benchmark_v2.py
```

## Citation
Youssef Hamdi Zafaan Ibrahim, Mohammed Khalaf Salama.
"ACTS: A Multi-Tier Benchmark for Evaluating LLM Cipher Identification
Under Controlled Metadata and Tool-Augmentation Conditions." 2026.

## License
MIT License
