from langchain_core.tools import tool
from wallet_functions import (
    generate_ciphertext,
    create_wallet_set,
    create_wallets,
    list_wallets,
    get_wallet,
    get_wallet_balance,
    transfer_token,
    get_transaction_status,
    update_env,
    get_wallet_info_by_name,
)
import os
from dotenv import load_dotenv

load_dotenv()

# ------------------ Wrappers ------------------


@tool
def tool_create_wallet_set(name: str):
    """Create a new wallet set on Circle."""
    
    # from wallet_functions import create_wallet_set
    # secret = generate_secret()
    secret = os.getenv("ENTITY_SECRET")
    print(secret)
    ciphertext = generate_ciphertext(secret)
    print(ciphertext)
    response = create_wallet_set(entity_secret_ciphertext=ciphertext, name=name)
    wallet_set_id = response["data"]["walletSet"]["id"]
    print(wallet_set_id)
    os.environ["WALLET_SET_ID"] = wallet_set_id
    update_env("WALLET_SET_ID", wallet_set_id)
    # return f"Wallet set '{name}' created with ID {wallet_set_id}"

@tool
def tool_create_wallets(count: int, wallet_names: list):
    """Create multiple wallets in the wallet set with user-provided names."""
    wallet_set_id = os.getenv("WALLET_SET_ID")
    secret = os.getenv("ENTITY_SECRET")
    ciphertext = generate_ciphertext(secret)
    # wallet_names = ["Electricity", "Gas", "Water"]
    response = create_wallets(wallet_set_id, entity_secret_ciphertext=ciphertext, wallet_names=wallet_names)
    wallet_ids = [w["id"] for w in response["data"]["wallets"]]
    wallet_adr = [w["address"] for w in response["data"]["wallets"]]
    print(wallet_ids)
    for i, wid in enumerate(wallet_ids, 1):
        os.environ[f"WALLET_ID_{i}"] = wid
        update_env(f"WALLET_ID_{i}", wid)
    for i, wadr in enumerate(wallet_adr, 1):
        os.environ[f"WALLET_ADDRESS_{i}"] = wadr
        update_env(f"WALLET_ADDRESS_{i}", wadr)
    # return f"Created {len(wallet_ids)} wallets: {wallet_ids}"

@tool
def tool_list_wallets():
    """List all wallets from Circle."""
    response = list_wallets()
    return response

@tool
def tool_transfer_token(from_wallet_name: str, to_wallet_name: str, amount: str, token_id: str):
    """Transfer USDC token between wallets."""
    from_wallet = get_wallet_info_by_name(from_wallet_name)
    to_wallet = get_wallet_info_by_name(to_wallet_name)
    if not from_wallet or not to_wallet:
        return f"Could not find one or both wallet names in .env."
    
    secret = os.getenv("ENTITY_SECRET")
    ciphertext = generate_ciphertext(secret)
    response = transfer_token(
        wallet_id=from_wallet["wallet_id"], 
        entity_secret_ciphertext=ciphertext, 
        destination_address=to_wallet["wallet_address"], 
        amount=amount, 
        token_id="5042002"
        )
    return response

@tool
def tool_get_wallet_balance(wallet_id: str):
    """Check wallet balance."""
    return get_wallet_balance(wallet_id)






