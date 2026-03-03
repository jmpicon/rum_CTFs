import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from solution import factorize, solve

N = 81072007
E = 65537
CIPHERTEXTS = [
    35052328, 22271299, 52920117, 58471634, 44240802, 7062297,
    35465995, 28706700, 13269390, 44240802, 31621302, 67049974,
    30135115, 44240802, 28706700, 22865087, 49700552, 49274517,
    34287145, 35465995, 22865087, 34287145, 49700552, 62169525,
]
FLAG = "CTF{rsa_primer_contacto}"


def test_factorize_n():
    p, q = factorize(N)
    assert p * q == N
    assert p != 1 and q != 1


def test_factorize_returns_primes():
    p, q = factorize(N)
    def is_prime(n):
        if n < 2: return False
        return all(n % i != 0 for i in range(2, int(n**0.5)+1))
    assert is_prime(p) and is_prime(q)


def test_decryption_correct():
    flag = solve(N, E, CIPHERTEXTS)
    assert flag == FLAG


def test_flag_format():
    flag = solve(N, E, CIPHERTEXTS)
    assert flag.startswith("CTF{") and flag.endswith("}")
