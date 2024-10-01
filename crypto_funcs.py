from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def encrypt(message: str, pub_k='public_key.pem'):
    public_key = RSA.import_key(open(pub_k).read())
    cipher_rsa = PKCS1_OAEP.new(public_key)
    ciphertext_segments = []

    # Instead of a fixed segment size, use a limit based on key size
    key_size = 190
    for i in range(0, len(message), key_size):
        segment = message[i:i + key_size]
        ciphertext = cipher_rsa.encrypt(segment.encode('utf-8'))
        # We can join segments with a special delimiter if needed in case of further processing.
        ciphertext_segments.append(ciphertext)

    return b''.join(ciphertext_segments)

def decrypt(ciphertext: bytes, priv_k='private_key.pem'):
    private_key = RSA.import_key(open(priv_k).read())
    cipher_rsa = PKCS1_OAEP.new(private_key)

    key_size = private_key.size_in_bytes()
    decrypted_segments = []

    # Split ciphertext into equal segments based on the expected ciphertext size
    for i in range(0, len(ciphertext), key_size):
        segment = ciphertext[i:i + key_size]
        decrypted_segment = cipher_rsa.decrypt(segment)
        decrypted_segments.append(decrypted_segment.decode('utf-8'))

    return ''.join(decrypted_segments)

def check_access():
    try:
        return int(decrypt(encrypt('1')))
    except ValueError:
        return False

print(check_access())
#decrypt_long_messages(encrypt('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'))