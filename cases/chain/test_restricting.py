import time

import pytest
from lib.chain.utils import assert_code, assert_voucher_result, assert_voucher_staking_result, assert_status, \
    scientific_notation_to_int
from alaya import Web3
from loguru import logger
import numpy as np
np.set_printoptions(suppress=True)


def restricting(client):
    amount = Web3.toWei(100, "ether")
    benifit_address, _ = client.account.generate_account(client.node.web3, client.node.web3.toWei(100, 'ether'))
    epoch = 1
    plan = [{'Epoch': epoch, 'Amount': amount}]
    tx_hash = client.builtin_rpc.createRestrictingPlan(benifit_address, plan, client.account.address_with_money)
    logger.info(" create Restricting Plan transaction hash: {}".format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(3)
    restricting_info = client.node.ppos.getRestrictingInfo(benifit_address)
    print(restricting_info)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 4000)
    result = client.tidb.tb_tx_ori_voucher_create_lock_plan_attach(benifit_address)
    print(result)
    assert int(result['lock_amount']) == amount
    assert int(result['release_epoch']) == epoch
    client.assert_balance(benifit_address)
    return benifit_address, amount


def restricting_staking(client):
    amount = client.economic.create_staking_limit
    address, _ = client.account.generate_account(client.node.web3, client.economic.create_staking_limit * 2)
    benifit_address, _ = client.account.generate_account(client.node.web3, client.node.web3.toWei(100, 'ether'))
    epoch = 1
    plan = [{'Epoch': epoch, 'Amount': amount}]
    tx_hash = client.builtin_rpc.createRestrictingPlan(benifit_address, plan, address)
    logger.info(" create Restricting Plan transaction hash: {}".format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    restricting_info = client.node.ppos.getRestrictingInfo(benifit_address)
    print(restricting_info)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 4000)
    result = client.tidb.tb_tx_ori_voucher_create_lock_plan_attach(benifit_address)
    assert int(result['lock_amount']) == amount
    assert int(result['release_epoch']) == epoch
    tx_hash = client.builtin_rpc.create_staking(1, benifit_address, benifit_address)
    logger.info(" create restricting staking transaction hash: {}".format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1000)
    staking_status = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, client.staking_address)
    assert_voucher_staking_result(staking_status, 2, 4)
    staking_detail = client.tidb.tb_tx_ori_voucher_staking_delegate_detail(client.node.node_id, client.staking_address)
    assert scientific_notation_to_int(staking_detail['lock_amount']) == client.economic.create_staking_limit
    # assert int(staking_detail['lock_amount']) == client.economic.create_staking_limit
    result = client.tidb.tb_node(client.node.node_id)
    assert int(result['hesitating_staking_restricting_amount']) == client.economic.create_staking_limit
    return benifit_address, amount


def test_create_restricting(noconsensus_client_unanalyze, unstaking):
    """
    创建锁仓计划,等待释放查看信息状态
    """
    client = noconsensus_client_unanalyze
    benifit_address, amount = restricting(client)
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    result = client.tidb.tb_restrict_release_ori_voucher(benifit_address)
    assert int(result['release_amount']) == amount
    client.assert_balance(benifit_address)


def test_restricting_staking(noconsensus_client_unanalyze, unstaking):
    """
    使用锁仓金额质押 查看信息状态
    """
    client = noconsensus_client_unanalyze
    benifit_address, amount = restricting_staking(client)
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    logger.info("benifit_address balance: {}".format(client.node.eth.getBalance(benifit_address)))
    result = client.tidb.tb_restrict_release_ori_voucher(benifit_address)
    assert int(result['release_amount']) == amount - client.economic.create_staking_limit
    client.assert_balance(benifit_address)
    resutl = client.tidb.tb_node(client.node.node_id)
    # assert scientific_notation_to_int(resutl['valid_staking_restricting_amount']) == client.economic.create_staking_limit
    assert int(resutl['valid_staking_restricting_amount']) == client.economic.create_staking_limit
    client.assert_balance(benifit_address)


