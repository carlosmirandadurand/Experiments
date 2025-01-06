import os
import zipfile
import hashlib
import shutil
import getpass
import secrets

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.exceptions import InvalidKey


# Global constants

SALT_SIZE = 16       # length of salt
KEY_SIZE = 32        # length of encription key
BLOCK_SIZE = 128     # size of padding block 
AES_BLOCK_SIZE = 16  # block size of the AES cipher (fixed)
HASH_FILE_NAME = "_file_vault_content_checks_.txt"
PACKED_FILE_SUFFIX = "_packed"


# Validation functions

def validate_password(password):
    """Ensure the password is minimally appropriate."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if password.isdigit() or password.isalpha():
        raise ValueError("Password must contain both letters and numbers.")

def compute_checksum(directory):
    """Compute a checksum for all files in a directory, excluding the checksum file itself."""
    hash_sha256 = hashlib.sha256()
    for root, _, files in sorted(os.walk(directory)):
        for file in sorted(files):
            if file == HASH_FILE_NAME:  # Skip the checksum file itself
                continue
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


# Encription/decription functions

def derive_key(password, salt):
    """Derive a key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_file(file_path, password, output_path):
    """Encrypt a file using AES."""
    salt = secrets.token_bytes(SALT_SIZE)
    key = derive_key(password, salt)

    with open(file_path, 'rb') as f:
        data = f.read()

    padder = PKCS7(BLOCK_SIZE).padder()
    padded_data = padder.update(data) + padder.finalize()

    iv = secrets.token_bytes(AES_BLOCK_SIZE)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    with open(output_path, 'wb') as f:
        f.write(salt + iv + encrypted_data)

def decrypt_file(file_path, password, output_path):
    """Decrypt a file using AES."""
    with open(file_path, 'rb') as f:
        content = f.read()

    salt = content[:SALT_SIZE]
    iv = content[SALT_SIZE:SALT_SIZE + AES_BLOCK_SIZE]
    encrypted_data = content[SALT_SIZE + AES_BLOCK_SIZE:]

    key = derive_key(password, salt)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    try:
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = PKCS7(BLOCK_SIZE).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        with open(output_path, 'wb') as f:
            f.write(data)
    except InvalidKey:
        print("Decryption failed. Invalid password or corrupted file.")
        return False
    return True


# Compression functions

def zip_folder(folder_path, output_zip):
    """Compress a folder into a zip file."""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=folder_path)
                zipf.write(file_path, arcname)

def unzip_folder(zip_path, output_folder):
    """Extract a zip file to a folder."""
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(output_folder)


# Main operations of this program

def pack(location, password, nocleanup=False):
    """Pack (zip and encrypt) a folder."""

    # Check the inputs
    validate_password(password)
    if not os.path.isdir(location):
        raise ValueError(f"'{location}' is not a valid directory.")
    
    # Create a new checksum file 
    checksum_file = os.path.join(location, HASH_FILE_NAME)
    if os.path.exists(checksum_file):
        raise ValueError(f"Checksum file '{HASH_FILE_NAME}' already exists. Aborting.")
    
    checksum = compute_checksum(location)
    with open(checksum_file, 'w') as f:
        f.write(checksum)
    
    # Compress and encript the contents
    temp_zip = location + "_tmp_e.zip"
    zip_folder(location, temp_zip)

    encrypted_file = location + PACKED_FILE_SUFFIX
    encrypt_file(temp_zip, password, encrypted_file)
    os.remove(temp_zip)

    # Remove the original unpacked content, unless otherwise specified
    if not nocleanup:
        shutil.rmtree(location)

    print(f"Folder '{location}' has been zipped and encrypted as '{encrypted_file}'.")

def unpack(location, password, nocleanup=False):
    """Unpack (decrypt and unzip) an encrypted file."""

    # Check inputs
    validate_password(password)
    if not os.path.isfile(location):
        raise ValueError(f"'{location}' is not a valid file.")
    
    # Decript and unzip
    temp_decrypted_file = location + "_tmp_d.zip"
    if not decrypt_file(location, password, temp_decrypted_file):
        return

    output_folder = location.replace(PACKED_FILE_SUFFIX, "")
    unzip_folder(temp_decrypted_file, output_folder)
    os.remove(temp_decrypted_file)

    # Validate the checksum
    checksum_file = os.path.join(output_folder, HASH_FILE_NAME)
    if not os.path.exists(checksum_file):
        raise ValueError(f"Checksum file '{HASH_FILE_NAME}' missing after unpacking. Aborting.")
    
    with open(checksum_file, 'r') as f:
        original_checksum = f.read()
    os.remove(checksum_file)

    unpacked_checksum = compute_checksum(output_folder)
    if original_checksum != unpacked_checksum:
        shutil.rmtree(output_folder)
        raise ValueError("Checksum mismatch. Unpacking failed due to data corruption.")


    # Remove the packed content since the original unpacked was restored, unless otherwise specified
    if not nocleanup:
        os.remove(location)

    print(f"File '{location}' has been unpacked and restored to '{output_folder}'.")



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FolderVault: Securely pack and unpack directories.")
    parser.add_argument("operation", choices=["pack", "unpack"], help="Operation to perform: 'pack' or 'unpack'.")
    parser.add_argument("location", help="Path to the directory (for 'pack') or encrypted file (for 'unpack').")
    parser.add_argument("--password", help="Password or passphrase (optional).")
    parser.add_argument("--nocleanup", action="store_true", help="Do not delete original contents after operation.")

    args = parser.parse_args()

    try:
        password = args.password
        if not password:
            password  = getpass.getpass("Enter password: ")
            password2 = getpass.getpass("Reenter password: ")
            if password != password2:
                raise ValueError("Passwords do not match")

        if args.operation == "pack":
            pack(args.location, password, args.nocleanup)
        elif args.operation == "unpack":
            unpack(args.location, password, args.nocleanup)
        else:
            raise ValueError("Incorrect operation: must select either pack or unpack")

    except Exception as e:
        print(f"Error: {e}")

# To generate executable:
# pip install pyinstaller
# pyinstaller --onefile --name filevault filevault.py
# cd dist
# add exe to path
# filevault.exe pack my_folder 

