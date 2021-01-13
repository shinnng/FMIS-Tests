# -*- coding: utf-8 -*-
import json, rlp
import time
import random
import string
from decimal import Decimal

from hexbytes import HexBytes
from loguru import logger
from typing import List


def decorator_sleep(func):
    def wrap():
        result = func()
        if result is None:
            time.sleep(5)
            result = func()
        return result

    return wrap


def find_proposal(proposal_list, block_number):
    for proposal in proposal_list:
        if proposal_effective(proposal, block_number):
            return proposal


def proposal_list_effective(proposal_list, block_number):
    """
    Determine if there is a proposal in the voting period
    :param proposal_list:
    :param block_number:
    :return:
    """
    for proposal in proposal_list:
        if proposal_effective(proposal, block_number):
            return True
    return False


def proposal_effective(proposal, block_number):
    """
    Determine if the proposal is in the voting period
    :param proposal:
    :param block_number:
    :return:
    """
    if proposal["EndVotingBlock"] > block_number:
        return True
    return False


def get_blockhash(node, blocknumber=None):
    """
    Get block hash based on block height
    :param node:
    :param blocknumber:
    :return:
    """
    if not blocknumber:
        blocknumber = node.block_number
    blockinfo = node.eth.getBlock(blocknumber)
    blockhash = blockinfo.get('hash')
    blockhash = HexBytes(blockhash).hex()
    return blockhash


def int_to_bytes(value):
    return int(value).to_bytes(length=4, byteorder='big', signed=False)


def int16_to_bytes(value):
    return int(value).to_bytes(length=1, byteorder='big', signed=False)


def bytes_to_int(value):
    return int.from_bytes(value, byteorder='big', signed=False)


def get_pledge_list(func, nodeid=None) -> list:
    """
    View the list of specified node IDs
    :param func: Query method, 1. List of current pledge nodes 2,
     the current consensus node list 3, real-time certifier list
    :return:
    """
    validator_info = func().get('Ret')
    if validator_info == "Getting verifierList is failed:The validator is not exist":
        time.sleep(10)
        validator_info = func().get('Ret')
    if validator_info == "Getting candidateList is failed:CandidateList info is not found":
        time.sleep(10)
        validator_info == func().get('Ret')
    if not nodeid:
        validator_list = []
        for info in validator_info:
            validator_list.append(info.get('NodeId'))
        return validator_list
    else:
        for info in validator_info:
            if nodeid == info.get('NodeId'):
                return info.get('RewardPer'), info.get('NextRewardPer')
        raise Exception('Nodeid {} not in the list'.format(nodeid))


def wait_block_number(node, block, interval=1):
    """
    Waiting until the specified block height
    :param node: Node
    :param block: Block height
    :param interval: Block interval, default is 1s
    :return:
    """
    current_block = node.eth.blockNumber
    if 0 < block - current_block <= 10:
        timeout = 10 + int(time.time()) + 50
    elif block - current_block > 10:
        timeout = int((block - current_block) * interval * 1.5) + int(time.time()) + 50
    else:
        logger.info('current block {} is greater than block {}'.format(node.eth.blockNumber, block))
        return
    print_t = 0
    while int(time.time()) < timeout:
        print_t += 1
        if print_t == 10:
            # Print once every 10 seconds to avoid printing too often
            logger.info('The current block height is {}, waiting until {}'.format(node.eth.blockNumber, block))
            print_t = 0
        if node.eth.blockNumber > block:
            return
        time.sleep(1)
    raise Exception("Unable to pop out the block normally, the "
                    "current block height is: {}, the target block height is: {}".format(node.eth.blockNumber, block))


def get_block_count_number(node, number, current_block=None):
    """
    Get the number of verifier blocks
    :param url: node url
    :param cycle: Consensus cycle
    :return:
    """

    current_block = node.eth.blockNumber
    if current_block is None:
        current_block = node.block_number
    count = 0
    for i in range(number - 1):
        nodeid = node.eth.ecrecover(current_block)
        current_block = current_block - 1
        if nodeid == node.node_id:
            count = count + 1
    return count


