from monitoring_config import config
from measurement_validator_info import calculate_output_data
from common import print_json

print_json(calculate_output_data(config))

