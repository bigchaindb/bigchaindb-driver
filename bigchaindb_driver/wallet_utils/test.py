import sys
sys.path.append("..")


from crypto import *
from account import * 
from mnemonic import *
from key_manager import *


alice_keypair = generate_keypair()

print("Alice's keypair: ", '\n', alice_keypair)

# Get base64 private key and address from BDB keypair
pk, address = get_address_from_bdb(alice_keypair.private_key, alice_keypair.public_key)
print("Base64 private key: ", pk)

# Load BDB keypair from the base64 private key
print("BDB keys: ")
bdb_pk, bdb_pubkey = get_bdb_keys_from_pk(pk)
print(bdb_pk, bdb_pubkey)

# Derive mnemonic from base64 private key
mnemonic_pk = from_private_key(pk)

# Store mnemonic with a Fernet key and load the BDB keys from the encrypted mnemonic file
store_encrypted_mnemonic(mnemonic_pk, key=None)
private_key, public_key = load_keys_from_encrypted_mnemonic('mn.txt')
print(private_key, public_key)

# Store keypair with a Fernet key and load the BDB keys from the encrypted mnemonic file
store_encrypted_keys(alice_keypair.private_key, alice_keypair.public_key, key=None)
load_keys_from_encrypted_file('keys.txt')
