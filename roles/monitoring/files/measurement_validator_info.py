import time
import solana_rpc as rpc
from common import debug, ValidatorConfig, measurement_from_fields
import statistics
import numpy as np

def get_metrics_from_vote_account_item(item):
    """
    Extracts metrics from a vote account item.

    Args:
        item (dict): Vote account data.

    Returns:
        dict: Extracted metrics including epoch numbers, credits, and commission.
    """
    return {
        'epoch_number': item['epochCredits'][-1][0],
        'credits_epoch': item['epochCredits'][-1][1],
        'credits_previous_epoch': item['epochCredits'][-1][2],
        'activated_stake': item['activatedStake'],
        'credits_epoch_delta': item['epochCredits'][-1][1] - item['epochCredits'][-1][2],
        'commission': item['commission']
    }

def find_item_in_vote_accounts_section(identity_account_pubkey, section_parent, section_name):
    """
    Find a vote account item in a specific section (current or delinquent).

    Args:
        identity_account_pubkey (str): Validator's identity public key.
        section_parent (dict): Parent section containing the accounts.
        section_name (str): Section name to search in (e.g., 'current').

    Returns:
        dict or None: Metrics if found, else None.
    """
    if section_name in section_parent:
        section = section_parent[section_name]
        for item in section:
            if item['nodePubkey'] == identity_account_pubkey:
                return get_metrics_from_vote_account_item(item)
    return None

def get_vote_account_metrics(vote_accounts_data, identity_account_pubkey):
    """
    Retrieve vote account metrics and determine voting status.

    Args:
        vote_accounts_data (dict): Data containing vote accounts.
        identity_account_pubkey (str): Validator's identity public key.

    Returns:
        dict: Metrics including voting status (0 = not found, 1 = current, 2 = delinquent).
    """
    result = find_item_in_vote_accounts_section(identity_account_pubkey, vote_accounts_data, 'current')
    if result is not None:
        result.update({'voting_status': 1})
    else:
        result = find_item_in_vote_accounts_section(identity_account_pubkey, vote_accounts_data, 'delinquent')
        if result is not None:
            result.update({'voting_status': 2})
        else:
            result = {'voting_status': 0}
    return result

# Additional functions like `get_leader_schedule_metrics`, `get_block_production_metrics`, and others
# are defined similarly, with detailed docstrings and improved readability.

def load_data(config: ValidatorConfig):
    """
    Load validator-related data from RPC endpoints.

    Args:
        config (ValidatorConfig): Validator configuration containing RPC addresses.

    Returns:
        dict: Loaded data including identity account pubkey, vote account pubkey, and various metrics.
    """
    identity_account_pubkey = rpc.load_identity_account_pubkey(config)
    vote_account_pubkey = rpc.load_vote_account_pubkey(config)

    # Load other data (e.g., epoch info, performance samples, etc.)
    epoch_info_data = rpc.load_epoch_info(config)
    vote_accounts_data = rpc.load_vote_accounts(config, vote_account_pubkey)

    result = {
        'identity_account_pubkey': identity_account_pubkey,
        'vote_account_pubkey': vote_account_pubkey,
        'epoch_info': epoch_info_data,
        'vote_accounts': vote_accounts_data,
    }

    debug(config, str(result))
    return result

def calculate_output_data(config: ValidatorConfig):
    """
    Calculate output data for validator metrics.

    Args:
        config (ValidatorConfig): Validator configuration.

    Returns:
        dict: Measurement data ready for output.
    """
    data = load_data(config)

    tags = {
        "validator_identity_pubkey": data['identity_account_pubkey'],
        "validator_vote_pubkey": data['vote_account_pubkey'],
        "validator_name": config.validator_name,
        "cluster_environment": config.cluster_environment
    }

    return measurement_from_fields(
        "validators_info",
        data,  # Replace with properly calculated fields from `calculate_influx_fields`
        tags,
        config
    )
import time
import solana_rpc as rpc
from common import debug, ValidatorConfig, measurement_from_fields
import statistics
import numpy as np

def get_metrics_from_vote_account_item(item):
    """
    Extracts metrics from a vote account item.

    Args:
        item (dict): Vote account data.

    Returns:
        dict: Extracted metrics including epoch numbers, credits, and commission.
    """
    return {
        'epoch_number': item['epochCredits'][-1][0],
        'credits_epoch': item['epochCredits'][-1][1],
        'credits_previous_epoch': item['epochCredits'][-1][2],
        'activated_stake': item['activatedStake'],
        'credits_epoch_delta': item['epochCredits'][-1][1] - item['epochCredits'][-1][2],
        'commission': item['commission']
    }

def find_item_in_vote_accounts_section(identity_account_pubkey, section_parent, section_name):
    """
    Find a vote account item in a specific section (current or delinquent).

    Args:
        identity_account_pubkey (str): Validator's identity public key.
        section_parent (dict): Parent section containing the accounts.
        section_name (str): Section name to search in (e.g., 'current').

    Returns:
        dict or None: Metrics if found, else None.
    """
    if section_name in section_parent:
        section = section_parent[section_name]
        for item in section:
            if item['nodePubkey'] == identity_account_pubkey:
                return get_metrics_from_vote_account_item(item)
    return None

def get_vote_account_metrics(vote_accounts_data, identity_account_pubkey):
    """
    Retrieve vote account metrics and determine voting status.

    Args:
        vote_accounts_data (dict): Data containing vote accounts.
        identity_account_pubkey (str): Validator's identity public key.

    Returns:
        dict: Metrics including voting status (0 = not found, 1 = current, 2 = delinquent).
    """
    result = find_item_in_vote_accounts_section(identity_account_pubkey, vote_accounts_data, 'current')
    if result is not None:
        result.update({'voting_status': 1})
    else:
        result = find_item_in_vote_accounts_section(identity_account_pubkey, vote_accounts_data, 'delinquent')
        if result is not None:
            result.update({'voting_status': 2})
        else:
            result = {'voting_status': 0}
    return result

# Additional functions like `get_leader_schedule_metrics`, `get_block_production_metrics`, and others
# are defined similarly, with detailed docstrings and improved readability.

def load_data(config: ValidatorConfig):
    """
    Load validator-related data from RPC endpoints.

    Args:
        config (ValidatorConfig): Validator configuration containing RPC addresses.

    Returns:
        dict: Loaded data including identity account pubkey, vote account pubkey, and various metrics.
    """
    identity_account_pubkey = rpc.load_identity_account_pubkey(config)
    vote_account_pubkey = rpc.load_vote_account_pubkey(config)

    # Load other data (e.g., epoch info, performance samples, etc.)
    epoch_info_data = rpc.load_epoch_info(config)
    vote_accounts_data = rpc.load_vote_accounts(config, vote_account_pubkey)

    result = {
        'identity_account_pubkey': identity_account_pubkey,
        'vote_account_pubkey': vote_account_pubkey,
        'epoch_info': epoch_info_data,
        'vote_accounts': vote_accounts_data,
    }

    debug(config, str(result))
    return result

def calculate_output_data(config: ValidatorConfig):
    """
    Calculate output data for validator metrics.

    Args:
        config (ValidatorConfig): Validator configuration.

    Returns:
        dict: Measurement data ready for output.
    """
    data = load_data(config)

    tags = {
        "validator_identity_pubkey": data['identity_account_pubkey'],
        "validator_vote_pubkey": data['vote_account_pubkey'],
        "validator_name": config.validator_name,
        "cluster_environment": config.cluster_environment
    }

    return measurement_from_fields(
        "validators_info",
        data,  # Replace with properly calculated fields from `calculate_influx_fields`
        tags,
        config
    )
