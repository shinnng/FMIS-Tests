import math
import time
from decimal import Decimal

from cases.chain.conftest import withdrew_staking_all
from lib.chain.utils import assert_code, assert_voucher_result, assert_voucher_staking_result, assert_status
from loguru import logger


def hes_staking(client):
    """
    质押分红比例为10%的节点犹豫期查看节点信息状态
    """
    assert_code(client.staking_result, 0)
    result = client.tidb.tb_tx_ori_voucher(client.staking_hash)
    assert_voucher_result(result, 1, 1000)
    result = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, client.staking_address)
    assert_voucher_staking_result(result, 2, 4)


def test_hes_staking(staking_client):
    """
    质押分红比例为10%的节点犹豫期查看节点信息状态
    """
    client = staking_client
    hes_staking(client)


def test_Hes_withdrew_staking(noconsensus_client_unanalyze):
    """
    犹豫期并退出查看节点信息状态
    """
    client = noconsensus_client_unanalyze
    amount = client.economic.create_staking_limit * 2
    address, _ = client.account.generate_account(client.node.web3, amount)
    logger.info("address {} balance: {}".format(address, client.node.eth.getBalance(address)))
    tx_hash = client.builtin_rpc.create_staking(0, address, address, reward_per=1000)
    logger.info("create staking hash : {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1000)
    staking_status = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, address)
    assert_voucher_staking_result(staking_status, 2, 4)
    client.assert_balance(address)

    tx_hash = client.builtin_rpc.withdrew_staking(address)
    logger.info("withdrew staking hash : {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)

    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1003)
    result = client.tidb.tb_tx_ori_voucher_unstaking_attach(client.node.node_id, address)
    assert int(result['free_unstaking_amount']) == client.economic.create_staking_limit
    client.assert_balance(address)


def assert_hes_delegate(client):
    assert_code(client.staking_result, 0)
    result = client.tidb.tb_tx_ori_voucher(client.staking_hash)
    assert_voucher_result(result, 1, 1000)
    result = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, client.staking_address)
    assert_voucher_staking_result(result, 2, 4)

    amount = client.economic.delegate_limit * 2
    delegate_address, _ = client.account.generate_account(client.node.web3, amount)
    tx_hash = client.builtin_rpc.delegate(0, delegate_address)
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    logger.info("create delegate hash : {}".format(tx_hash))
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1004)
    staking_status = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, delegate_address)
    assert_voucher_staking_result(staking_status, 1, 4)
    client.assert_balance(delegate_address)
    return delegate_address


def test_Hes_delegate(staking_client):
    """
    犹豫期并委托节点信息状态
    """
    client = staking_client
    assert_hes_delegate(client)


def test_Hes_withdrew_delegate(staking_client):
    """
    犹豫期委托节点又赎回委托信息状态
    """
    client = staking_client
    delegate_address, staking_detail = assert_hes_delegate(client)
    staking_number = client.builtin_rpc.staking_block_number()
    tx_hash = client.builtin_rpc.withdrew_delegate(staking_number, delegate_address)
    logger.info("withdrew delegate hash : {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1005)
    result = client.tidb.tb_tx_ori_voucher_undelegation_attach(client.node.node_id, delegate_address)
    assert int(result['free_unlock_staking_amount']) == client.economic.delegate_limit
    client.assert_balance(delegate_address)


def test_Hes_delegate_withdrew_staking(staking_client):
    """
    犹豫期并委托节点又退回质押信息状态
    """
    client = staking_client
    assert_hes_delegate(client)
    staking_address = client.staking_address
    tx_hash = client.builtin_rpc.withdrew_staking(staking_address)
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    logger.info("withdrew staking hash : {}".format(tx_hash))
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1003)
    result = client.tidb.tb_tx_ori_voucher_unstaking_attach(client.node.node_id, staking_address)
    assert int(result['free_unstaking_amount']) == client.economic.create_staking_limit
    client.assert_balance(staking_address)


def test_lock_staking(staking_client):
    """
    锁定期无委托查看信息状态
    """
    client = staking_client
    hes_staking(client)
    client.economic.wait_settlement_blocknum()
    time.sleep(2)
    result = client.node.ppos.getCandidateInfo(client.node.node_id)
    print("CandidateInfo", result)
    result = client.node.ppos.getCandidateList()
    print("CandidateList", result)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['valid_staking_balance_amount']) == client.economic.create_staking_limit
    result = client.tidb.tb_staking_lock_ori_voucher(client.node.node_id, client.staking_address)
    assert int(result['staking_lock_amount']) == client.economic.create_staking_limit
    client.assert_balance(staking_client.staking_address)


