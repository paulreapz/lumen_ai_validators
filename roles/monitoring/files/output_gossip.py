import solana_rpc as rpc
from common import ValidatorConfig, print_json, measurement_from_fields
from monitoring_config import config

def calculate_output_data(config: ValidatorConfig):
    """
    Generate measurement data for Solana gossip information.

    Args:
        config (ValidatorConfig): Validator configuration containing RPC details.

    Returns:
        list: List of measurements generated from gossip data.
    """
    data = rpc.load_solana_gossip(config)
    measurements = []

    for gossip in data:
        measurement = measurement_from_fields("gossip", gossip, {}, config)
        measurements.append(measurement)

    return measurements

# Print the output as JSON
if __name__ == "__main__":
    print_json(calculate_output_data(config))
