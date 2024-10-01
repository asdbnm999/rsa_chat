from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

def encrypt(message: str, pub_k='public_key.pem'):
    public_key = RSA.import_key(open(pub_k).read())
    cipher_rsa = PKCS1_OAEP.new(public_key)
    ciphertext = cipher_rsa.encrypt(bytes(message, 'utf-8'))
    return ciphertext

def decrypt(message: bytes, priv_k='private_key.pem'):
    private_key = RSA.import_key(open(priv_k).read())
    cipher_rsa = PKCS1_OAEP.new(private_key)
    decrypted_ciphertext = cipher_rsa.decrypt(message)
    return decrypted_ciphertext.decode('utf-8')
