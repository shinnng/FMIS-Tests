from .config import PipConfig


class PipMixin:
    """
    Used to initiate a pip transaction,
    if you need to use the call method, please call pip
    """
    pip_cfg = PipConfig

    def submitText(self, verifier, pip_id, from_address, transaction_cfg=None):
        """
        Submit a text proposal
        :param verifier: The certified submitting the proposal
        :param pip_id: PIPID
        :param from_address: address for transaction
        :param transaction_cfg: Transaction basic configuration
             type: dict
             example:pip_cfg = {
                 "gas":100000000,
                 "gasPrice":2000000000000,
                 "nonce":1,
             }
        :return: if is need analyze return transaction result dict
               if is not need analyze return transaction hash
        """
        pri_key = self._account.find_pri_key(from_address)
        return self._pip.submitText(verifier, pip_id, pri_key, transaction_cfg)

    def submitVersion(self, verifier, pip_id, new_version, end_voting_rounds, from_address, transaction_cfg=None):
        """
        Submit an upgrade proposal
        :param verifier:  The certified submitting the proposal
        :param pip_id:  PIPID
        :param new_version: upgraded version
        :param end_voting_rounds: The number of voting consensus rounds.
            Explanation: Assume that the transaction submitted by the proposal is rounded when the consensus round
            number of the package is packed into the block, then the proposal voting block is high,
            which is the 230th block height of the round of the round1 + endVotingRounds
            (assuming a consensus round out of block 250, ppos The list is 20 blocks high in advance,
             250, 20 are configurable), where 0 < endVotingRounds <= 4840 (about 2 weeks, the actual discussion
             can be calculated according to the configuration), and is an integer)
        :param from_address: address for transaction
        :param transaction_cfg: Transaction basic configuration
              type: dict
              example:pip_cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        :return: if is need analyze return transaction result dict
                if is not need analyze return transaction hash
        """
        pri_key = self._account.find_pri_key(from_address)
        return self._pip.submitVersion(verifier, pip_id, new_version, end_voting_rounds, pri_key, transaction_cfg)

    def submitParam(self, verifier, pip_id, module, name, new_value, from_address, transaction_cfg=None):
        """
        Submit an param proposal
        :param verifier: The certified submitting the proposal
        :param pip_id: PIPID
        :param module: parameter module
        :param name: parameter name
        :param new_value: New parameter value
        :param from_address: address for transaction
        :param transaction_cfg: Transaction basic configuration
             type: dict
             example:pip_cfg = {
                 "gas":100000000,
                 "gasPrice":2000000000000,
                 "nonce":1,
             }
        :return: if is need analyze return transaction result dict
               if is not need analyze return transaction hash
        """
        pri_key = self._account.find_pri_key(from_address)
        return self._pip.submitParam(verifier, pip_id, module, name, new_value, pri_key, transaction_cfg)

    def submitCancel(self, verifier, pip_id, end_voting_rounds, tobe_canceled_proposal_id, from_address,
                     transaction_cfg=None):
        """
        Submit cancellation proposal
        :param verifier: The certified submitting the proposal
        :param pip_id: PIPID
        :param end_voting_rounds:
           The number of voting consensus rounds. Refer to the instructions for submitting the upgrade proposal.
           At the same time, the value of this parameter in this interface
           cannot be greater than the value in the corresponding upgrade proposal.
        :param tobe_canceled_proposal_id: Upgrade proposal ID to be cancelled
        :param from_address: address for transaction
        :param transaction_cfg: Transaction basic configuration
              type: dict
              example:pip_cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        :return: if is need analyze return transaction result dict
                if is not need analyze return transaction hash
        """
        pri_key = self._account.find_pri_key(from_address)
        return self._pip.submitCancel(verifier, pip_id, end_voting_rounds, tobe_canceled_proposal_id, pri_key,
                                      transaction_cfg)

    def vote(self, verifier, proposal_id, option, from_address, program_version=None, version_sign=None,
             transaction_cfg=None):
        """
        Vote for proposal
        :param verifier:  The certified submitting the proposal
        :param proposal_id: Proposal ID
        :param option: Voting option
        :param program_version: Node code version, obtained by rpc getProgramVersion interface
        :param version_sign: Code version signature, obtained by rpc getProgramVersion interface
        :param from_address: address for transaction
        :param transaction_cfg: Transaction basic configuration
              type: dict
              example:pip_cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        :return: if is need analyze return transaction result dict
                if is not need analyze return transaction hash
        """
        pri_key = self._account.find_pri_key(from_address)
        if program_version is None:
            program_version = self._node.program_version
        if version_sign is None:
            version_sign = self._node.program_version_sign
        return self._pip.vote(verifier, proposal_id, option, program_version, version_sign, pri_key, transaction_cfg)

    def declareVersion(self, active_node, from_address, program_version=None, version_sign=None, transaction_cfg=None):
        """
        Version statement
        :param active_node: The declared node can only be a verifier/candidate
        :param program_version: The declared version, obtained by rpc's getProgramVersion interface
        :param version_sign: The signed version signature, obtained by rpc's getProgramVersion interface
        :param from_address: address transaction
        :param transaction_cfg: Transaction basic configuration
              type: dict
              example:pip_cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        :return: if is need analyze return transaction result dict
                if is not need analyze return transaction hash
        """
        pri_key = self._account.find_pri_key(from_address)
        if program_version is None:
            program_version = self._node.program_version
        if version_sign is None:
            version_sign = self._node.program_version_sign
        return self._pip.declareVersion(active_node, program_version, version_sign, pri_key, transaction_cfg)

    def get_proposal(self, proposal_type):
        proposal_list = self._node.pip.listProposal()['Ret']
        for proposal in proposal_list:
            if (proposal.get('ProposalType') == proposal_type) and (proposal["EndVotingBlock"] > self._node.platon.blockNumber):
                return proposal
        return None
