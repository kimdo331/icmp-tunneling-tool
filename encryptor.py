"""
binary encryption by AES-CBC

- encoding: utf-8
- key: 32 bytes
- origin: https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256

- date: 2022-10-16
- description:
    I modified it to use utf-8 encoding
    If key length is not 32 bytes, it will be padded with 0x00

"""

from Crypto.Cipher import AES
from secrets import token_bytes

key = ''
with open('key.txt', 'r') as f:
    key = f.read().encode('utf-8')[:32]
    key = key + bytes([0x00] * (32 - len(key))) # padding

assert len(key) == 32 # key length must be 32 bytes

BLOCK_SIZE = 16

def encrypt(msg: bytes) -> bytes:
    
    def _pad(s: bytes):
        return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE).encode('utf-8')
    msg = _pad(msg)
    
    iv = bytes([0x00] * 16)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(msg)
    return ciphertext

def decrypt(ciphertext: bytes) -> bytes:
    
    def _unpad(s):
        return s[:-s[-1]]
    
    iv = bytes([0x00] * 16)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext = cipher.decrypt(ciphertext)
    return _unpad(plaintext)


if __name__ == '__main__':
    ciphertext = encrypt('이것은 김도현이 작성한 테스트 문구입니다~!@#$%^&*()_+'.encode('utf-8'))
    # ciphertext = encrypt(b'happy')
    
    plaintext = decrypt(ciphertext)
    
    print(f'Cipher text: {ciphertext}, length: {len(ciphertext)}')
    if not plaintext:
        print('Message is corrupted')
    else:
        len_bytes = len(plaintext)
        print(f'Plain text: {plaintext.decode()}, length: {len_bytes}')