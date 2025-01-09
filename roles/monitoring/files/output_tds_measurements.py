from monitoring_config import config
from measurement_tds_info import calculate_output_data
from common import print_json

if __name__ == "__main__":
    """
    Main script to calculate and output TDS measurements as JSON.
    """
    print_json(calculate_output_data(config))
