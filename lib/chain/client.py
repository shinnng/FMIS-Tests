import time

from alaya.utils.threads import (
    Timeout,
)
from loguru import logger
from .config import StakingConfig
from .economic import Economic
from .restricting import RestrictingMixin
from .delegate import DelegateMixin
from .staking import StakingMixin
from .pip import PipMixin
from .duplicate_sign import DuplicateSignMixin
from .node import ClientNode
from lib.tidb import Tidb
from .account import Account
from .genesis import Genesis


class Client:
    """
    Test client, the interface call method required for the collection test
    """

    def __init__(self, node: ClientNode, cfg: StakingConfig, tidb: Tidb, account: Account, genesis: Genesis):
        self.staking_cfg = cfg
        self.node = node
        self.economic = Economic(genesis, self.node)
        self.tidb = tidb
        self.account = account
        self.builtin_rpc = BuiltInRPC(self.node, cfg, self.economic, self.account)

    @property
    def staking_address(self):
        return self.node.staking_address

    def assert_balance(self, address):
        platon_block = self.node.eth.blockNumber
        with Timeout(10) as _timeout:
            while True:
                if self.tidb.tb_sync_status()['last_block_number'] > platon_block:
                    break
                _timeout.sleep(0.1)
        logger.info("tb_sync_status last block {}".format(self.tidb.tb_sync_status()['last_block_number']))
        logger.info("block number {} , platon address {} , banalce: {}".format(platon_block, address, self.node.platon.getBalance(address, platon_block)))
        logger.info("tidb max block {}, tb_track_account_book banalce: {}".format(platon_block, self.tidb.query_balance(address, platon_block)["balance"]))
        logger.info("tidb max block {}, tb_address banalce: {}".format(platon_block, self.tidb.tb_address(address)["balance"]))
        assert self.node.platon.getBalance(address, platon_block) == self.tidb.query_balance(address, platon_block)["balance"]
        assert self.node.platon.getBalance(address, platon_block) == int(self.tidb.tb_address(address)["balance"])


class BuiltInRPC(StakingMixin, DelegateMixin, RestrictingMixin, PipMixin, DuplicateSignMixin):
    def __init__(self, node: ClientNode, cfg: StakingConfig, economic: Economic, account: Account):
        self._staking_cfg = cfg
        self._node = node
        self._pip = node.pip
        self._ppos = node.ppos
        self._economic = economic
        self._account = account
