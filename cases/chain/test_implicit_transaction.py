import pytest
from loguru import logger
from platon_account.internal.transactions import bech32_address_bytes
from pytest import fixture
from alaya import Web3

from lib.chain import von_amount, HexBytes, rlp, assert_code, time, Decimal, assert_status, assert_voucher_result, \
    assert_voucher_staking_result
from lib.chain.config import EconomicConfig


def view_benifit_reward(client):
    """
    withdrew pledge return benifit balance and Number of blocks
    :param client:
    :param address:
    :return:
    """
    # withdrew of pledge
    tx_hash = client.builtin_rpc.withdrew_staking(client.staking_address)
    logger.info("create staking hash : {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    # wait settlement block
    client.economic.wait_settlement_blocknum()
    # wait consensus block
    client.economic.wait_consensus_blocknum()
    time.sleep(2)
    # count the number of blocks
    blocknumber = client.economic.get_block_count_number(5)
    logger.info("blocknumber: {}".format(blocknumber))
    return blocknumber


def test_meanwhile_transfer_staking(noconsensus_client_unanalyze, unstaking):
    """
    同时发起质押和转账
    """
    client = noconsensus_client_unanalyze
    economic = client.economic
    node = client.node
    address, _ = client.account.generate_account(node.web3, von_amount(economic.create_staking_limit, 2))
    benifit_address, _ = client.account.generate_account(node.web3, 0)
    first_staking_balance = node.eth.getBalance(node.web3.stakingAddress)
    logger.info("first_staking_balance : {}".format(first_staking_balance))
    program_version_sign = node.program_version_sign
    program_version = node.program_version
    bls_pubkey = node.blspubkey
    bls_proof = node.schnorr_NIZK_prove
    benifit_address = bech32_address_bytes(benifit_address)
    if program_version_sign[:2] == '0x':
        program_version_sign = program_version_sign[2:]
    data = HexBytes(rlp.encode([rlp.encode(int(1000)), rlp.encode(0), rlp.encode(benifit_address),
                                rlp.encode(bytes.fromhex(node.node_id)), rlp.encode("platon"), rlp.encode("platon1"),
                                rlp.encode("http://www.platon.network"), rlp.encode("The PlatON Node"),
                                rlp.encode(economic.create_staking_limit), rlp.encode(0), rlp.encode(program_version),
                                rlp.encode(bytes.fromhex(program_version_sign)), rlp.encode(bytes.fromhex(bls_pubkey)),
                                rlp.encode(bytes.fromhex(bls_proof))])).hex()
    transaction_data = {"to": EconomicConfig.STAKING_ADDRESS, "data": data, "from": address}
    gas = node.eth.estimateGas(transaction_data)
    logger.info("gas: {}".format(gas))
    receipt = client.account.sendTransaction(node.web3, data, address, EconomicConfig.STAKING_ADDRESS, node.eth.gasPrice, gas, node.web3.toWei(1000, 'ether'))
    logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))
    result = client.node.platon.analyzeReceiptByHash(receipt.transactionHash.hex())
    assert_code(result, 0)
    time.sleep(1)
    logger.info("Candidate Info".format(node.ppos.getCandidateInfo(node.node_id)))
    result = client.tidb.tb_tx_ori_voucher(receipt.transactionHash.hex())
    assert_voucher_result(result, 1, 1000)
    result = client.tidb.tb_tx_ori_voucher_staking_delegate_detail_status(node.node_id, client.staking_address)
    assert_voucher_staking_result(result, 2, 4)
    result = client.tidb.tb_node(node.node_id)
    assert_status(result, 1, 0)
    client.assert_balance(client.staking_address)
    client.assert_balance(node.web3.stakingAddress)


def test_block_reward(staking_client):
    """
    出块奖励和质押奖励
    """
    client = staking_client
    client.economic.wait_settlement_blocknum()
    time.sleep(1)
    block_reward, staking_reward = client.economic.get_current_year_reward(10)
    logger.info("block_reward: {} staking_reward: {}".format(block_reward, staking_reward))
    candidate_info = client.node.ppos.getCandidateInfo(client.node.node_id)
    blocknumber = view_benifit_reward(client)
    result = client.tidb.tb_node(client.node.node_id)
    assert_status(result, 2, 3)
    assert int(result['total_delegation_reward']) == 0
    assert int(result['total_staking_delegation_reward']) == 0
    assert int(result['total_block_delegation_reward']) == 0
    assert int(result['current_epoch_delegation_block_reward']) == 0
    assert int(result['reward_delegation_percent']) == candidate_info['Ret']['RewardPer']
    assert int(result['next_reward_delegation_percent']) == candidate_info['Ret']['NextRewardPer']
    result = client.tidb.tb_block_reward_ori_voucher(client.node.node_id, client.node.benifit_address)
    assert int(result['block_number']) == blocknumber
    # TODO:放到后面做
    # assert int(result['reward_amount']) == int(Decimal(blocknumber) * Decimal(str(block_reward)))
    # assert int(result['node_reward_amount']) == int(Decimal(blocknumber) * Decimal(str(block_reward)))
    # assert int(result['delegate_reward_amount']) == 0
    result = client.tidb.tb_staking_reward_ori_voucher(client.node.node_id, client.node.benifit_address)
    assert int(result['number']) == 1
    # assert int(result['reward_amount']) == staking_reward
    # assert int(result['node_reward_amount']) == staking_reward
    # assert int(result['delegate_reward_amount']) == 0



