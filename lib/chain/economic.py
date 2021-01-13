from decimal import Decimal

from .utils import wait_block_number, get_pledge_list
from .genesis import Genesis
from .node import ClientNode
import math


class Economic:

    def __init__(self, genesis: Genesis, node: ClientNode):

        self.genesis = genesis

        self.node = node

        # Block rate parameter
        self.per_round_blocks = self.genesis.config.cbft.amount
        self.interval = int((self.genesis.config.cbft.period / self.per_round_blocks) / 1000)

        # Length of additional issuance cycle
        self.additional_cycle_time = self.genesis.economicModel.common.additionalCycleTime

        # Number of verification
        self.validator_count = self.genesis.economicModel.common.maxConsensusVals

        # Billing related
        # Billing cycle
        self.expected_minutes = self.genesis.economicModel.common.maxEpochMinutes

        # Minimum amount limit
        self.create_staking_limit = self.genesis.economicModel.staking.stakeThreshold
        # Minimum deposit amount
        # Minimum holding amount
        self.add_staking_limit = self.genesis.economicModel.staking.operatingThreshold
        # Minimum commission amount
        self.delegate_limit = self.add_staking_limit
        # unstaking freeze duration
        self.unstaking_freeze_ratio = self.genesis.economicModel.staking.unStakeFreezeDuration
        # ParamProposalVote_DurationSeconds
        self.pp_vote_settlement_wheel = self.genesis.economicModel.gov.paramProposalVoteDurationSeconds // self.settlement_size
        # slash blocks reward
        self.slash_blocks_reward = self.genesis.economicModel.slashing.slashBlocksReward
        # text proposal vote duration senconds
        self.tp_vote_settlement_wheel = self.genesis.economicModel.gov.textProposalVoteDurationSeconds // (
            self.interval * self.per_round_blocks * self.validator_count)

    @property
    def consensus_wheel(self):
        return (self.expected_minutes * 60) // (
                self.interval * self.per_round_blocks * self.validator_count)

    @property
    def consensus_size(self):
        return self.per_round_blocks * self.validator_count

    @property
    def settlement_size(self):
        return self.consensus_wheel * (self.interval * self.per_round_blocks * self.validator_count)

    def get_block_count_number(self, current_block=None, roundnum=1):
        """
        Get the number of blocks out of the verification node
        """
        if current_block is None:
            current_block = self.node.eth.blockNumber
        block_namber = self.consensus_size * roundnum
        count = 0
        for i in range(block_namber):
            if current_block > 0:
                node_id = self.node.eth.ecrecover(current_block)
                # node_id = get_pub_key(node.url, current_block)
                current_block = current_block - 1
                if node_id == self.node.node_id:
                    count = count + 1
            else:
                break
        return count

    def get_number_blocks_in_interval(self, roundnum=1):
        """
        Get the number of blocks produced by the specified interval of the node
        """
        tmp_current_block = self.node.eth.blockNumber
        last_end_block = int(tmp_current_block / self.settlement_size) * self.settlement_size
        block_number = self.settlement_size * roundnum
        count = 0
        for i in range(block_number):
            node_id = self.node.eth.ecrecover(last_end_block)
            last_end_block = last_end_block - 1
            if node_id == self.node.node_id:
                count = count + 1
        return count

    def calculate_delegate_reward(self, block_reward, staking_reward, reward=None):
        block_number = self.get_number_blocks_in_interval()
        if reward is None:
            reward = self.node.ppos.getCandidateInfo(self.node.node_id)["Ret"]["RewardPer"]
        return int(Decimal(str(staking_reward))*Decimal(str(reward))/Decimal(str(10000)) + Decimal(str(int(Decimal(str(block_reward))*Decimal(str(reward))/Decimal(str(10000))))) * Decimal(str(block_number)))

    def delegate_cumulative_income(self, block_reward, staking_reward, delegate_total_amount, delegate_amount, reward=None):
        entrusted_income = self.calculate_delegate_reward(block_reward, staking_reward, reward)
        current_commission_award = math.floor(Decimal(str(entrusted_income)) * Decimal(str(delegate_amount)) / Decimal(str(delegate_total_amount)))
        return current_commission_award

    def delegate_dividend_income(self, delegate_reward_total, delegate_total_amount, delegate_amount):
        current_commission_award = math.floor(Decimal(str(delegate_reward_total)) * Decimal(str(delegate_amount)) / Decimal(str(delegate_total_amount)))
        return current_commission_award

    def get_current_year_reward(self, verifier_num=None):
        """
        Get the first year of the block reward, pledge reward
        :return:
        """
        if verifier_num is None:
            verifier_list = get_pledge_list(self.node.ppos.getVerifierList)
            verifier_num = len(verifier_list)
        result = self.node.ppos.getPackageReward()
        block_reward = result['Ret']
        result = self.node.ppos.getStakingReward()
        staking_reward = int(Decimal(str(result['Ret'])) / Decimal(str(verifier_num)))
        return block_reward, staking_reward

    def get_settlement_switchpoint(self, number=0):
        """
        Get the last block of the current billing cycle
        :param node: node object
        :param number: number of billing cycles
        :return:
        """
        block_number = self.settlement_size * number
        tmp_current_block = self.node.eth.blockNumber
        current_end_block = math.ceil(tmp_current_block / self.settlement_size) * self.settlement_size + block_number
        return current_end_block

    def get_front_settlement_switchpoint(self, number=0):
        """
        Get a block height before the current billing cycle
        :param node: node object
        :param number: number of billing cycles
        :return:
        """
        block_num = self.settlement_size * (number + 1)
        current_end_block = self.get_settlement_switchpoint()
        history_block = current_end_block - block_num + 1
        return history_block

    def wait_settlement_blocknum(self, number=0):
        """
        Waiting for a billing cycle to settle
        :param node:
        :param number: number of billing cycles
        :return:
        """
        end_block = self.get_settlement_switchpoint(number)
        wait_block_number(self.node, end_block, self.interval)

    def get_annual_switchpoint(self):
        """
        Get the number of annual settlement cycles
        """
        annual_cycle = (self.additional_cycle_time * 60) // self.settlement_size
        annualsize = annual_cycle * self.settlement_size
        current_block = self.node.eth.blockNumber
        current_end_block = math.ceil(current_block / annualsize) * annualsize
        return annual_cycle, annualsize, current_end_block

    def wait_annual_blocknum(self):
        """
        Waiting for the end of the annual block high
        """
        annualcycle, annualsize, current_end_block = self.get_annual_switchpoint()
        current_block = self.node.eth.blockNumber
        differ_block = annualsize - (current_block % annualsize)
        annual_end_block = current_block + differ_block
        wait_block_number(self.node, annual_end_block, self.interval)

    def wait_consensus_blocknum(self, number=0):
        """
        Waiting for a consensus round to end
        """
        end_block = self.get_consensus_switchpoint(number)
        wait_block_number(self.node, end_block, self.interval)

    def get_consensus_switchpoint(self, number=0):
        """
        Get the specified consensus round high
        """
        block_number = self.consensus_size * number
        current_block = self.node.eth.blockNumber
        current_end_block = math.ceil(current_block / self.consensus_size) * self.consensus_size + block_number
        return current_end_block

    def get_report_reward(self, amount, penalty_ratio=None, proportion_ratio=None):
        if penalty_ratio is None:
            penalty_ratio = self.genesis.economicModel.slashing.slashFractionDuplicateSign
        if proportion_ratio is None:
            proportion_ratio = self.genesis.economicModel.slashing.duplicateSignReportReward
        penalty_reward = int(Decimal(str(amount)) * Decimal(str(penalty_ratio / 10000)))
        proportion_reward = int(Decimal(str(penalty_reward)) * Decimal(str(proportion_ratio / 100)))
        incentive_pool_reward = penalty_reward - proportion_reward
        return proportion_reward, incentive_pool_reward
