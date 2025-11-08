from langchain_core.tools import tool
import streamlit as st
from wallet_functions import (
    generate_ciphertext,
    create_wallet_set,
    create_wallets,
    list_wallets,
    get_wallet_balance,
    transfer_token,
)


# ------------------ Wrappers ------------------

@tool
def tool_create_wallet_set(name: str):
    """Create a new wallet set on Circle."""
    secret = st.session_state.get("ENTITY_SECRET")
    
    ciphertext = generate_ciphertext(secret)
    response = create_wallet_set(entity_secret_ciphertext=ciphertext, name=name)
    wallet_set_id = response["data"]["walletSet"]["id"]
    return wallet_set_id


@tool
def tool_create_wallets(wallet_set_id:str, count: int, wallet_names: list[str]):
    """Create multiple wallets in the wallet set with user-provided names."""
    secret = st.session_state.get("ENTITY_SECRET")

    wallet_set_id = wallet_set_id
    secret = st.session_state.get("ENTITY_SECRET")
    ciphertext = generate_ciphertext(secret)
    response = create_wallets(wallet_set_id, entity_secret_ciphertext=ciphertext, wallet_names=wallet_names)
    return response

@tool
def tool_list_wallets():
    """List all wallets from Circle."""
    response = list_wallets()
    return response

@tool
def tool_transfer_token(wallet_id: str, destination_address: str, amount: str):
    """Transfer USDC token between wallets."""
    secret = st.session_state.get("ENTITY_SECRET")
    secret = st.session_state.get("ENTITY_SECRET")
    ciphertext = generate_ciphertext(secret)
    response = transfer_token(wallet_id, entity_secret_ciphertext=ciphertext, destination_address=destination_address, amount=amount)
    return response

@tool
def tool_get_wallet_balance(wallet_id: str):
    """Check wallet balance."""
    return get_wallet_balance(wallet_id)






