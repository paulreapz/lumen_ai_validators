from common import ValidatorConfig, debug
import subprocess
import requests
import json

def execute_cmd_str(config: ValidatorConfig, cmd: str, convert_to_json: bool, default=None):
    """
    Execute a shell command and return its output.

    Args:
        config (ValidatorConfig): Validator configuration for debug logging.
        cmd (str): Command to execute.
        convert_to_json (bool): Whether to parse the output as JSON.
        default: Default value to return in case of failure.

    Returns:
        str or dict: Command output as a string or parsed JSON.
    """
    try:
        debug(config, cmd)
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, timeout=10).decode().strip()

        if convert_to_json:
            result = json.loads(result)

        debug(config, result)
        return result
    except Exception as e:
        debug(config, f"Command failed: {e}")
        return default

def rpc_call(config: ValidatorConfig, address: str, method: str, params, error_result, except_result):
    """
    Perform an RPC call to a Solana node.

    Args:
        config (ValidatorConfig): Validator configuration for debug logging.
        address (str): RPC server address.
        method (str): RPC method to call.
        params: Parameters for the RPC method.
        error_result: Default value to return in case of error.
        except_result: Default value to return in case of exception.

    Returns:
        dict: RPC call result.
    """
    try:
        json_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        debug(config, json_request)
        json_response = requests.post(address, json=json_request).json()

        if 'result' not in json_response:
            return error_result
        return json_response['result']
    except Exception as e:
        debug(config, f"RPC call failed: {e}")
        return except_result

def smart_rpc_call(config: ValidatorConfig, method: str, params, default_result):
    """
    Perform an RPC call, trying the local server first and falling back to the remote server.

    Args:
        config (ValidatorConfig): Validator configuration for debug logging.
        method (str): RPC method to call.
        params: Parameters for the RPC method.
        default_result: Default value to return in case of failure.

    Returns:
        dict: RPC call result.
    """
    result = rpc_call(config, config.local_rpc_address, method, params, None, None)

    if result is None:
        result = rpc_call(config, config.remote_rpc_address, method, params, default_result, default_result)

    return result
