import time
import solana_rpc as rpc
from common import debug
from common import ValidatorConfig
import statistics
import numpy as np
from common import measurement_from_fields


def get_metrics_from_vote_account_item(item):
    return {
        'epoch_number': item['epochCredits'][-1][0],
        'credits_epoch': item['epochCredits'][-1][1],
        'credits_previous_epoch': item['epochCredits'][-1][2],
        'activated_stake': item['activatedStake'],
        'credits_epoch_delta': item['epochCredits'][-1][1] - item['epochCredits'][-1][2],
        'commission': item['commission']
    }


def find_item_in_vote_accounts_section(identity_account_pubkey, section_parent, section_name):
    if section_name in section_parent:
        section = section_parent[section_name]
        for item in section:
            if item['nodePubkey'] == identity_account_pubkey:
                return get_metrics_from_vote_account_item(item)

    return None


def get_vote_account_metrics(vote_accounts_data, identity_account_pubkey):
    """
    get vote metrics from vote account
    :return:
    voting_status: 0 if validator not found in voting accounts
    voting_status: 1 if validator is current
    voting_status: 2 if validator is delinquent

    """
    result = find_item_in_vote_accounts_section(identity_account_pubkey, vote_accounts_data, 'current')
    if result is not None:
        result.update({'voting_status': 1})
    else:
        result = find_item_in_vote_accounts_section(identity_account_pubkey, vote_accounts_data, 'delinquent')
        if result is not None:
            result.update({'voting_status': 2})
        else:
            result = {'voting_status': 0}
    return result


def get_leader_schedule_metrics(leader_schedule_data, identity_account_pubkey):
    """
    get metrics about leader slots
    """
    if identity_account_pubkey in leader_schedule_data:
        return {"leader_slots_this_epoch": len(leader_schedule_data[identity_account_pubkey])}
    else:
        return {"leader_slots_this_epoch": 0}


def get_block_production_metrics(block_production_data, identity_account_pubkey):
    try:
        item = block_production_data['value']['byIdentity'][identity_account_pubkey]
        return {
            "slots_done": item[0],
            "slots_skipped": item[0] - item[1],
            "blocks_produced": item[1]

        }
    except:
        return {"slots_done": 0, "slots_skipped": 0, "blocks_produced": 0}


def get_block_production_cli_metrics(block_production_data_cli, identity_account_pubkey: str):
    if 'leaders' in block_production_data_cli:
        leaders = block_production_data_cli['leaders']
        skip_rate = []
        my_skip_rate = 0
        for leader in leaders:
            leader_slots = leader.get('leaderSlots', 0)
            if leader_slots > 0:
                current_skip_rate = leader.get('skippedSlots', 0) / leader_slots
                skip_rate.append(current_skip_rate)
                if leader['identityPubkey'] == identity_account_pubkey:
                    my_skip_rate = current_skip_rate

        result = {
            'leader_skip_rate': my_skip_rate,
            'cluster_min_leader_skip_rate': min(skip_rate),
            'cluster_max_leader_skip_rate': max(skip_rate),
            'cluster_mean_leader_skip_rate': statistics.mean(skip_rate),
            'cluster_median_leader_skip_rate': statistics.median(skip_rate),
        }
    else:
        result = {}

    return result


def get_performance_metrics(performance_sample_data, epoch_info_data, leader_schedule_by_identity):
    if len(performance_sample_data) > 0:
        sample = performance_sample_data[0]
        if sample['numSlots'] > 0:
            mid_slot_time = sample['samplePeriodSecs'] / sample['numSlots']
        else:
            mid_slot_time = 0
        current_slot_index = epoch_info_data['slotIndex']
        remaining_time = (epoch_info_data["slotsInEpoch"] - current_slot_index) * mid_slot_time
        epoch_end_time = round(time.time()) + remaining_time
        time_until_next_slot = -1
        if leader_schedule_by_identity is not None:
            for slot in leader_schedule_by_identity:
                if current_slot_index < slot:
                    next_slot = slot
                    time_until_next_slot = (next_slot - current_slot_index) * mid_slot_time
                    break
        else:
            time_until_next_slot = None

        result = {
            "epoch_endtime": epoch_end_time,
            "epoch_remaining_sec": remaining_time
        }

        if time_until_next_slot is not None:
            result.update({"time_until_next_slot": time_until_next_slot})
    else:
        result = {}

    return result


