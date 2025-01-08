import solana_rpc as rpc


def get_apr_from_rewards(rewards_data):
    result = []

    if rewards_data is not None:
        if 'epochRewards' in rewards_data:
            epoch_rewards = rewards_data['epochRewards']
            for reward in epoch_rewards:
                result.append({
                    'percent_change': reward['percentChange'],
                    'apr': reward['apr']
                })

    return result


def calc_single_apy(apr, percent_change):
    epoch_count = apr / percent_change
    result = ((1 + percent_change / 100) ** epoch_count - 1) * 100
    return result


def calc_apy_list_from_apr(apr_per_epoch):
    l_apy = []

    for item in apr_per_epoch:
        apy = calc_single_apy(item['apr'], item['percent_change'])
        l_apy.append(apy)

    return l_apy


def process(validators):

    data = []

    for validator in validators:
        rewards_data = rpc.load_stake_account_rewards(validator['stake_account'])
        apr_per_epoch = get_apr_from_rewards(rewards_data)
        apy_per_epoch = calc_apy_list_from_apr(apr_per_epoch)
        data.append(apy_per_epoch)

    return data
