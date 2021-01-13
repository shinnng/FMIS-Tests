import pytest
import time

from lib.chain import PipConfig
from lib.chain.client import Client
from loguru import logger
from lib.chain.utils import assert_code, get_governable_parameter_value, assert_voucher_result

illegal_node_id = 'a23251dad890714ab59cf433cdc9c8efe4b5d3ea636a2656848cb6442ab9ce7ab5b453bca950d6d701fc6140a1af2263f4aa91e805582c2d58290cd8d79d6aca'


@pytest.fixture()
def version_proposal_client(consensus_client):
    result = consensus_client.builtin_rpc.submitVersion(consensus_client.node.node_id, str(time.time()),
                                                        consensus_client.builtin_rpc.pip_cfg.version5, 1,
                                                        consensus_client.node.staking_address,
                                                        transaction_cfg=consensus_client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit version result : {}'.format(result))
    assert_code(result, 0)
    yield consensus_client
    cancal_proposal(consensus_client, consensus_client.builtin_rpc.pip_cfg.version_proposal)


@pytest.fixture()
def param_proposal_client(consensus_client):
    newvalue = '1'
    if int(get_governable_parameter_value(consensus_client, 'slashBlocksReward')) == 1:
        newvalue = '2'
    result = consensus_client.builtin_rpc.submitParam(consensus_client.node.node_id, str(time.time()), 'slashing',
                                                      'slashBlocksReward', newvalue,
                                                      consensus_client.node.staking_address,
                                                      transaction_cfg=consensus_client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit param proposal result : {}'.format(result))
    assert_code(result, 0)
    yield consensus_client
    cancal_proposal(consensus_client, consensus_client.builtin_rpc.pip_cfg.param_proposal)


@pytest.fixture()
def text_proposal_client(consensus_client):
    result = consensus_client.builtin_rpc.submitText(consensus_client.node.node_id, str(time.time()),
                                                     consensus_client.node.staking_address,
                                                     transaction_cfg=consensus_client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit text result:'.format(result))
    assert_code(result, 0)
    yield consensus_client
    cancal_proposal(consensus_client, consensus_client.builtin_rpc.pip_cfg.text_proposal)


def cancal_proposal(client: Client, proposal_type):
    proposal = client.builtin_rpc.get_proposal(proposal_type)
    logger.info('Get voting param proposal info :{}'.format(proposal))
    if proposal is None:
        return
    result = client.builtin_rpc.submitCancel(client.node.node_id, str(time.time()), 2, proposal.get('ProposalID'),
                                             client.node.staking_address,
                                             transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit cancel proposal result : {}'.format(result))
    assert_code(result, 0)


def proposal_is_exists(client, proposal_type):
    proposal_dict = client.node.pip.listProposal()
    if proposal_dict['Code'] == 0:
        proposal = client.builtin_rpc.get_proposal(proposal_type)
        logger.info("proposal info : {}".format(proposal))
        if proposal:
            if 'EndVotingRounds' in proposal.keys():
                number = proposal['EndVotingRounds']
                client.economic.wait_settlement_blocknum(number - 1)
            else:
                client.economic.wait_settlement_blocknum()
    return


def test_version_proposal(consensus_client_unanalyze):
    """

    """
    client = consensus_client_unanalyze
    proposal_is_exists(client, 2)
    tx_hash = client.builtin_rpc.submitVersion(illegal_node_id, str(time.time()),
                                               client.builtin_rpc.pip_cfg.version5, 1,
                                               client.node.staking_address,
                                               transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit version tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 302022)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 9997)

    tx_hash = client.builtin_rpc.submitVersion(client.node.node_id, str(time.time()),
                                               client.builtin_rpc.pip_cfg.version5, 1,
                                               client.node.staking_address,
                                               transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit version tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 2001)


def test_param_proposal(consensus_client_unanalyze):
    """

    """
    client = consensus_client_unanalyze
    proposal_is_exists(client, 3)
    newvalue = '1'
    if int(get_governable_parameter_value(client,
                                          'slashBlocksReward')) == client.economic.genesis.economicModel.slashing.slashBlocksReward:
        newvalue = '2'
    tx_hash = client.builtin_rpc.submitParam(illegal_node_id, str(time.time()), 'slashing',
                                             'slashBlocksReward', newvalue,
                                             client.node.staking_address,
                                             transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit submitParam tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 302022)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 9997)

    tx_hash = client.builtin_rpc.submitParam(client.node.node_id, str(time.time()), 'slashing',
                                             'slashBlocksReward', newvalue,
                                             client.node.staking_address,
                                             transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit submitParam tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 2002)


def test_text_proposal(consensus_client_unanalyze):
    client = consensus_client_unanalyze
    proposal_is_exists(client, 1)
    tx_hash = client.builtin_rpc.submitText(illegal_node_id, str(time.time()),
                                            client.node.staking_address,
                                            transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit submitText tx_hash:'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 302022)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 9997)

    tx_hash = client.builtin_rpc.submitText(client.node.node_id, str(time.time()),
                                            client.node.staking_address,
                                            transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit submitText tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 2000)


def test_cancal_submitVersion_proposal(consensus_client_unanalyze):
    client = consensus_client_unanalyze
    proposal_is_exists(client, 2)
    proposal_is_exists(client, 4)
    tx_hash = client.builtin_rpc.submitVersion(client.node.node_id, str(time.time()),
                                               client.builtin_rpc.pip_cfg.version5, 2,
                                               client.node.staking_address,
                                               transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit version tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 2001)

    proposal = client.builtin_rpc.get_proposal(2)
    logger.info('Get voting param proposal info :{}'.format(proposal))
    tx_hash = client.builtin_rpc.submitCancel(illegal_node_id, str(time.time()), 1, proposal.get('ProposalID'),
                                              client.node.staking_address,
                                              transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit cancel submitCancel tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 302022)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 9997)

    logger.info('Get voting param proposal info :{}'.format(proposal))
    tx_hash = client.builtin_rpc.submitCancel(client.node.node_id, str(time.time()), 1, proposal.get('ProposalID'),
                                              client.node.staking_address,
                                              transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit cancel submitCancel tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 2005)


def test_cancal_submitParam_proposal(consensus_client_unanalyze):
    client = consensus_client_unanalyze
    proposal_is_exists(client, 3)
    proposal_is_exists(client, 4)
    newvalue = '1'
    if int(get_governable_parameter_value(client,
                                          'slashBlocksReward')) == client.economic.genesis.economicModel.slashing.slashBlocksReward:
        newvalue = '2'
    tx_hash = client.builtin_rpc.submitParam(client.node.node_id, str(time.time()), 'slashing',
                                             'slashBlocksReward', newvalue,
                                             client.node.staking_address,
                                             transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit submitParam tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 2002)

    proposal = client.builtin_rpc.get_proposal(3)
    logger.info('Get voting param proposal info :{}'.format(proposal))
    tx_hash = client.builtin_rpc.submitCancel(illegal_node_id, str(time.time()), 1, proposal.get('ProposalID'),
                                              client.node.staking_address,
                                              transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit cancel submitCancel tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 302022)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 9997)

    logger.info('Get voting param proposal info :{}'.format(proposal))
    tx_hash = client.builtin_rpc.submitCancel(client.node.node_id, str(time.time()), 1, proposal.get('ProposalID'),
                                              client.node.staking_address,
                                              transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit cancel submitCancel tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 2005)


def test_declare_version(consensus_client_unanalyze):
    client = consensus_client_unanalyze
    tx_hash = client.builtin_rpc.declareVersion(client.node.node_id, client.account.address_with_money)
    logger.info('declareVersion tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 302021)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 9997)

    tx_hash = client.builtin_rpc.declareVersion(client.node.node_id, client.staking_address)
    logger.info('declareVersion tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 2004)


def test_vote(consensus_client_unanalyze):
    """

    """
    client = consensus_client_unanalyze
    proposal_is_exists(client, 2)
    proposal = client.builtin_rpc.submitVersion(client.node.node_id, str(time.time()),
                                                client.builtin_rpc.pip_cfg.version4, 4,
                                                client.node.staking_address,
                                                transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('submit version tx_hash : {}'.format(proposal))
    result = client.node.eth.analyzeReceiptByHash(proposal)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(proposal)
    assert_voucher_result(result, 1, 2001)

    tx_hash = client.builtin_rpc.vote(client.node.node_id, proposal, 1, client.account.address_with_money)
    logger.info('vote tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 302021)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 9997)

    tx_hash = client.builtin_rpc.vote(client.node.node_id, proposal, 1, client.staking_address)
    logger.info('vote tx_hash : {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    time.sleep(2)
    result = client.tidb.tb_tx_ori_voucher(tx_hash)
    assert_voucher_result(result, 1, 2003)
