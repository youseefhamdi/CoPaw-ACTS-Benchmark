import sys
import math
from collections import Counter

def chi_square_test(data):
    """Calculate chi-square statistic for byte frequency analysis"""
    if not data:
        return 0
    
    # Count byte frequencies
    freq = Counter(data)
    length = len(data)
    
    # Expected frequency for uniform distribution (256 possible byte values)
    expected = length / 256.0
    
    # Calculate chi-square statistic
    chi_square = 0
    for byte_val in range(256):
        observed = freq.get(byte_val, 0)
        chi_square += ((observed - expected) ** 2) / expected
    
    return chi_square

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 chi_square.py <file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'rb') as f:
            data = f.read()
        
        chi_square_value = chi_square_test(data)
        print(f"{chi_square_value:.2f}")
        
    except FileNotFoundError:
        print("Error: File not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()