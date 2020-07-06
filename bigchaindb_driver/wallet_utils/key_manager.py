from cryptography.fernet import Fernet
from account import * 
from mnemonic import *

# Save mnemonic in a non-encrypted file
def store_mnemonic(mnemonic):
	with open("mn.txt", "x") as file:
		file.write(mnemonic)
		file.close()

# Load keypair from mnemonic from a non-encrypted file
def load_keys_from_mnemonic(file):
	with open (file, "r") as mn:
		mnemonic = mn.readlines()[0]
		to_pk = to_private_key(mnemonic) 
		bdb_pk, bdb_pubkey = get_bdb_keys_from_pk(to_pk)
	return bdb_pk, bdb_pubkey

# Save mnemonic in an encrypted file
def store_encrypted_mnemonic(mnemonic, key=None):
	if key == None:
		key = Fernet.generate_key()  # Keep this secret!
		print("Store this encryption key: ", key)
	fernet = Fernet(key)
	encrypted_mnemonic = fernet.encrypt(mnemonic.encode())
	with open("mn.txt", "x") as file:
		file.write(encrypted_mnemonic.decode())
		file.close()

# Load keypair from mnemonic from an encrypted file
def load_keys_from_encrypted_mnemonic(file):
	with open (file, "r") as mn:
		encrypted_mnemonic = mn.read().encode()
		print("Enter your encryption key: ")
		key = input()
		fernet = Fernet(key)
		decrypted_mnemonic = fernet.decrypt(encrypted_mnemonic)
		print(decrypted_mnemonic)
		to_pk = to_private_key(decrypted_mnemonic.decode()) 
		bdb_pk, bdb_pubkey = get_bdb_keys_from_pk(to_pk)
	return bdb_pk, bdb_pubkey

# Save keypair in an encrypted file
def store_encrypted_keys(private_key, public_key, key=None):
	if key == None:
		key = Fernet.generate_key()  # Keep this secret!
		print("Store this encryption key: ", key)
	fernet = Fernet(key)
	encrypted_private_key = fernet.encrypt(private_key)
	encrypted_public_key = fernet.encrypt(public_key)
	with open("keys.txt", "x") as file:
		file.write(encrypted_private_key.decode())
		file.write('\n')
		file.write(encrypted_public_key.decode())
		file.close()

# Load keypair from an encrypted file
def load_keys_from_encrypted_file(file):
	with open (file, "r") as mn:
		encrypted_keys = mn.readlines()
		print(encrypted_keys)
		print("Enter your encryption key: ")
		key = input()
		fernet = Fernet(key)
		decrypted_keys = [fernet.decrypt(encrypted_keys[0].encode()), 
						  fernet.decrypt(encrypted_keys[1]).encode()]
		return decrypted_keys
		