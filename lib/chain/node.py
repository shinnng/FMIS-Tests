from alaya import Web3

from common.connect import connect_web3
from alaya.eth import PlatON
from alaya.ppos import Ppos
from alaya.pip import Pip
from alaya.admin import Admin
from alaya.debug import Debug
from env.node import NodeEnv

failed_msg = "Node-{} do {} failed:{}"
success_msg = "Node-{} do {} success"


class ClientNode:
    def __init__(self, web3: Web3, env: NodeEnv):
        self.web3 = web3
        self.uri = web3.manager.providers[0].endpoint_uri
        self.pip = Pip(self.web3)
        self.ppos = Ppos(self.web3)
        self.platon = PlatON(self.web3)
        self.eth = self.platon
        self.admin = Admin(self.web3)
        self.debug = Debug(self.web3)
        self.env = env

    @property
    def program_version(self):
        return self.admin.getProgramVersion()['Version']

    @property
    def program_version_sign(self):
        return self.admin.getProgramVersion()['Sign']

    @property
    def schnorr_NIZK_prove(self):
        return self.admin.getSchnorrNIZKProve()

    @property
    def node_id(self):
        return self.admin.nodeInfo.id

    @property
    def blspubkey(self):
        return self.admin.nodeInfo.blsPubKey

    @property
    def chain_id(self):
        return self.admin.nodeInfo.protocols.platon.config.chainId

    @property
    def staking_address(self):
        """
        staking wallet address
        """
        if not self.is_candidate:
            raise Exception("node not staking")
        return self.candidate.get('StakingAddress')

    @property
    def benefit_address(self):
        """
        staking wallet address
        """
        if not self.is_candidate:
            raise Exception("node not staking")
        return self.candidate.get('BenefitAddress')

    @property
    def candidate(self):
        return self.ppos.getCandidateInfo(self.node_id).get('Ret')

    @property
    def is_candidate(self):
        if isinstance(self.candidate, str):
            return False
        return True

    @property
    def benifit_address(self):
        """
        staking wallet address
        """
        if not self.is_candidate:
            raise Exception("node not staking")
        return self.candidate.get('BenefitAddress')


if __name__ == '__main__':
    web3 = connect_web3("http://10.10.8.209:7008", 101)
    node = ClientNode(web3)
    # print(node.node_id)
    # print(node.blspubkey)
    print(node.admin.nodeInfo.protocols.cbft.config.sys.period)
