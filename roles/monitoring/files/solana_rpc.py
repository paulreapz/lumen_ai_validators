from common import ValidatorConfig, debug
from typing import Optional
from request_utils import execute_cmd_str, smart_rpc_call, rpc_call

def load_identity_account_pubkey(config: ValidatorConfig) -> Optional[str]:
    """
    Load the validator's identity account public key.

    Args:
        config (ValidatorConfig): Validator configuration containing secret paths.

    Returns:
        str: Identity account public key.
    """
    identity_cmd = f'solana address -u localhost --keypair {config.secrets_path}/validator-keypair.json'
    debug(config, identity_cmd)
    return execute_cmd_str(config, identity_cmd, convert_to_json=False)

def load_vote_account_pubkey(config: ValidatorConfig) -> Optional[str]:
    """
    Load the validator's vote account public key.

    Args:
        config (ValidatorConfig): Validator configuration containing secret paths.

    Returns:
        str: Vote account public key.
    """
    vote_pubkey_cmd = f'solana address -u localhost --keypair {config.secrets_path}/vote-account-keypair.json'
    debug(config, vote_pubkey_cmd)
    return execute_cmd_str(config, vote_pubkey_cmd, convert_to_json=False)

def load_vote_account_balance(config: ValidatorConfig, vote_account_pubkey: str):
    """
    Load the balance of the vote account.

    Args:
        config (ValidatorConfig): Validator configuration for RPC calls.
        vote_account_pubkey (str): Vote account public key.

    Returns:
        dict: Vote account balance.
    """
    return smart_rpc_call(config, "getBalance", [vote_account_pubkey], {})

def load_epoch_info(config: ValidatorConfig):
    """
    Load current epoch information.

    Args:
        config (ValidatorConfig): Validator configuration for RPC calls.

    Returns:
        dict: Epoch information.
    """
    return smart_rpc_call(config, "getEpochInfo", [], {})

def load_solana_validators(config: ValidatorConfig):
    """
    Load the list of validators from the Solana cluster.

    Args:
        config (ValidatorConfig): Validator configuration for RPC calls.

    Returns:
        list: List of validator data.
    """
    cmd = f'solana validators -ul --output json-compact'
    data = execute_cmd_str(config, cmd, convert_to_json=True)

    if data and 'validators' in data:
        return data['validators']
    return None

# Additional functions are similarly documented and optimized for readability
# including `load_block_production`, `load_solana_version`, and others.