def get_balance_metric(balance_data, key: str):
    if 'value' in balance_data:
        result = {key: balance_data['value']}
    else:
        result = {}

    return result


def get_solana_version_metric(solana_version_data):
    if solana_version_data is not None:
        if 'solana-core' in solana_version_data:
            return {'solana_version': solana_version_data['solana-core']}

    return {}


def get_validators_metric(validators, identity_account_pubkey):
    if validators is not None:
        epoch_credits_l = []
        last_vote_l = []
        root_slot_l = []
        current_last_vote = -1
        current_root_slot = -1

        for v in validators:
            if not v['delinquent']:
                epoch_credits_l.append(v['epochCredits'])
                last_vote_l.append(v['lastVote'])
                root_slot_l.append(v['rootSlot'])
            if identity_account_pubkey == v['identityPubkey']:
                current_last_vote = v['lastVote']
                current_root_slot = v['rootSlot']

        epoch_credits = np.array(epoch_credits_l, dtype=np.int32)
        last_vote = np.array(last_vote_l, dtype=np.int32)
        root_slot = np.array(root_slot_l, dtype=np.int32)

        last_vote = last_vote[last_vote > 0]
        root_slot = root_slot[root_slot > 0]

        cluster_max_last_vote = np.amax(last_vote)
        cluster_min_last_vote = np.amin(last_vote)
        cluster_mean_last_vote = abs((last_vote - cluster_max_last_vote).mean())
        cluster_median_last_vote = abs(np.median(last_vote - cluster_max_last_vote))

        cluster_max_root_slot = np.amax(root_slot)
        cluster_min_root_slot = np.amin(root_slot)
        cluster_mean_root_slot = abs((root_slot - cluster_max_root_slot).mean())
        cluster_median_root_slot = abs(np.median(root_slot - cluster_max_root_slot))

        result = {
            'cluster_mean_epoch_credits': epoch_credits.mean(),
            'cluster_min_epoch_credits': np.amin(epoch_credits),
            'cluster_max_epoch_credits': np.amax(epoch_credits),
            'cluster_median_epoch_credits': np.median(epoch_credits),

            'cluster_max_last_vote': cluster_max_last_vote,
            'cluster_min_last_vote_v2': cluster_min_last_vote,
            'cluster_mean_last_vote_v2': cluster_mean_last_vote,
            'cluster_median_last_vote': cluster_median_last_vote,
            'current_last_vote': current_last_vote,

            'cluster_max_root_slot': cluster_max_root_slot,
            'cluster_min_root_slot_v2': cluster_min_root_slot,
            'cluster_mean_root_slot_v2': cluster_mean_root_slot,
            'cluster_median_root_slot': cluster_median_root_slot,
            'current_root_slot': current_root_slot
        }

    else:
        result = {}

    return result


def get_current_stake_metric(stake_data):
    active = 0
    activating = 0
    deactivating = 0
    active_cnt = 0
    activating_cnt = 0
    deactivating_cnt = 0
    for item in stake_data:
        if 'activeStake' in item:
            active = active + item.get('activeStake', 0)
            active_cnt = active_cnt + 1
        if 'activatingStake' in item:
            activating = activating + item.get('activatingStake', 0)
            activating_cnt = activating_cnt + 1
        if 'deactivatingStake' in item:
            deactivating = deactivating + item.get('deactivatingStake', 0)
            deactivating_cnt = deactivating_cnt + 1

    return {
        'active_stake': active,
        'activating_stake': activating,
        'deactivating_stake': deactivating,
        'stake_holders': len(stake_data),
        'active_cnt': active_cnt,
        'activating_cnt': activating_cnt,
        'deactivating_cnt': deactivating_cnt
    }


