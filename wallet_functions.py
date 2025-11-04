import os
import uuid
import base64
import requests
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv


load_dotenv()


# Load environment variables
API_KEY = os.getenv("API_KEY")
ENTITY_SECRET_ENV = os.getenv("ENTITY_SECRET")
WALLET_SET_ID_ENV = os.getenv("WALLET_SET_ID")
WALLET_ID_1_ENV = os.getenv("WALLET_ID_1")
WALLET_ADDRESS_2_ENV = os.getenv("WALLET_ADDRESS_2")
USDC_TOKEN_ID_ENV = os.getenv("USDC_TOKEN_ID")
BASE_URL = "https://api.circle.com/v1/w3s/developer"


# -------------------------------------------------------------------
# Generate a random secret (equivalent to crypto.randomBytes(32))
# -------------------------------------------------------------------
def generate_secret():
    return os.urandom(32).hex()


# -------------------------------------------------------------------
# Fetch public key from Circle
# -------------------------------------------------------------------
def fetch_public_key(api_key=API_KEY):
    url = "https://api.circle.com/v1/w3s/config/entity/publicKey"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data.get("data", {}).get("publicKey")


# -------------------------------------------------------------------
# Generate ciphertext (RSA-OAEP encrypt the secret)
# -------------------------------------------------------------------
def generate_ciphertext(secret_hex, api_key=API_KEY):
    if not secret_hex:
        raise ValueError("secret_hext must be provided to generate ciphertext.")
    
    try:
    # Convert hex secret to bytes
        entity_secret_bytes = bytes.fromhex(secret_hex)
    except Exception as e:
        raise ValueError("Invalid secret_hex (must be hex string)") from e

    # Fetch Circle public key
    public_key_pem = fetch_public_key(api_key)
    if not public_key_pem:
        raise RuntimeError("Could not fetch public key from Circle.")
    # Load public key
    public_key = serialization.load_pem_public_key(public_key_pem.encode())

    # Encrypt using RSA-OAEP (SHA256)
    encrypted_data = public_key.encrypt(
        entity_secret_bytes,
        padding.OAEP(
                     mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None
        ),
    )

    # Return base64-encoded ciphertext
    encoded = base64.b64encode(encrypted_data).decode()
    # print("Encrypted entity secret ciphertext:")
    # print(encoded)
    return encoded


# -------------------------------------------------------------------
# Create Wallet Set
# -------------------------------------------------------------------
def create_wallet_set(api_key=API_KEY, entity_secret_ciphertext=None, name="Set 1"):
    url = f"{BASE_URL}/walletSets"
    payload = {
        "entitySecretCiphertext": entity_secret_ciphertext,
        "idempotencyKey": str(uuid.uuid4()),
        "name": name
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Wallet Set Response:", response.json())
    return response.json()


# -------------------------------------------------------------------
# 5. Create Wallet(s)
# -------------------------------------------------------------------
def create_wallets(wallet_set_id, api_key=API_KEY, entity_secret_ciphertext=None, count=2):
    url = f"{BASE_URL}/wallets"
    payload = {
        "idempotencyKey": str(uuid.uuid4()),
        "entitySecretCiphertext": entity_secret_ciphertext,
        "accountType": "SCA",
        "blockchains": ["ARC-TESTNET"],
        "count": count,
        "metadata": [{"name":"User"},{"name":"Electricity"}],
        "walletSetId": wallet_set_id
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Wallet Creation Response:", response.json())
    return response.json()


# -------------------------------------------------------------------
# 6. List all Wallets
# -------------------------------------------------------------------
def list_wallets(api_key=API_KEY):
    url = "https://api.circle.com/v1/w3s/wallets"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    print("Wallets:", response.json())
    return response.json()


# -------------------------------------------------------------------
# Get Specific Wallet
# -------------------------------------------------------------------
def get_wallet(wallet_id, api_key=API_KEY):
    if not wallet_id:
        raise ValueError("wallet_id is required")
    
    url = f"{BASE_URL}/wallets/{wallet_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    print("Wallet Details:", response.json())
    return response.json()


# -------------------------------------------------------------------
# Get Wallet Balance
# -------------------------------------------------------------------
def get_wallet_balance(wallet_id, api_key=API_KEY):
    if not wallet_id:
        raise ValueError("wallet_id is required")
    url = f"https://api.circle.com/v1/w3s/wallets/{wallet_id}/balances"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    print("Balance:", response.json())
    return response.json()


# -------------------------------------------------------------------
# Transfer Token between Wallets
# -------------------------------------------------------------------
def transfer_token(wallet_id, entity_secret_ciphertext=None, destination_address=None, token_id=None, api_key=API_KEY, amount="2.0"):
    if not wallet_id:
        raise ValueError("wallet_id is required")
    if not destination_address:
        raise ValueError("destination_address is required")
    # use provided token_id or environment fallback
    token_id = token_id or USDC_TOKEN_ID_ENV
    if not token_id:
        raise ValueError("token_id must be provided (or set in env USDC_TOKEN_ID)")
    
    url = "https://api.circle.com/v1/w3s/developer/transactions/transfer"
    payload = {
        "idempotencyKey": str(uuid.uuid4()),
         "entitySecretCiphertext": entity_secret_ciphertext,
        "walletId": wallet_id,
        "tokenId": token_id,
        "destinationAddress": destination_address,
        "amounts": [amount],
        "feeLevel": "HIGH",
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    # print("Transfer Response:", response.json())
    return response.json()


# -------------------------------------------------------------------
# Check Transaction State
# -------------------------------------------------------------------
def get_transaction_status(transaction_id, api_key=API_KEY):
    url = f"{BASE_URL}/transactions/{transaction_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    print("Transaction Details:", response.json())
    return response.json()



if __name__ == "__main__":
    print("wallet_functions loaded — use functions from other modules.")
    # secret = generate_secret()
    # print("Generated Secret:", secret)

    # ciphertext = generate_ciphertext()
    # print("Ciphertext:", ciphertext)

    # wallet_set = create_wallet_set(entity_secret_ciphertext=ciphertext, name="Demo Set")
    # wallet_set_id = wallet_set["data"]["walletSet"]["id"]

    # wallets = create_wallets(wallet_set_id=WALLET_SET_ID, entity_secret_ciphertext=ciphertext, count=2)

    # list_wallets()
    # list_wallets()
    # get_wallet_balance()
    # transfer_token(entity_secret_ciphertext=ciphertext)