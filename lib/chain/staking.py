class StakingMixin:
    """
    Used to initiate a Staking transaction,
    if you need to use the call method, please call ppos
    """

    def create_staking(self, typ, benifit_address, from_address, node_id=None, amount=None, program_version=None,
                       program_version_sign=None, bls_pubkey=None, bls_proof=None, transaction_cfg=None, reward_per=0):
        """
        Initiate Staking
        :param typ: Indicates whether the account free amount or the account's lock amount is used for staking, 0: free amount; 1: lock amount
        :param benifit_address: Income account for accepting block rewards and staking rewards
        :param node_id: The idled node Id (also called the candidate's node Id)
        :param amount: staking von (unit:von, 1LAT = 10**18 von)
        :param program_version: The real version of the program, admin_getProgramVersion
        :param program_version_sign: The real version of the program is signed, admin_getProgramVersion
        :param bls_pubkey: Bls public key
        :param bls_proof: Proof of bls, obtained by pulling the proof interface, admin_getSchnorrNIZKProve
        :param from_address: address for transaction
        :param transaction_cfg: Transaction basic configuration
              type: dict
              example:pip_cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        :param reward_per: Proportion of the reward share obtained from the commission, using BasePoint 1BP = 0.01%
        :return: if is need analyze return transaction result dict
                if is not need analyze return transaction hash
        """
        if node_id is None:
            node_id = self._node.node_id
        if amount is None:
            amount = self._economic.create_staking_limit
        if program_version is None:
            program_version = self._node.program_version
        if program_version_sign is None:
            program_version_sign = self._node.program_version_sign
        if bls_pubkey is None:
            bls_pubkey = self._node.blspubkey
        if bls_proof is None:
            bls_proof = self._node.schnorr_NIZK_prove
        pri_key = self._account.find_pri_key(from_address)
        return self._ppos.createStaking(typ, benifit_address, node_id, self._staking_cfg.external_id,
                                        self._staking_cfg.node_name,
                                        self._staking_cfg.website, self._staking_cfg.details, amount, program_version,
                                        program_version_sign,
                                        bls_pubkey, bls_proof, pri_key, reward_per, transaction_cfg=transaction_cfg)

    def edit_candidate(self, from_address, benifit_address, node_id=None, transaction_cfg=None, reward_per=0):
        """
        Modify staking information
        :param benifit_address: Income account for accepting block rewards and staking rewards
        :param node_id: The idled node Id (also called the candidate's node Id)
        :param from_address: address for transaction
        :param transaction_cfg: Transaction basic configuration
              type: dict
              example:pip_cfg = {
                  "gas":100000000,
                  "gasPrice":2000000000000,
                  "nonce":1,
              }
        :param reward_per: Proportion of the reward share obtained from the commission, using BasePoint 1BP = 0.01%
        :return: if is need analyze return transaction result dict
                if is not need analyze return transaction hash
        """
        if node_id is None:
            node_id = self._node.node_id
        pri_key = self._account.find_pri_key(from_address)
        return self._ppos.editCandidate(benifit_address, node_id, self._staking_cfg.external_id,
                                        self._staking_cfg.node_name,
                                        self._staking_cfg.website, self._staking_cfg.details,
                                        pri_key, reward_per, transaction_cfg=transaction_cfg)

    def increase_staking(self, typ, from_address, node_id=None, amount=None, transaction_cfg=None):
        """
        Increase staking
        :param typ: Indicates whether the account free amount or the account's lock amount is used for staking, 0: free amount; 1: lock amount
        :param node_id: The idled node Id (also called the candidate's node Id)
        :param amount: staking von (unit:von, 1LAT = 10**18 von)
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
        if node_id is None:
            node_id = self._node.node_id
        if amount is None:
            amount = self._economic.add_staking_limit
        pri_key = self._account.find_pri_key(from_address)
        return self._ppos.increaseStaking(typ, node_id, amount, pri_key, transaction_cfg=transaction_cfg)

    def withdrew_staking(self, from_address, node_id=None, transaction_cfg=None):
        """
        Withdrawal of staking (one-time initiation of all cancellations, multiple arrivals)
        :param node_id: The idled node Id (also called the candidate's node Id)
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
        if node_id is None:
            node_id = self._node.node_id
        pri_key = self._account.find_pri_key(from_address)
        return self._ppos.withdrewStaking(node_id, pri_key, transaction_cfg=transaction_cfg)

    def staking_block_number(self, node=None):
        """
        According to the node to obtain the amount of the deposit
        """
        if node is None:
            node = self._node
        stakinginfo = node.ppos.getCandidateInfo(node.node_id)
        staking_data = stakinginfo.get('Ret')
        stakingblocknum = staking_data.get('StakingBlockNum')
        return int(stakingblocknum)
