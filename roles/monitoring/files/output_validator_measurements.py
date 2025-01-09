from monitoring_config import config
from measurement_validator_info import calculate_output_data
from common import print_json

if __name__ == "__main__":
    """
    Main script to calculate and output validator measurements as JSON.
    """
    print_json(calculate_output_data(config))
