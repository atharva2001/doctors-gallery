from passlib.context import CryptContext
import hashlib
import os
import base64
import hmac

iterations = 100_000

def hash_pass(password: str):
    hash_b64 = base64.b85decode(password.encode("utf-8"))
    return hash_b64

# Verify
# def verify_password(input_password, stored_hash_b64):
#     decr_stored_hash = base64.b85decode(stored_hash_b64).decode("utf-8")
#     print(decr_stored_hash, input_password)
#     return decr_stored_hash == input_password

def verify_password(input_password: str, stored_hash_b64: str) -> bool:
    print(input_password, stored_hash_b64)
    return input_password == stored_hash_b64