import pytest
from loguru import logger
from pytest import fixture
from alaya import Web3

from lib.chain.config import EconomicConfig


def test_init_balance(consensus_client):
    """
    初始余额
    """
    node = consensus_client.node
    foundation_louckup = node.eth.getBalance(EconomicConfig.FOUNDATION_LOCKUP_ADDRESS)
    logger.info('Initial lock up contract amount：{}'.format(foundation_louckup))
    incentive_pool = node.eth.getBalance(EconomicConfig.INCENTIVEPOOL_ADDRESS)
    logger.info('Incentive pool amount：{}'.format(incentive_pool))
    staking = node.eth.getBalance(EconomicConfig.STAKING_ADDRESS)
    logger.info('Address of pledge contract amount：{}'.format(staking))
    foundation = node.eth.getBalance(EconomicConfig.FOUNDATION_ADDRESS)
    logger.info('PlatON Foundation amount：{}'.format(foundation))
    remain = node.eth.getBalance(EconomicConfig.REMAIN_ACCOUNT_ADDRESS)
    logger.info('Remaining total account amount：{}'.format(remain))
    develop = node.eth.getBalance(EconomicConfig.DEVELOPER_FOUNDATAION_ADDRESS)
    logger.info('Community developer foundation amount：{}'.format(develop))


def test_annual_additional_issue():
    """
    年度增发
    """