def load_data(config: ValidatorConfig):
    identity_account_pubkey = rpc.load_identity_account_pubkey(config)
    vote_account_pubkey = rpc.load_vote_account_pubkey(config)

    epoch_info_data = rpc.load_epoch_info(config)
    block_production_cli = rpc.load_block_production_cli(config)
    performance_sample_data = rpc.load_recent_performance_sample(config)
    solana_version_data = rpc.load_solana_version(config)
    validators_data = rpc.load_solana_validators(config)

    default = []

    identity_account_balance_data = default
    leader_schedule_data = default
    block_production_data = default   

    vote_account_balance_data = default
    vote_accounts_data = default
    stakes_data = default

    if identity_account_pubkey is not None:
        identity_account_balance_data = rpc.load_identity_account_balance(config, identity_account_pubkey)
        leader_schedule_data = rpc.load_leader_schedule(config, identity_account_pubkey)
        block_production_data = rpc.load_block_production(config, identity_account_pubkey)      

    if vote_account_pubkey is not None:
        vote_account_balance_data = rpc.load_vote_account_balance(config, vote_account_pubkey)
        vote_accounts_data = rpc.load_vote_accounts(config, vote_account_pubkey)
        stakes_data = rpc.load_stakes(config, vote_account_pubkey)

    result = {
        'identity_account_pubkey': identity_account_pubkey,
        'vote_account_pubkey': vote_account_pubkey,
        'identity_account_balance': identity_account_balance_data,
        'vote_account_balance': vote_account_balance_data,
        'epoch_info': epoch_info_data,
        'leader_schedule': leader_schedule_data,
        'block_production': block_production_data,
        'load_block_production_cli': block_production_cli,
        'vote_accounts': vote_accounts_data,
        'performance_sample': performance_sample_data,
        'solana_version_data': solana_version_data,
        'stakes_data': stakes_data,
        'validators_data': validators_data,   
        'cpu_model': rpc.load_cpu_model(config)
    }

    debug(config, str(result))

    return result


def calculate_influx_fields(data):
    if data is None:
        result = {"validator_status": 0}
    else:
        identity_account_pubkey = data['identity_account_pubkey']

        vote_account_metrics = get_vote_account_metrics(data['vote_accounts'], identity_account_pubkey)
        leader_schedule_metrics = get_leader_schedule_metrics(data['leader_schedule'], identity_account_pubkey)
        epoch_metrics = data['epoch_info']
        block_production_metrics = get_block_production_metrics(data['block_production'], identity_account_pubkey)
        if identity_account_pubkey in data['leader_schedule']:
            leader_schedule_by_identity = data['leader_schedule'][identity_account_pubkey]
        else:
            leader_schedule_by_identity = None

        performance_metrics = get_performance_metrics(
            data['performance_sample'], epoch_metrics, leader_schedule_by_identity)

        result = {"validator_status": 1}
        result.update(vote_account_metrics)
        result.update(leader_schedule_metrics)
        result.update(epoch_metrics)
        result.update(block_production_metrics)
        result.update(performance_metrics)
        result.update(get_balance_metric(data['identity_account_balance'], 'identity_account_balance'))
        result.update(get_balance_metric(data['vote_account_balance'], 'vote_account_balance'))
        result.update(get_current_stake_metric(data['stakes_data']))
        result.update(get_validators_metric(data['validators_data'], identity_account_pubkey))
        result.update(get_block_production_cli_metrics(data['load_block_production_cli'], identity_account_pubkey))
        result.update({"cpu_model": data['cpu_model']})

    return result


def calculate_output_data(config: ValidatorConfig):
    data = load_data(config)

    tags = {
        "validator_identity_pubkey": data['identity_account_pubkey'],
        "validator_vote_pubkey": data['vote_account_pubkey'],
        "validator_name": config.validator_name,
        "cluster_environment": config.cluster_environment
    }

    legacy_tags = {
        "validator_identity_pubkey": data['identity_account_pubkey'],
        "validator_vote_pubkey": data['vote_account_pubkey'],
        "validator_name": config.validator_name,
    }

    measurement = measurement_from_fields(
        "validators_info",
        calculate_influx_fields(data),
        tags,
        config,
        legacy_tags
    )
    measurement.update({"cpu_model": data['cpu_model']})
    if data is not None and 'solana_version_data' in data:
        measurement.update(get_solana_version_metric(data['solana_version_data']))

    return measurement
