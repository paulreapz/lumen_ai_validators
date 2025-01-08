import solana_rpc as rpc
from common import ValidatorConfig
from common import print_json
from common import measurement_from_fields
from monitoring_config import config


def calculate_output_data(config: ValidatorConfig):

    data = rpc.load_solana_validators(config)

    measurements = []

    for info in data:
        measurement = measurement_from_fields("validators", info, config)
        measurements.append(measurement)

    return measurements


print_json(calculate_output_data(config))

