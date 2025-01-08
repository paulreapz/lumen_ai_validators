import solana_rpc as rpc
from common import ValidatorConfig
from common import print_json
from common import measurement_from_fields
from monitoring_config import config


def calculate_output_data(config: ValidatorConfig):

    data = rpc.load_solana_gossip(config)

    measurements = []

    for gossip in data:
        measurement = measurement_from_fields("gossip", gossip, config)
        measurements.append(measurement)

    return measurements


print_json(calculate_output_data(config))

