from pprint import pprint
import json
import numpy
import time


class ValidatorConfig:
    """
    Configuration class for a validator, storing essential parameters.
    """
    def __init__(self,
                 validator_name: str,
                 secrets_path: str,
                 local_rpc_address: str,
                 remote_rpc_address: str,
                 cluster_environment: str,
                 debug_mode: bool):
        self.validator_name = validator_name
        self.secrets_path = secrets_path
        self.local_rpc_address = local_rpc_address
        self.remote_rpc_address = remote_rpc_address
        self.cluster_environment = cluster_environment
        self.debug_mode = debug_mode


class JsonEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle numpy data types and structures.
    """
    def default(self, obj):
        if isinstance(obj, (numpy.int_, numpy.intc, numpy.intp, numpy.int8,
                            numpy.int16, numpy.int32, numpy.int64, numpy.uint8,
                            numpy.uint16, numpy.uint32, numpy.uint64)):
            return int(obj)
        elif isinstance(obj, (numpy.float_, numpy.float16, numpy.float32,
                              numpy.float64)):
            return float(obj)
        elif isinstance(obj, (numpy.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def debug(config: ValidatorConfig, data):
    """
    Prints debug information if debug mode is enabled in the configuration.

    Args:
        config (ValidatorConfig): The validator configuration.
        data: Data to be printed for debugging.
    """
    if config.debug_mode:
        pprint(data)


def print_json(data):
    """
    Prints a Python object as a JSON string using the custom encoder.

    Args:
        data: Data to be printed in JSON format.
    """
    print(json.dumps(data, cls=JsonEncoder))


def measurement_from_fields(name, data, tags, config, legacy_tags=None):
    """
    Constructs a measurement dictionary for monitoring purposes.

    Args:
        name (str): Name of the measurement.
        data (dict): Field data for the measurement.
        tags (dict): Tags associated with the measurement.
        config (ValidatorConfig): Validator configuration.
        legacy_tags (dict, optional): Additional legacy tags to include.

    Returns:
        dict: Constructed measurement dictionary.
    """
    if legacy_tags is None:
        legacy_tags = {}

    # Add cluster environment data
    data.update({"cluster_environment": config.cluster_environment})

    # Base measurement structure
    measurement = {
        "measurement": name,
        "time": round(time.time() * 1000),
        "monitoring_version": "3.2.0",
        "cluster_environment": config.cluster_environment,
        "fields": data,
        "tags": tags
    }

    # Include legacy tags
    measurement.update(legacy_tags)

    return measurement