def test_restricting_staking_free_increase_staking(noconsensus_client_unanalyze, unstaking):
    """
    使用锁仓金额质押,自由金额增持质押 查看信息状态
    """
    client = noconsensus_client_unanalyze
    benifit_address, amount = restricting_staking(client)
    tx_hash = client.builtin_rpc.increase_staking(0, benifit_address)
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    logger.info("free amount increase staking transaction hash: {}".format(tx_hash))
    staking_status = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, benifit_address)
    assert_voucher_staking_result(staking_status, 2, 1)
    staking_detail = client.tidb.tb_tx_ori_voucher_staking_delegate_detail(client.node.node_id, benifit_address)
    assert int(staking_detail['free_amount']) == client.economic.add_staking_limit
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['hesitating_staking_balance_amount']) == client.economic.add_staking_limit
    assert int(result['hesitating_staking_restricting_amount']) == client.economic.create_staking_limit
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    logger.info("benifit_address balance: {}".format(client.node.eth.getBalance(benifit_address)))
    result = client.tidb.tb_restrict_release_ori_voucher(benifit_address)
    assert int(result['release_amount']) == amount - client.economic.create_staking_limit
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['valid_staking_balance_amount']) == client.economic.add_staking_limit
    assert int(result['valid_staking_restricting_amount']) == client.economic.create_staking_limit
    result = client.tidb.tb_staking_lock_ori_voucher(client.node.node_id, benifit_address)
    assert int(
        result['staking_lock_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit
    client.assert_balance(benifit_address)


def test_free_staking_restricting_increase_staking(noconsensus_client_unanalyze, unstaking):
    """
    使用自由金额质押,锁仓金额增持质押 查看信息状态
    """
    client = noconsensus_client_unanalyze
    address, _ = client.account.generate_account(client.node.web3, client.economic.create_staking_limit * 2)
    tx_hash = client.builtin_rpc.create_staking(0, address, address)
    logger.info("free amount create staking transaction hash: {}".format(tx_hash))
    amount = Web3.toWei(100, "ether")
    # benifit_address, _ = client.account.generate_account(client.node.web3, 0)
    epoch = 1
    plan = [{'Epoch': epoch, 'Amount': amount}]
    tx_hash = client.builtin_rpc.createRestrictingPlan(address, plan, client.account.address_with_money)
    logger.info(" create Restricting Plan transaction hash: {}".format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    tx_hash = client.builtin_rpc.increase_staking(1, address)
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    logger.info("Restricting Plan amount increase staking transaction hash: {}".format(tx_hash))
    staking_status = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, address)
    assert_voucher_staking_result(staking_status, 2, 1)
    staking_detail = client.tidb.tb_tx_ori_voucher_staking_delegate_detail(client.node.node_id, address)
    assert int(staking_detail['lock_amount']) == client.economic.add_staking_limit
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['hesitating_staking_balance_amount']) == client.economic.create_staking_limit
    assert int(result['hesitating_staking_restricting_amount']) == client.economic.add_staking_limit
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    logger.info("benifit_address balance: {}".format(client.node.eth.getBalance(address)))
    result = client.tidb.tb_restrict_release_ori_voucher(address)
    assert int(result['release_amount']) == amount - client.economic.add_staking_limit
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['valid_staking_balance_amount']) == client.economic.create_staking_limit
    assert int(result['valid_staking_restricting_amount']) == client.economic.add_staking_limit
    result = client.tidb.tb_staking_lock_ori_voucher(client.node.node_id, address)
    assert int(
        result['staking_lock_amount']) == client.economic.create_staking_limit + client.economic.add_staking_limit
    client.assert_balance(address)