def test_lock_increase_staking(staking_client):
    """
    锁定期增持质押查看信息状态
    """
    client = staking_client
    hes_staking(client)
    client.economic.wait_settlement_blocknum()
    tx_hash = client.builtin_rpc.increase_staking(0, staking_client.staking_address)
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    logger.info("increase staking hash : {}".format(tx_hash))
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1002)
    staking_detail = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, client.staking_address)
    assert_voucher_staking_result(staking_detail, 2, 1)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['hesitating_staking_balance_amount']) == client.economic.add_staking_limit
    assert int(result['valid_staking_balance_amount']) == client.economic.create_staking_limit
    client.economic.wait_settlement_blocknum()
    client.economic.wait_consensus_blocknum()
    client.assert_balance(client.staking_address)


def test_lock_withdrew_staking(staking_client):
    """
    锁定期退回质押查看信息状态
    """
    client = staking_client
    node_id = client.node.node_id
    staking_address = client.staking_address
    client.economic.wait_settlement_blocknum()
    tx_hash = client.builtin_rpc.withdrew_staking(client.staking_address)
    logger.info("withdrew staking tx hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    logger.info("withdrew staking hash : {}".format(tx_hash))
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1003)
    unstaking_detail = client.tidb.tb_tx_ori_voucher_unstaking_attach(client.node.node_id, client.staking_address)
    assert int(unstaking_detail['freeze_staking_amount']) == client.economic.create_staking_limit
    print(client.node.ppos.getCandidateInfo(client.node.node_id))
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 3)
    assert int(result['offline_type']) == 3
    assert int(result['valid_staking_balance_amount']) == client.economic.create_staking_limit
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    print(client.node.ppos.getCandidateInfo(client.node.node_id))
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 2, 3)
    assert int(result['offline_type']) == 3
    assert int(result['valid_staking_balance_amount']) == client.economic.create_staking_limit
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    print(client.node.ppos.getCandidateInfo(client.node.node_id))
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 2, 3)
    assert int(result['offline_type']) == 3
    assert int(result['valid_staking_balance_amount']) == client.economic.create_staking_limit
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    print(client.node.ppos.getCandidateInfo(client.node.node_id))
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 2, 3)
    assert int(result['offline_type']) == 3
    assert int(result['valid_staking_balance_amount']) == 0
    result = client.tidb.tb_unfreeze_staking_ori_voucher(node_id, staking_address)
    assert int(result['freeze_staking_amount']) == client.economic.create_staking_limit
    assert int(result['return_free_amount']) == client.economic.create_staking_limit
    client.assert_balance(staking_address)


