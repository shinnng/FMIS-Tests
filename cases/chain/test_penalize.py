import time
from decimal import Decimal

from loguru import logger

from cases.chain.conftest import withdrew_staking_all
from lib.chain.config import EconomicConfig
from lib.chain.utils import get_pledge_list, assert_code, assert_voucher_result, assert_status, \
    get_governable_parameter_value, assert_voucher_staking_result, get_report_reward
from common.key import mock_duplicate_sign
import pytest


def test_duplicate_sign(consensus_client_unanalyze, staking_client):
    """
    双签
    """
    client = consensus_client_unanalyze
    node = client.node
    economic = client.economic
    economic.wait_settlement_blocknum()
    time.sleep(1)
    penalty_reward, proportion_reward, incentive_pool_reward = get_report_reward(staking_client)
    report_address, _ = client.account.generate_account(node.web3, node.web3.toWei(1, "ether"))
    print(client.node.ppos.getVerifierList())
    for i in range(economic.consensus_wheel):
        verfiers = get_pledge_list(node.ppos.getValidatorList)
        # result = client.node.ppos.getVerifierList()
        print("获取验证人列表的信息{}".format(verfiers))
        if staking_client.node.node_id in verfiers:
            break
        economic.wait_consensus_blocknum()
    else:
        assert False, "node cannot enter consensus round"
    # nodekey, blsprikey = staking_client.account.find_node_pri_key(staking_client.node.node_id)
    nodekey = staking_client.node.env.private_key
    blsprikey = staking_client.node.env.bls_private_key
    data = mock_duplicate_sign(1, nodekey, blsprikey, node.eth.blockNumber)
    time.sleep(2)
    node_id = staking_client.node.node_id
    tx_hash = client.builtin_rpc.reportDuplicateSign(1, data, report_address)
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    logger.info("report Duplicate Sign hash : {}".format(tx_hash))
    # result = client.tidb.tb_tx_ori_voucher(tx_hash)
    # assert_voucher_result(result, 1, 3000)
    result = client.tidb.tb_tx_ori_voucher_double_sign_attach(node_id)
    print(result)
    assert int(result['total_punish_amount']) == penalty_reward
    assert int(result['reporter_punish_amount']) == proportion_reward
    assert int(result['reward_punish_amount']) == incentive_pool_reward
    assert int(result['locked_staking_amount']) == staking_client.economic.create_staking_limit - penalty_reward
    client.assert_balance(report_address)
    client.assert_balance(EconomicConfig.INCENTIVEPOOL_ADDRESS)


def test_zero_rate(consensus_client, noconsensus_client_unanalyze):
    """

    """
    # withdrew_staking_all(noconsensus_client)
    client = noconsensus_client_unanalyze
    amount = client.economic.create_staking_limit * 3
    address, _ = client.account.generate_account(client.node.web3, amount)
    logger.info("address {} balance: {}".format(address, client.node.eth.getBalance(address)))
    tx_hash = client.builtin_rpc.create_staking(0, address, address, amount=client.economic.create_staking_limit * 2 , reward_per=1000)
    logger.info("create staking hash : {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    node_id = client.node.node_id
    # result = client.tidb.tb_tx_ori_voucher(tx_hash)
    # assert_voucher_result(result, 1, 1000)
    staking_detail = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(node_id, client.staking_address)
    assert_voucher_staking_result(staking_detail, 2, 4)
    result = client.tidb.tb_node(node_id)
    assert_status(result, 1, 0)
    # client.assert_balance(client.staking_address)
    consensus_client.economic.wait_settlement_blocknum()
    block_reward, staking_reward = client.economic.get_current_year_reward(5)
    print("block_reward {}, staking_reward {}".format(block_reward, staking_reward))
    punishment_amonut = int(Decimal(str(block_reward)) * Decimal(str(consensus_client.economic.genesis.economicModel.slashing.slashBlocksReward)))
    print("punishment_amonut ", punishment_amonut)
    client.node.env.stop()
    consensus_client.economic.wait_settlement_blocknum()
    consensus_client.economic.wait_consensus_blocknum()
    noconsensus_client_unanalyze.node.env.start()
    candidate_info = consensus_client.node.ppos.getCandidateInfo(node_id)
    logger.info(" Candidate Info: {}".format(candidate_info))
    result = consensus_client.tidb.tb_node(node_id)
    assert_status(result, 2, 2)
    result = consensus_client.tidb.tb_slash_ori_voucher(node_id)
    # assert_zeroOutBlock(result, punishment_amonut * 2, candidate_info['Ret']['Released'])
    if punishment_amonut > consensus_client.economic.create_staking_limit * 2:
        assert int(result['slashing_amount']) == consensus_client.economic.create_staking_limit * 2
        assert int(result['freeze_staking_amount']) == 0
    else:
        assert int(result['slashing_amount']) == punishment_amonut
        assert int(result['freeze_staking_amount']) == consensus_client.economic.create_staking_limit * 2 - punishment_amonut
    assert int(result['slashing_type']) == 1
    consensus_client.assert_balance(address)
    # consensus_client.assert_balance(EconomicConfig.INCENTIVEPOOL_ADDRESS)


def test_0mb_not_triggered(consensus_client,noconsensus_client_unanalyze):
    client = noconsensus_client_unanalyze
    amount = client.economic.create_staking_limit * 101
    address, _ = client.account.generate_account(client.node.web3, amount)
    logger.info("address {} balance: {}".format(address, client.node.eth.getBalance(address)))
    tx_hash = client.builtin_rpc.create_staking(0, address, address, amount=client.economic.create_staking_limit * 100, reward_per=1000)
    logger.info("create staking hash : {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    node_id = client.node.node_id
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 1000)
    staking_detail = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(node_id, client.staking_address)
    assert_voucher_staking_result(staking_detail, 2, 4)
    result = client.tidb.tb_node(node_id)
    assert_status(result, 1, 0)
    # client.assert_balance(client.staking_address)
    consensus_client.economic.wait_settlement_blocknum()
    candidate_info = client.node.ppos.getCandidateInfo(node_id)['Ret']
    released = candidate_info['Released']
    block_reward, staking_reward = client.economic.get_current_year_reward(5)
    punishment_amonut = int(Decimal(str(block_reward)) * Decimal(str(consensus_client.economic.genesis.economicModel.slashing.slashBlocksReward)))
    client.node.env.stop()
    consensus_client.economic.wait_settlement_blocknum()
    client.node.env.start()
    result = consensus_client.tidb.tb_node(node_id)
    assert_status(result, 2, 6)
    consensus_client.economic.wait_settlement_blocknum()
    time.sleep(2)
    candidate_info = consensus_client.node.ppos.getCandidateInfo(node_id)
    logger.info(" Candidate Info: {}".format(candidate_info))
    result = consensus_client.tidb.tb_node(node_id)
    assert_status(result, 1, 0)
    result = consensus_client.tidb.tb_slash_ori_voucher(node_id)
    # assert_zeroOutBlock(result, punishment_amonut * 2, candidate_info['Ret']['Released'])
    assert int(result['slashing_amount']) == punishment_amonut
    assert int(result['freeze_staking_amount']) == released - punishment_amonut
    assert int(result['slashing_type']) == 1
    consensus_client.assert_balance(address)
    # client.assert_balance(EconomicConfig.INCENTIVEPOOL_ADDRESS)