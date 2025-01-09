import time
import solana_rpc as rpc
from common import debug, ValidatorConfig, measurement_from_fields
import statistics
import numpy as np
import tds_info as tds

def load_data(config: ValidatorConfig):
    """
    Load TDS-related data for a given validator configuration.

    Args:
        config (ValidatorConfig): Validator configuration containing details for RPC calls.

    Returns:
        dict: Dictionary containing identity account public key and TDS data.
    """
    identity_account_pubkey = rpc.load_identity_account_pubkey(config)
    default = []
    tds_data = tds.load_tds_info(config, identity_account_pubkey) if identity_account_pubkey else default

    result = {
        'identity_account_pubkey': identity_account_pubkey,
        'tds_data': tds_data
    }

    debug(config, str(result))
    return result

def calculate_influx_fields(data):
    """
    Calculate fields for influx measurements based on loaded TDS data.

    Args:
        data (dict): Loaded TDS data.

    Returns:
        dict: Fields for influx measurements.
    """
    if data is None:
        return {"tds_info": 0}

    return data['tds_data'] if 'tds_data' in data else {"tds_info": 0}

def calculate_output_data(config: ValidatorConfig):
    """
    Calculate measurement output for TDS info.

    Args:
        config (ValidatorConfig): Validator configuration.

    Returns:
        dict: Measurement data ready for output.
    """
    data = load_data(config)

    tags = {
        "validator_identity_pubkey": data['identity_account_pubkey'],
        "validator_name": config.validator_name,
        "cluster_environment": config.cluster_environment
    }

    return measurement_from_fields(
        "tds_info",
        calculate_influx_fields(data),
        tags,
        config
    )