def restricting_delegate(client):
    address, _ = client.account.generate_account(client.node.web3, client.economic.create_staking_limit * 2)
    tx_hash = client.builtin_rpc.create_staking(0, address, address)
    logger.info("free amount create staking transaction hash: {}".format(tx_hash))
    benifit_address, amount = restricting(client)
    tx_hash = client.builtin_rpc.delegate(1, benifit_address, amount=client.economic.delegate_limit * 2)
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    logger.info("Restricting Plan amount delegate transaction hash: {}".format(tx_hash))
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1004)
    delegate_status = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, benifit_address)
    assert_voucher_staking_result(delegate_status, 1, 4)
    delegate_detail = client.tidb.tb_tx_ori_voucher_staking_delegate_detail(client.node.node_id, benifit_address)
    assert scientific_notation_to_int(delegate_detail['lock_amount']) == client.economic.delegate_limit * 2
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['hesitating_delegation_restricting_amount']) == client.economic.delegate_limit * 2
    return benifit_address, amount


def test_restricting_delegate(noconsensus_client_unanalyze, unstaking):
    """
    使用锁仓金额委托
    """
    client = noconsensus_client_unanalyze
    benifit_address, amount = restricting_delegate(client)
    client.economic.wait_settlement_blocknum()
    time.sleep(2)
    logger.info("benifit_address balance: {}".format(client.node.eth.getBalance(benifit_address)))
    result = client.tidb.tb_restrict_release_ori_voucher(benifit_address)
    assert int(result['release_amount']) == amount - client.economic.delegate_limit * 2
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['valid_delegation_restricting_amount']) == client.economic.delegate_limit * 2
    result = client.tidb.tb_delegate_lock_ori_voucher(client.node.node_id, benifit_address)
    assert result
    result = client.tidb.tb_staking_lock_ori_voucher(client.node.node_id, client.staking_address)
    assert int(result['staking_lock_amount']) == client.economic.create_staking_limit
    client.assert_balance(benifit_address)


def test_restricting_withdrew_delegate(noconsensus_client_unanalyze, unstaking):
    """
    锁仓委托又赎回部分委托，等待锁定期再赎回剩余委托
    """
    client = noconsensus_client_unanalyze
    benifit_address, amount = restricting_delegate(client)
    block_number = client.builtin_rpc.staking_block_number()
    tx_hash = client.builtin_rpc.withdrew_delegate(block_number, benifit_address)
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    logger.info("Restricting Plan amount withdrew delegate transaction hash: {}".format(tx_hash))
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1005)
    result = client.tidb.tb_tx_ori_voucher_undelegation_attach(client.node.node_id, benifit_address)
    assert int(result['lock_unlock_staking_amount']) == client.economic.delegate_limit
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['hesitating_delegation_balance_amount']) == 0
    assert int(result['hesitating_delegation_restricting_amount']) == client.economic.delegate_limit
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    logger.info("benifit_address balance: {}".format(client.node.eth.getBalance(benifit_address)))
    result = client.tidb.tb_restrict_release_ori_voucher(benifit_address)
    assert int(result['release_amount']) == amount - client.economic.delegate_limit
    # result = client.tidb.tb_delegate_lock_ori_voucher(client.node.node_id, benifit_address)
    # assert result
    result = client.tidb.tb_staking_lock_ori_voucher(client.node.node_id, client.staking_address)
    assert int(result['staking_lock_amount']) == client.economic.create_staking_limit
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['valid_delegation_restricting_amount']) == client.economic.delegate_limit
    tx_hash = client.builtin_rpc.withdrew_delegate(block_number, benifit_address)
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    logger.info("Restricting Plan amount withdrew delegate transaction hash: {}".format(tx_hash))
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1005)
    candidate_info = client.node.ppos.getCandidateInfo(client.node.node_id)
    logger.info("Candidate Info : {}".format(candidate_info))
    result = client.tidb.tb_tx_ori_voucher_undelegation_attach(client.node.node_id, benifit_address)
    assert int(result['lock_unlock_staking_amount']) == client.economic.delegate_limit
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['valid_delegation_balance_amount']) == 0
    assert int(result['valid_delegation_restricting_amount']) == 0
    client.assert_balance(benifit_address)


