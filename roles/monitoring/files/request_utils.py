from common import ValidatorConfig
import subprocess
import requests
import json
from common import debug


def execute_cmd_str(config: ValidatorConfig, cmd: str, convert_to_json: bool, default=None):
    """
    executes shell command and return string result
    :param default:
    :param config:
    :param convert_to_json:
    :param cmd: shell command
    :return: returns string result or None
    """
    try:
        debug(config, cmd)
        result: str = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, timeout=10).decode().strip()

        if convert_to_json:
            result = json.loads(result)

        debug(config, result)

        return result
    except:
        return default


def rpc_call(config: ValidatorConfig, address: str, method: str, params, error_result, except_result):
    """
    calls solana rpc (https://docs.solana.com/developing/clients/jsonrpc-api)
    and returns result or default
    :param config:
    :param except_result:
    :param error_result:
    :param address: local or remote rpc server address
    :param method: rpc method
    :param params: rpc call parameters
    :return: result or default
    """
    try:
        json_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        debug(config, json_request)
        debug(config, address)

        json_response = requests.post(address, json=json_request).json()
        if 'result' not in json_response:
            result = error_result
        else:
            result = json_response['result']
    except:
        result = except_result

    debug(config, result)

    return result


def smart_rpc_call(config: ValidatorConfig, method: str, params, default_result):
    """
    tries to call local rpc, if it fails tries to call remote rpc
    """
    result = rpc_call(config, config.local_rpc_address, method, params, None, None)

    if result is None:
        result = rpc_call(config, config.remote_rpc_address, method, params, default_result, default_result)

    return result