def random_string(length=10) -> str:
    """
    Randomly generate a string of letters and numbers of a specified length
    :param length:
    :return:
    """
    return ''.join(
        random.choice(
            string.ascii_lowercase
            + string.ascii_uppercase
            + string.digits
        ) for _ in range(length)
    )


def assert_code(result, code):
    '''
    assert the ErrorCode
    :param result:
    :param code:
    :return:
    '''
    if isinstance(result, int):
        assert result == code, "code error，expect：{}，actually:{}".format(code, result)
    else:
        assert result.get('Code') == code, "code error，expect：{}，actually:{}".format(code, result)


def assert_voucher_result(result, status, transaction_type):
    assert int(result['result']) == status, "status error，expect：{}，actually:{}".format(status, result)
    assert int(result['tx_type']) == transaction_type, "status error，expect：{}，actually:{}".format(transaction_type,
                                                                                                   result)


def assert_voucher_staking_result(result, status, transaction_type):
    assert int(result['record_type']) == status, "status error，expect：{}，actually:{}".format(status, result)
    assert int(result['opt_type']) == transaction_type, "status error，expect：{}，actually:{}".format(transaction_type,
                                                                                                    result)


def assert_status(result, status, offline_type):
    assert int(result['status']) == status, "status error，expect：{}，actually:{}".format(status, result)
    assert int(result['offline_type']) == offline_type, "status error，expect：{}，actually:{}".format(offline_type,
                                                                                                    result)


# def assert_zeroOutBlock(result, punishment_amonut, Released):
#     slashing_amount = 0
#     for info in result:
#         assert int(info['slashing_type']) == 1
#         slashing_amount = slashing_amount + int(info['slashing_amount'])
#     assert slashing_amount == punishment_amonut
#     assert int(result[0]['freeze_staking_amount']) == Released
#     assert int(result[0]['staking_amount']) == Released


def von_amount(amonut, base):
    """
    Get von amount
    :param amonut:
    :param base:
    :return:
    """
    return int(Decimal(str(amonut)) * Decimal(str(base)))


def scientific_notation_to_int(value):
    """

    :param value:
    :return:
    """
    return int(Decimal(str(value)))


def get_governable_parameter_value(client_obj, parameter, flag=None):
    """
    Get governable parameter value
    :return:
    """
    # Get governable parameters
    govern_param = client_obj.node.pip.listGovernParam()
    parameter_information = govern_param['Ret']
    for i in parameter_information:
        if i['ParamItem']['Name'] == parameter:
            logger.info("{} ParamValue: {}".format(parameter, i['ParamValue']['Value']))
            logger.info("{} Param old Value: {}".format(parameter, i['ParamValue']['StaleValue']))
            if not flag:
                return i['ParamValue']['Value']
            else:
                return int(i['ParamValue']['Value']), int(i['ParamValue']['StaleValue'])


def get_the_dynamic_parameter_gas_fee(data):
    """
    Get the dynamic parameter gas consumption cost
    :return:
    """
    zero_number = 0
    byte_group_length = len(data)
    for i in data:
        if i == 0:
            zero_number = zero_number + 1
    non_zero_number = byte_group_length - zero_number
    dynamic_gas = non_zero_number * 68 + zero_number * 4
    return dynamic_gas


def get_report_reward(client, penalty_ratio=None, proportion_ratio=None):
    # view Pledge amount
    candidate_info1 = client.node.ppos.getCandidateInfo(client.node.node_id)
    amount = candidate_info1['Ret']['Released']
    if penalty_ratio is None:
        penalty_ratio = client.economic.genesis.economicModel.slashing.slashFractionDuplicateSign
    if proportion_ratio is None:
        proportion_ratio = client.economic.genesis.economicModel.slashing.duplicateSignReportReward
    penalty_reward = int(Decimal(str(amount)) * Decimal(str(penalty_ratio / 10000)))
    proportion_reward = int(Decimal(str(penalty_reward)) * Decimal(str(proportion_ratio / 100)))
    incentive_pool_reward = penalty_reward - proportion_reward
    return penalty_reward, proportion_reward, incentive_pool_reward
