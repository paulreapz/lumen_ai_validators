import time
import solana_rpc as rpc
from common import debug
from common import ValidatorConfig
import statistics
import numpy as np
import tds_info as tds
from common import measurement_from_fields

def load_data(config: ValidatorConfig):
    identity_account_pubkey = rpc.load_identity_account_pubkey(config)
    default = []
    tds_data = default
    tds_data = tds.load_tds_info(config, identity_account_pubkey)
    
    result = {
        'identity_account_pubkey': identity_account_pubkey,
        'tds_data': tds_data
    }

    debug(config, str(result))

    return result

def calculate_influx_fields(data):
    if data is None:
        result = {"tds_info": 0}
    else:
        identity_account_pubkey = data['identity_account_pubkey']

        result = data['tds_data']
    return result

def calculate_output_data(config: ValidatorConfig):
    data = load_data(config)

    tags = {
        "validator_identity_pubkey": data['identity_account_pubkey'],
        "validator_name": config.validator_name,
        "cluster_environment": config.cluster_environment
    }


    measurement = measurement_from_fields(
        "tds_info",
        calculate_influx_fields(data),
        tags,
        config
    )
    return measurement
