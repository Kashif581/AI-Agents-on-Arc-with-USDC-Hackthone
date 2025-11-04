from langchain_core.tools import tool
from wallet_functions import (
    generate_secret,
    generate_ciphertext,
    create_wallet_set,
    create_wallets,
    list_wallets,
    get_wallet,
    get_wallet_balance,
    transfer_token,
    get_transaction_status,
)
import os
from dotenv import load_dotenv

load_dotenv()

# ------------------ Wrappers ------------------

@tool
def tool_generate_secret():
    """Generate a new 32-byte random secret for Circle API."""
    secret = generate_secret()
    os.environ["ENTITY_SECRET"] = secret
    update_env("ENTITY_SECRET", secret)
    return f"New secret generated and stored in .env: {secret}"

@tool
def tool_generate_ciphertext():
    """Encrypt the entity secret using Circle public key."""
    secret = os.getenv("ENTITY_SECRET")
    ciphertext = generate_ciphertext(secret)
    os.environ["ENTITY_SECRET_CIPHERTEXT"] = ciphertext
    update_env("ENTITY_SECRET_CIPHERTEXT", ciphertext)
    return "Entity secret encrypted and ciphertext stored in .env."

@tool
def tool_create_wallet_set(name: str = "My Wallet Set"):
    """Create a new wallet set on Circle."""
    from wallet_functions import create_wallet_set
    ciphertext = os.getenv("ENTITY_SECRET_CIPHERTEXT")
    response = create_wallet_set(entity_secret_ciphertext=ciphertext, name=name)
    wallet_set_id = response["data"]["walletSet"]["id"]
    os.environ["WALLET_SET_ID"] = wallet_set_id
    update_env("WALLET_SET_ID", wallet_set_id)
    return f"Wallet set '{name}' created with ID {wallet_set_id}"

@tool
def tool_create_wallets(count: int = 2):
    """Create multiple wallets in the existing wallet set."""
    wallet_set_id = os.getenv("WALLET_SET_ID")
    ciphertext = os.getenv("ENTITY_SECRET_CIPHERTEXT")
    response = create_wallets(wallet_set_id, entity_secret_ciphertext=ciphertext, count=count)
    wallet_ids = [w["id"] for w in response["data"]["wallets"]]
    for i, wid in enumerate(wallet_ids, 1):
        os.environ[f"WALLET_ID_{i}"] = wid
        update_env(f"WALLET_ID_{i}", wid)
    return f"Created {len(wallet_ids)} wallets: {wallet_ids}"

@tool
def tool_list_wallets():
    """List all wallets from Circle."""
    response = list_wallets()
    return response

@tool
def tool_transfer_token(wallet_id: str, destination_address: str, amount: str = "1.0"):
    """Transfer USDC token between wallets."""
    ciphertext = os.getenv("ENTITY_SECRET_CIPHERTEXT")
    response = transfer_token(wallet_id, entity_secret_ciphertext=ciphertext, destination_address=destination_address, amount=amount)
    return response

@tool
def tool_get_wallet_balance(wallet_id: str):
    """Check wallet balance."""
    return get_wallet_balance(wallet_id)

@tool
def update_env(key: str, value: str):
    """Update .env file with a key=value pair."""
    with open(".env", "a") as f:
        f.write(f"\n{key}={value}")
    return f"{key}={value} added to .env"