def hes_increase_staking(client):
    hes_staking(client)
    tx_hash = client.builtin_rpc.increase_staking(0, client.staking_address)
    logger.info("withdrew staking tx hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(3)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1002)
    result = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, client.staking_address)
    assert_voucher_staking_result(result, 2, 1)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['hesitating_staking_balance_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit


def test_Hes_increase_staking(staking_client):
    """
    犹豫期增持质押等待一个结算期查看节点信息状态
    """
    client = staking_client
    hes_increase_staking(client)
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['valid_staking_balance_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit
    client.assert_balance(client.staking_address)


def test_Hes_increase_lock_increase(staking_client):
    """
    犹豫期增持质押等待一个结算期增持质押查看节点信息状态
    """
    client = staking_client
    hes_increase_staking(client)
    client.economic.wait_settlement_blocknum()
    tx_hash = client.builtin_rpc.increase_staking(0, client.staking_address)
    logger.info("withdrew staking tx hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1002)
    result = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, client.staking_address)
    assert_voucher_staking_result(result, 2, 1)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['hesitating_staking_balance_amount']) == client.economic.add_staking_limit
    assert int(result['valid_staking_balance_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit


def test_Hes_increase_lock_withdrew(staking_client):
    """
    犹豫期增持质押等待一个结算期退出质押查看节点信息状态
    """
    client = staking_client
    hes_increase_staking(client)
    client.economic.wait_settlement_blocknum()
    tx_hash = client.builtin_rpc.increase_staking(0, client.staking_address)
    logger.info("withdrew staking tx hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1002)
    result = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, client.staking_address)
    assert_voucher_staking_result(result, 2, 1)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['hesitating_staking_balance_amount']) == client.economic.add_staking_limit
    assert int(result[
                   'valid_staking_balance_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit

    tx_hash = client.builtin_rpc.withdrew_staking(client.staking_address)
    logger.info("withdrew staking tx hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    logger.info("withdrew staking hash : {}".format(tx_hash))
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1003)
    print(client.node.ppos.getCandidateInfo(client.node.node_id))
    unstaking_detail = client.tidb.tb_tx_ori_voucher_unstaking_attach(client.node.node_id, client.staking_address)
    assert int(unstaking_detail[
                   'freeze_staking_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit
    print(client.node.ppos.getCandidateInfo(client.node.node_id))
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 3)
    assert int(result['offline_type']) == 3
    assert int(result[
                   'valid_staking_balance_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit
    assert int(result['hesitating_staking_balance_amount']) == 0
    client.assert_balance(client.staking_address)


def het_increase_delegate(client):
    hes_increase_staking(client)
    amount = client.economic.delegate_limit * 4
    address, _ = client.account.generate_account(client.node.web3, amount)
    tx_hash = client.builtin_rpc.delegate(0, address)
    logger.info("delegate tx hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1004)
    result = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, address)
    assert_voucher_staking_result(result, 1, 4)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['hesitating_staking_balance_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit
    assert int(result['hesitating_delegation_balance_amount']) == client.economic.delegate_limit
    return address


def test_Hes_increase_delegate(staking_client):
    """
    犹豫期增持质押且被委托等待一个结算期查看节点信息状态
    """
    client = staking_client
    delegate_address = het_increase_delegate(client)
    client.economic.wait_settlement_blocknum()
    time.sleep(2)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['valid_staking_balance_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit
    assert int(result['valid_delegation_balance_amount']) == client.economic.delegate_limit
    result = client.tidb.tb_delegate_lock_ori_voucher(client.node.node_id, delegate_address)
    assert int(result['delegation_lock_amount']) == client.economic.delegate_limit
    client.assert_balance(delegate_address)


def test_Hes_increase_delegate_lock_withdrew_delegate(staking_client):
    """
    犹豫期增持质押且被委托等待一个结算期查看节点信息状态
    """
    client = staking_client
    delegate_address = het_increase_delegate(client)
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    result = client.tidb.tb_staking_lock_ori_voucher(client.node.node_id, client.staking_address)
    assert int(
        result['staking_lock_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit
    result = client.tidb.tb_delegate_lock_ori_voucher(client.node.node_id, delegate_address)
    assert int(result['delegation_lock_amount']) == client.economic.delegate_limit
    staking_number = client.builtin_rpc.staking_block_number(client.node)
    tx_hash = client.builtin_rpc.withdrew_delegate(staking_number, delegate_address)
    logger.info("withdrew delegate tx hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['valid_delegation_balance_amount']) == 0
    assert int(result['hesitating_delegation_balance_amount']) == 0
    client.assert_balance(delegate_address)


def test_Hes_increase_delegate_lock_withdrew_staking(staking_client):
    """
    犹豫期增持质押且被委托等待一个结算期查看节点信息状态
    """
    client = staking_client
    delegate_address = het_increase_delegate(client)
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    result = client.tidb.tb_staking_lock_ori_voucher(client.node.node_id, client.staking_address)
    assert int(
        result['staking_lock_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit
    result = client.tidb.tb_delegate_lock_ori_voucher(client.node.node_id, delegate_address)
    assert int(result['delegation_lock_amount']) == client.economic.delegate_limit
    tx_hash = client.builtin_rpc.withdrew_staking(client.staking_address)
    logger.info("withdrew staking delegate tx hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(1)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1003)
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 2, 3)
    client.assert_balance(delegate_address)


def test_delegate_more(staking_client):
    """
    犹豫期多人委托，锁定期查看信息状态
    """
    client = staking_client
    hes_increase_staking(client)
    amount = client.economic.delegate_limit * 2
    first_ddress, _ = client.account.generate_account(client.node.web3, amount)
    second_address, _ = client.account.generate_account(client.node.web3, amount)
    tx_hash = client.builtin_rpc.delegate(0, first_ddress)
    logger.info("first_ddress delegate tx hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1004)
    result = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, first_ddress)
    assert_voucher_staking_result(result, 1, 4)
    tx_hash = client.builtin_rpc.delegate(0, second_address)
    logger.info("second_address delegate tx hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1004)
    result = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, first_ddress)
    assert_voucher_staking_result(result, 1, 4)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['hesitating_delegation_balance_amount']) == client.economic.delegate_limit * 2
    assert int(result[
                   'hesitating_staking_balance_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['valid_delegation_balance_amount']) == client.economic.delegate_limit * 2
    assert int(result[
                   'valid_staking_balance_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit
    client.assert_balance(first_ddress)
    client.assert_balance(second_address)


def test_withdraw_delegate_reward(staking_client):
    """
    犹豫期委托，夸结算周期领取委托分红查看信息状态
    """
    client = staking_client
    delegate_address = het_increase_delegate(client)
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    candidate_info = client.node.ppos.getCandidateInfo(client.node.node_id)
    logger.info("candidate info: {}".format(candidate_info))
    result = client.tidb.tb_staking_lock_ori_voucher(client.node.node_id, client.staking_address)
    assert int(
        result['staking_lock_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit
    result = client.tidb.tb_delegate_lock_ori_voucher(client.node.node_id, delegate_address)
    assert int(result['delegation_lock_amount']) == client.economic.delegate_limit
    block_reward, staking_reward = client.economic.get_current_year_reward()
    logger.info("block_reward: {} staking_reward: {}".format(block_reward, staking_reward))
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    candidate_info = client.node.ppos.getCandidateInfo(client.node.node_id)['Ret']
    logger.info("candidate info: {}".format(candidate_info))
    staking_blocknum = client.builtin_rpc.staking_block_number()
    delegation_info = client.node.ppos.getDelegateInfo(staking_blocknum, delegate_address, client.node.node_id)
    logger.info("delegation info: {}".format(delegation_info))
    delegate_reward = client.node.ppos.getDelegateReward(delegate_address)
    logger.info("delegate reward: {}".format(delegate_reward))
    staking_delegation_reward = int(Decimal(str(staking_reward)) * Decimal(str(candidate_info["RewardPer"] / 10000)))
    logger.info("staking delegation reward: {}".format(staking_delegation_reward))
    block_delegation_reward = Decimal(str(candidate_info['DelegateRewardTotal'])) - Decimal(
        str(staking_delegation_reward))
    logger.info("block delegation reward: {}".format(block_delegation_reward))
    block_reward, staking_reward = client.economic.get_current_year_reward()
    logger.info("block_reward: {} staking_reward: {}".format(block_reward, staking_reward))
    reward_result = client.tidb.tb_reward_alloc_ori_voucher(client.node.node_id, delegate_address)
    assert int(reward_result['reward_amount']) == staking_delegation_reward
    assert int(reward_result['node_reward_amount']) == block_delegation_reward

    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    # assert int(result['total_delegation_reward']) == block_reward
    # assert int(result['total_staking_delegation_reward']) == 0
    # assert int(result['total_block_delegation_reward']) == block_reward
    # assert int(result['current_epoch_delegation_block_reward']) == block_reward
    assert int(result['reward_delegation_percent']) == candidate_info['RewardPer']
    assert int(result['next_reward_delegation_percent']) == candidate_info['NextRewardPer']

    tx_hash = client.builtin_rpc.withdraw_delegate_reward(delegate_address)
    logger.info("withdraw delegate reward tx hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 5000)
    result = client.tidb.tb_tx_ori_voucher_receive_delegate_reward_attach(client.node.node_id, delegate_address)
    # assert int(result['block_reward_amount']) == block_delegation_reward
    # assert int(result['staking_reward_amount']) == staking_delegation_reward
    assert int(result['total_reward_amount']) == candidate_info['DelegateRewardTotal']
    client.assert_balance(delegate_address)


def delegate_staking(client, RewardPer=0):
    staking_amount = client.economic.create_staking_limit * 3
    delegate_amount = client.economic.delegate_limit * 4
    staking_address, _ = client.account.generate_account(client.node.web3, staking_amount)
    delegate_address, _ = client.account.generate_account(client.node.web3, delegate_amount)
    tx_hash = client.builtin_rpc.create_staking(0, staking_address, staking_address,
                                                amount=client.economic.create_staking_limit * 2, reward_per=RewardPer)
    logger.info("transaction hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(1)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1000)
    tx_hash = client.builtin_rpc.delegate(0, delegate_address)
    logger.info("delegate1 transaction hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(1)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1004)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['hesitating_staking_balance_amount']) == client.economic.create_staking_limit * 2
    assert int(result['hesitating_delegation_balance_amount']) == client.economic.delegate_limit
    return delegate_address


def test_zero_delegate(noconsensus_client_unanalyze, unstaking):
    """
    质押分红比例0%被委托，等待结算周期查看分红信息状态
    """
    client = noconsensus_client_unanalyze
    delegate_address = delegate_staking(client)
    client.economic.wait_settlement_blocknum()
    time.sleep(2)
    result = client.tidb.tb_node(client.node.node_id)
    assert int(result['valid_staking_balance_amount']) == client.economic.create_staking_limit * 2
    assert int(result['valid_delegation_balance_amount']) == client.economic.delegate_limit
    result = client.tidb.tb_staking_lock_ori_voucher(client.node.node_id, client.staking_address)
    assert int(result['staking_lock_amount']) == client.economic.create_staking_limit * 2
    result = client.tidb.tb_delegate_lock_ori_voucher(client.node.node_id, delegate_address)
    assert int(result['delegation_lock_amount']) == client.economic.delegate_limit
    client.economic.wait_settlement_blocknum()
    time.sleep(2)
    reward_result = client.tidb.tb_reward_alloc_ori_voucher(client.node.node_id, delegate_address)
    assert int(reward_result['reward_amount']) == 0
    assert int(reward_result['node_reward_amount']) == 0
    client.assert_balance(delegate_address)


def test_redeem_all_orders(staking_client):
    """
    赎回全部委托查看分红奖励
    :param staking_client:
    :return:
    """
    client = staking_client
    delegate_address = het_increase_delegate(client)
    client.economic.wait_settlement_blocknum()
    time.sleep(2)
    block_reward, staking_reward = client.economic.get_current_year_reward()
    logger.info("block_reward: {} staking_reward: {}".format(block_reward, staking_reward))
    block_number = client.builtin_rpc.staking_block_number()
    client.economic.wait_settlement_blocknum()
    time.sleep(2)
    candidate_info = client.node.ppos.getCandidateInfo(client.node.node_id)['Ret']
    logger.info(candidate_info)
    staking_delegation_reward = int(Decimal(str(staking_reward)) * Decimal(str(candidate_info["RewardPer"] / 10000)))
    logger.info("staking delegation reward: {}".format(staking_delegation_reward))
    block_delegation_reward = Decimal(str(candidate_info['DelegateRewardTotal'])) - Decimal(
        str(staking_delegation_reward))
    logger.info("block delegation reward: {}".format(block_delegation_reward))
    reward_result = client.tidb.tb_reward_alloc_ori_voucher(client.node.node_id, delegate_address)
    assert int(reward_result['reward_amount']) == staking_delegation_reward
    assert int(reward_result['node_reward_amount']) == block_delegation_reward
    tx_hash = client.builtin_rpc.withdrew_delegate(block_number, delegate_address)
    logger.info("transaction hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1005)
    result = client.tidb.tb_tx_ori_voucher_undelegation_attach(client.node.node_id, delegate_address)
    assert int(result['free_locked_delegate_amount']) == client.economic.delegate_limit
    assert int(result['refund_block_reward_amount']) == block_delegation_reward
    assert int(result['refund_staking_reward_amount']) == staking_delegation_reward
    client.assert_balance(delegate_address)


def test_delegating_multiple_nodes(noconsensus_clients_unanalyze, unstaking_all):
    """
    委托多个节点，跨结算周期赎回其中一个节点委托，查看分红奖励
    :param noconsensus_clients_unanalyze:
    :return:
    """
    client1 = noconsensus_clients_unanalyze[0]
    client2 = noconsensus_clients_unanalyze[1]
    delegate_address = delegate_staking(client1, RewardPer=1000)
    staking_amount = client2.economic.create_staking_limit * 3
    staking_address, _ = client2.account.generate_account(client2.node.web3, staking_amount)
    tx_hash = client2.builtin_rpc.create_staking(0, staking_address, staking_address,
                                                 amount=client2.economic.create_staking_limit * 2, reward_per=2000)
    logger.info("create staking transaction hash: {}".format(tx_hash))
    result = client2.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    tx_hash = client2.builtin_rpc.delegate(0, delegate_address)
    logger.info("delegate2 transaction hash: {}".format(tx_hash))
    result = client2.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    client1.economic.wait_settlement_blocknum()
    time.sleep(2)

    candidate_info1 = client1.node.ppos.getCandidateInfo(client1.node.node_id)['Ret']
    logger.info(candidate_info1)
    candidate_info2 = client2.node.ppos.getCandidateInfo(client2.node.node_id)['Ret']
    logger.info(candidate_info2)
    block_reward, staking_reward = client1.economic.get_current_year_reward()
    logger.info("block_reward: {} staking_reward: {}".format(block_reward, staking_reward))
    block_number = client1.builtin_rpc.staking_block_number()
    client1.economic.wait_settlement_blocknum()
    time.sleep(2)

    candidate_info1 = client1.node.ppos.getCandidateInfo(client1.node.node_id)['Ret']
    logger.info(candidate_info1)
    candidate_info2 = client2.node.ppos.getCandidateInfo(client2.node.node_id)['Ret']
    logger.info(candidate_info2)
    staking_delegation_reward1 = int(Decimal(str(staking_reward)) * Decimal(str(candidate_info1["RewardPer"] / 10000)))
    logger.info("staking delegation reward: {}".format(staking_delegation_reward1))
    block_delegation_reward1 = Decimal(str(candidate_info1['DelegateRewardTotal'])) - Decimal(
        str(staking_delegation_reward1))
    logger.info("block delegation reward: {}".format(block_delegation_reward1))
    staking_delegation_reward2 = int(Decimal(str(staking_reward)) * Decimal(str(candidate_info2["RewardPer"] / 10000)))
    logger.info("staking delegation reward: {}".format(staking_delegation_reward2))
    block_delegation_reward2 = Decimal(str(candidate_info2['DelegateRewardTotal'])) - Decimal(
        str(staking_delegation_reward2))
    logger.info("block delegation reward: {}".format(block_delegation_reward2))

    reward_result = client1.tidb.tb_reward_alloc_ori_voucher(client1.node.node_id, delegate_address)
    assert int(reward_result['reward_amount']) == staking_delegation_reward1
    assert int(reward_result['node_reward_amount']) == block_delegation_reward1
    reward_result = client2.tidb.tb_reward_alloc_ori_voucher(client2.node.node_id, delegate_address)
    assert int(reward_result['reward_amount']) == staking_delegation_reward2
    assert int(reward_result['node_reward_amount']) == block_delegation_reward2

    tx_hash = client1.builtin_rpc.withdrew_delegate(block_number, delegate_address)
    logger.info("transaction hash: {}".format(tx_hash))
    result = client1.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)

    result = client1.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1005)
    result = client1.tidb.tb_tx_ori_voucher_undelegation_attach(client1.node.node_id, delegate_address)
    assert int(result['free_locked_delegate_amount']) == client1.economic.delegate_limit
    assert int(result['refund_block_reward_amount']) == block_delegation_reward1
    assert int(result['refund_staking_reward_amount']) == staking_delegation_reward1
    client1.assert_balance(delegate_address)


def test_one_node_multiple_delegates(staking_client):
    """
    一个节点被多个委托，查看分红奖励
    :param staking_client:
    :return:
    """
    client = staking_client
    delegate_address1 = het_increase_delegate(client)
    delegate_amount = client.economic.delegate_limit * 3
    delegate_address2, _ = client.account.generate_account(client.node.web3, delegate_amount)
    tx_hash = client.builtin_rpc.delegate(0, delegate_address2, amount=client.economic.delegate_limit * 2)
    logger.info("delegate transaction hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    client.economic.wait_settlement_blocknum()
    time.sleep(2)

    candidate_info = client.node.ppos.getCandidateInfo(client.node.node_id)['Ret']
    logger.info(candidate_info)
    block_reward, staking_reward = client.economic.get_current_year_reward()
    logger.info("block_reward: {} staking_reward: {}".format(block_reward, staking_reward))
    client.economic.wait_settlement_blocknum()
    time.sleep(2)

    candidate_info = client.node.ppos.getCandidateInfo(client.node.node_id)['Ret']
    logger.info(candidate_info)
    staking_reward_total = int(Decimal(str(staking_reward)) * Decimal(str(candidate_info["RewardPer"] / 10000)))
    logger.info("staking delegation reward: {}".format(staking_reward_total))
    block_reward_total = Decimal(str(candidate_info['DelegateRewardTotal'])) - Decimal(str(staking_reward_total))
    logger.info("block delegation reward: {}".format(block_reward_total))

    staking_delegation_reward1 = math.floor(
        Decimal(str(staking_reward_total)) * Decimal(str(client.economic.delegate_limit)) / Decimal(
            str(client.economic.delegate_limit * 3)))
    logger.info("staking1 delegation reward: {}".format(staking_delegation_reward1))
    block_delegation_reward1 = math.floor(
        Decimal(str(block_reward_total)) * Decimal(str(client.economic.delegate_limit)) / Decimal(
            str(client.economic.delegate_limit * 3)))
    logger.info("block1 delegation reward: {}".format(block_delegation_reward1))

    staking_delegation_reward2 = math.floor(
        Decimal(str(staking_reward_total)) * Decimal(str(client.economic.delegate_limit * 2)) / Decimal(
            str(client.economic.delegate_limit * 3)))
    logger.info("staking2 delegation reward: {}".format(staking_delegation_reward2))
    block_delegation_reward2 = math.floor(
        Decimal(str(block_reward_total)) * Decimal(str(client.economic.delegate_limit * 2)) / Decimal(
            str(client.economic.delegate_limit * 3)))
    logger.info("block2 delegation reward: {}".format(block_delegation_reward2))

    reward_result = client.tidb.tb_reward_alloc_ori_voucher(client.node.node_id, delegate_address1)
    assert int(reward_result['reward_amount']) == staking_delegation_reward1
    assert int(reward_result['node_reward_amount']) == block_delegation_reward1
    reward_result = client.tidb.tb_reward_alloc_ori_voucher(client.node.node_id, delegate_address2)
    assert int(reward_result['reward_amount']) == staking_delegation_reward2
    assert int(reward_result['node_reward_amount']) == block_delegation_reward2

    tx_hash = client.builtin_rpc.withdraw_delegate_reward(delegate_address1)
    logger.info("withdraw delegate reward transaction hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 5000)
    tx_hash = client.builtin_rpc.withdrew_delegate(candidate_info['StakingBlockNum'], delegate_address2, amount=client.economic.delegate_limit * 2)
    logger.info("withdraw delegate transaction hash: {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1005)

    result = client.tidb.tb_tx_ori_voucher_receive_delegate_reward_attach(client.node.node_id, delegate_address1)
    assert int(result['total_reward_amount']) == staking_delegation_reward1 + block_delegation_reward1
    result = client.tidb.tb_tx_ori_voucher_undelegation_attach(client.node.node_id, delegate_address2)
    print(result)
    assert int(result['refund_staking_reward_amount']) == staking_delegation_reward2
    assert int(result['refund_block_reward_amount']) == block_delegation_reward2


def test_sd(consensus_client):
    # noconsensus_clients = global_test_clients[1]
    # withdrew_staking_all(noconsensus_clients)
    print(consensus_client.node.ppos.getCandidateInfo('4cc7be9ec01466fc4f14365f6700da36f3eb157473047f32bded7b1c0c00955979a07a8914895f7ee59af9cb1e6b638aa57c91a918f7a84633a92074f286b208'))


def block_reward_total(block_reward, blocknum):
    block_reward_total = math.ceil(Decimal(str(block_reward)) * blocknum)
    delegate_block_reward = 0
    i = 0
    for i in range(blocknum):
        delegate_block = int(Decimal(str(block_reward)) * Decimal(str(10 / 100)))
        delegate_block_reward = delegate_block_reward + delegate_block
        i = i + 1
    node_block_reward = block_reward_total - delegate_block_reward
    print("统计次数 {}".format(i))
    print("节点出块奖励为{}".format(node_block_reward))
    print("委托出块奖励为{}".format(delegate_block_reward))
    return block_reward_total, node_block_reward, delegate_block_reward


def test_sss(noconsensus_client):
    """

    """
    client = noconsensus_client
    economic = client.economic
    node = client.node
    address, _ = client.account.generate_account(node.web3, economic.create_staking_limit * 2)
    print("创建的质押地址为{}".format(address))
    benifit_address, _ = client.account.generate_account(node.web3, 0)
    print("创建的收益地址为{}".format(benifit_address))
    delegate_address, _ = client.account.generate_account(node.web3, economic.delegate_limit * 2)
    print("创建的委托地址为{}".format(delegate_address))
    result = client.builtin_rpc.create_staking(0, benifit_address, address, reward_per=1000)
    assert_code(result, 0)
    result = client.builtin_rpc.delegate(0, delegate_address)
    assert_code(result, 0)
    economic.wait_settlement_blocknum()
    economic.wait_consensus_blocknum()
    result = client.builtin_rpc.withdrew_staking(client.staking_address)
    assert_code(result, 0)
    first_block_reward, first_staking_reward = economic.get_current_year_reward()
    print("第一个结算周期节点出块奖励为{},节点质押奖励为{}".format(first_block_reward, first_staking_reward))
    economic.wait_settlement_blocknum()
    economic.wait_consensus_blocknum()
    second_block_reward, second_staking_reward = economic.get_current_year_reward()
    print("第二个结算周期节点出块奖励为{},节点质押奖励为{}".format(second_block_reward, second_staking_reward))

    first_settlement_block = economic.get_settlement_switchpoint() - economic.settlement_size
    first_blocknum = economic.get_block_count_number(first_settlement_block, 10)
    print("第一个结算周期的出块数{}".format(first_blocknum))
    economic.wait_settlement_blocknum()
    economic.wait_consensus_blocknum()
    second_settlement_block = economic.get_settlement_switchpoint() - economic.settlement_size
    second_blocknum = economic.get_block_count_number(second_settlement_block, 20)
    print("第一个结算周期的出块数{}".format(second_blocknum - first_blocknum))
    first_block_reward_total, first_node_block_reward, first_delegate_block_reward = block_reward_total(first_block_reward, first_blocknum)
    print("第一个结算周期总出块奖励 {}".format(first_block_reward_total))
    print("第一个结算周期节点出块奖励 {}".format(first_node_block_reward))
    print("第一个结算周期委托者出块奖励 {}".format(first_delegate_block_reward))
    first_reward_total = first_block_reward_total + first_staking_reward
    print("第一个结算周期总奖励 {}".format(first_reward_total))
    delegate_staking_reward = int(Decimal(str(first_staking_reward)) * Decimal(str(10 / 100)))
    print("第一个结算周期委托者质押奖励 {}".format(delegate_staking_reward))
    delegate_reward_total = first_delegate_block_reward + delegate_staking_reward
    print("第一个结算周期委托者总奖励 {}".format(delegate_reward_total))
    node_staking_reward = math.ceil(Decimal(str(first_staking_reward)) * Decimal(str(90 / 100)))
    print("第一个结算周期节点质押奖励 {}".format(node_staking_reward))
    node_reward_total = node_staking_reward + first_node_block_reward
    print("第一个结算周期节点总奖励 {}".format(node_reward_total))

    second_block_reward_total, second_node_block_reward, second_delegate_block_reward = block_reward_total(second_block_reward, second_blocknum - first_blocknum)
    print("第二个结算周期总出块奖励 {}".format(second_block_reward_total))
    print("第二个结算周期节点出块奖励 {}".format(second_node_block_reward))
    print("第二个结算周期委托者出块奖励 {}".format(second_delegate_block_reward))
    print("第一个 + 第二个结算周期总奖励 {}".format(delegate_reward_total + first_node_block_reward + second_node_block_reward + node_staking_reward))
    print("第一个 + 第二个结算周期节点出块奖励 {}".format(first_node_block_reward + second_node_block_reward + second_delegate_block_reward))
    print("第一个 + 第二个结算周期节点出块奖励 {}".format(first_node_block_reward + second_block_reward_total))
    print("第一个 + 第二个结算周期节点总奖励 {}".format(first_node_block_reward + second_block_reward_total + node_staking_reward))

    balance = node.eth.getBalance(benifit_address, second_settlement_block)
    print("收益地址余额", balance)
    result = client.node.ppos.getCandidateInfo(client.node.node_id)
    print("获取当前节点的信息{}".format(result))
    result = client.node.ppos.getDelegateReward(delegate_address)
    print("获取委托者委托分红奖励{}".format(result))


def test_sss(noconsensus_client):
    client = noconsensus_client
    node = client.node
    economic = client.economic
    print(node.node_id)
    print(node.uri)
    # address, _ = client.account.generate_account(node.web3, noconsensus_client.economic.delegate_limit * 100)
    # print(address)
    # address = 'lax1s3age76zyrrf7e4j74yv0mjtawna8kpvcsvy3g'
    # node_id = 'd016ee2d7d10d57c27435c617c39ca170a79a9c414e8640e0f6fbedcb0cdb866fb8c03abbedd585897a63e5f6d4b074cbae163462ecba844829061fbdbfa76c5'
    # address = 'lax16r7sc6v6r73pu8wle5r2wn3ru7cx04qmd3c5hx'
    node_id = 'd0fc53064676b0e49c40271efadabf5109378d08b07850364243c2abf1df708a86e501e8b62d617579c2eea2ac80f0c996ee7b8a8db75d95e7e313c34646c1bc'
    # delegate_address = 'lax14vr3jfr9weg5scpm5en85v2t0lcmf7lpu7qzs5'
    delegate_address = 'lax10055sajvl3xu0av8kwd6x7048cfn5kz323mpyh'

    # result = client.builtin_rpc.create_staking(0, address, address, amount=client.economic.create_staking_limit * 2, reward_per=5000)
    # print(result)
    # result = client.builtin_rpc.withdrew_staking(address, node_id=node_id)
    # print(result)
    result = client.builtin_rpc.delegate(0, delegate_address, node_id=node_id)
    print(result)