def test_restricting_and_free_delegate(noconsensus_client_unanalyze):
    """
    使用混合金额委托
    """
    client = noconsensus_client_unanalyze
    benifit_address, amount = restricting_delegate(client)
    tx_hash = client.builtin_rpc.delegate(0, benifit_address)
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    logger.info("free amount delegate transaction hash: {}".format(tx_hash))
    staking_status = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(client.node.node_id, benifit_address)
    assert_voucher_staking_result(staking_status, 1, 4)
    staking_detail = client.tidb.tb_tx_ori_voucher_staking_delegate_detail(client.node.node_id, benifit_address)
    assert scientific_notation_to_int(staking_detail['free_amount']) == client.economic.add_staking_limit
    assert scientific_notation_to_int(staking_detail['lock_amount']) == client.economic.add_staking_limit * 2
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['hesitating_delegation_balance_amount']) == client.economic.delegate_limit
    assert int(result['hesitating_delegation_restricting_amount']) == client.economic.delegate_limit * 2

    client.economic.wait_settlement_blocknum()
    time.sleep(2)
    logger.info("benifit_address balance: {}".format(client.node.eth.getBalance(benifit_address)))
    result = client.tidb.tb_restrict_release_ori_voucher(benifit_address)
    assert int(result['release_amount']) == amount - client.economic.delegate_limit * 2
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 1, 0)
    assert int(result['valid_delegation_restricting_amount']) == client.economic.delegate_limit * 2
    assert int(result['valid_delegation_balance_amount']) == client.economic.delegate_limit
    assert int(result['valid_delegation_restricting_amount']) == client.economic.delegate_limit * 2
    result = client.tidb.tb_delegate_lock_ori_voucher(client.node.node_id, benifit_address)
    assert result
    result = client.tidb.tb_staking_lock_ori_voucher(client.node.node_id, client.staking_address)
    assert int(result['staking_lock_amount']) == client.economic.create_staking_limit
    client.assert_balance(benifit_address)


def test_restricting_multiple_releases(noconsensus_client_unanalyze):
    """
    多次释放
    """
    client = noconsensus_client_unanalyze
    benifit_address, _ = client.account.generate_account(client.node.web3, 0)
    plan = [{'Epoch': 1, 'Amount': client.economic.delegate_limit},
            {'Epoch': 2, 'Amount': client.economic.delegate_limit}]
    tx_hash = client.builtin_rpc.createRestrictingPlan(benifit_address, plan, client.account.address_with_money)
    logger.info(" create Restricting Plan transaction hash: {}".format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    restricting_info = client.node.ppos.getRestrictingInfo(benifit_address)
    print(restricting_info)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 4000)
    result = client.tidb.tb_tx_ori_voucher_create_lock_plan_attach(benifit_address)
    print(result)
    assert int(result[0]['lock_amount']) == client.economic.delegate_limit and int(
        result[1]['lock_amount']) == client.economic.delegate_limit
    assert int(result[0]['release_epoch']) == 1 and int(result[1]['release_epoch']) == 2
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    result = client.tidb.tb_restrict_release_ori_voucher(benifit_address)
    assert int(result['release_amount']) == client.economic.delegate_limit
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    result = client.tidb.tb_restrict_release_ori_voucher(benifit_address)
    assert int(result['release_amount']) == client.economic.delegate_limit


def test_restricting_unstaking(noconsensus_client_unanalyze):
    """

    :param noconsensus_client_unanalyze:
    :return:
    """
    client = noconsensus_client_unanalyze
    benifit_address, amount = restricting_staking(client)
    client.economic.wait_settlement_blocknum()
    time.sleep(2)
    tx_hash = client.builtin_rpc.withdrew_staking(benifit_address)
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)


