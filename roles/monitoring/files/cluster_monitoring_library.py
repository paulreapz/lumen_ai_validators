import solana_rpc as rpc

def get_apr_from_rewards(rewards_data):
    """
    Extract APR and percent change from rewards data.

    Args:
        rewards_data (dict): Rewards data containing epoch rewards.

    Returns:
        list: A list of dictionaries with 'percent_change' and 'apr' for each epoch reward.
    """
    result = []

    if rewards_data and 'epochRewards' in rewards_data:
        for reward in rewards_data['epochRewards']:
            result.append({
                'percent_change': reward['percentChange'],
                'apr': reward['apr']
            })

    return result

def calc_single_apy(apr, percent_change):
    """
    Calculate APY for a single epoch based on APR and percent change.

    Args:
        apr (float): Annual percentage rate for the epoch.
        percent_change (float): Percent change in the epoch.

    Returns:
        float: Calculated APY for the epoch.
    """
    epoch_count = apr / percent_change
    return ((1 + percent_change / 100) ** epoch_count - 1) * 100

def calc_apy_list_from_apr(apr_per_epoch):
    """
    Calculate a list of APYs from a list of APR values per epoch.

    Args:
        apr_per_epoch (list): List of dictionaries containing 'apr' and 'percent_change'.

    Returns:
        list: List of APY values for each epoch.
    """
    return [calc_single_apy(item['apr'], item['percent_change']) for item in apr_per_epoch]

def process(validators):
    """
    Process a list of validators to calculate APYs based on their rewards data.

    Args:
        validators (list): List of validators with stake account information.

    Returns:
        list: List of lists containing APY values per epoch for each validator.
    """
    data = []

    for validator in validators:
        rewards_data = rpc.load_stake_account_rewards(validator['stake_account'])
        apr_per_epoch = get_apr_from_rewards(rewards_data)
        apy_per_epoch = calc_apy_list_from_apr(apr_per_epoch)
        data.append(apy_per_epoch)

    return data
