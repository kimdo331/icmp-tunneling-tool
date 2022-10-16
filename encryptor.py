"""
binary encryption by AES-CBC

encoding: utf-8
key: 32 bytes
origin: https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256

date: 2022-10-16
description:
    I modified it to use utf-8 encoding

"""

from Crypto.Cipher import AES
from secrets import token_bytes

# key = token_bytes(32)
key = 'happynewyear2022happynewyear2022'.encode('utf-8')
assert len(key) == 32 # key length must be 32

BLOCK_SIZE = 16

def encrypt(msg: str):
    
    def _pad(s):
        return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE).encode('utf-8')
    msg = _pad(msg.encode('utf-8'))
    
    iv = bytes([0x00] * 16)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(msg)
    return ciphertext

def decrypt(ciphertext):
    
    def _unpad(s):
        return s[:-s[-1]]
    
    iv = bytes([0x00] * 16)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext = cipher.decrypt(ciphertext)
    return _unpad(plaintext).decode('utf-8')


if __name__ == '__main__':
    ciphertext = encrypt('김도현김도현김도현김도현김도현')
    # ciphertext = encrypt('happy')
    
    plaintext = decrypt(ciphertext)
    
    print(f'Cipher text: {ciphertext}')
    if not plaintext:
        print('Message is corrupted')
    else:
        print(f'Plain text: {plaintext}')