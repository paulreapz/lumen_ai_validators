import solana_rpc as rpc
from common import ValidatorConfig, print_json, measurement_from_fields
from monitoring_config import config

def calculate_output_data(config: ValidatorConfig):
    """
    Generate measurement data for Solana validators.

    Args:
        config (ValidatorConfig): Validator configuration containing RPC details.

    Returns:
        list: List of measurements generated from validators data.
    """
    data = rpc.load_solana_validators(config)
    measurements = []

    for info in data:
        measurement = measurement_from_fields("validators", info, {}, config)
        measurements.append(measurement)

    return measurements

# Print the output as JSON
if __name__ == "__main__":
    print_json(calculate_output_data(config))
