from common import ValidatorConfig
import requests
from common import debug


def tds_rpc_call(config: ValidatorConfig, identity_account_pubkey: str):

    address = "https://kyc-api.vercel.app/api/validators/list?search_term=" + identity_account_pubkey

    try:
        debug(config, address)
        json_response = requests.get(address, timeout=5).json()
        if 'data' not in json_response:
            result = {}
        else:
            result = json_response['data']
    except:
        result = {}

    debug(config, result)

    return result


def load_tds_info(config: ValidatorConfig, identity_account_pubkey: str):
    tds_data = tds_rpc_call(config, identity_account_pubkey)
    result = {}
    if tds_data != [] and tds_data != {}:
        if 'tnCalculatedStats' in tds_data[0] and tds_data[0]['tnCalculatedStats'] is not None:
            result = {
                'tds': tds_data[0]['tnCalculatedStats'],
            }
            if 'onboardingNumber' in tds_data[0]:
                result['tds']['onboardingNumber'] = tds_data[0]['onboardingNumber']
                result['tds']['tdsOnboardingGroup'] = tds_data[0]['tdsOnboardingGroup']

    debug(config, result)

    return result
