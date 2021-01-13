import math

from lib.chain import assert_code, Decimal, logger


# def block_reward_total(block_reward, blocknum):
#     block_reward_total = math.ceil(Decimal(str(block_reward)) * blocknum)
#     delegate_block_reward = 0
#     for i in range(blocknum):
#         delegate_block = int(Decimal(str(block_reward)) * Decimal(str(10 / 100)))
#         delegate_block_reward = delegate_block_reward + delegate_block
#     node_block_reward = block_reward_total - delegate_block_reward
#     print("节点出块奖励为{}".format(node_block_reward))
#     print("委托出块奖励为{}".format(delegate_block_reward))
#     return block_reward_total, node_block_reward, delegate_block_reward
#
#
# def test_sss(noconsensus_client):
#     """
#
#     """
#     client = noconsensus_client
#     economic = client.economic
#     node = client.node
#     address, _ = client.account.generate_account(node.web3, economic.create_staking_limit * 2)
#     print("创建的质押地址为{}".format(address))
#     benifit_address, _ = client.account.generate_account(node.web3, 0)
#     print("创建的收益地址为{}".format(benifit_address))
#     delegate_address, _ = client.account.generate_account(node.web3, economic.delegate_limit * 2)
#     print("创建的委托地址为{}".format(delegate_address))
#     result = client.builtin_rpc.create_staking(0, benifit_address, address, reward_per=1000)
#     assert_code(result, 0)
#     result = client.builtin_rpc.delegate(0, delegate_address)
#     assert_code(result, 0)
#     economic.wait_settlement_blocknum()
#     economic.wait_consensus_blocknum()
#     result = client.builtin_rpc.withdrew_staking(client.staking_address)
#     assert_code(result, 0)
#     first_block_reward, first_staking_reward = economic.get_current_year_reward()
#     print("第一个结算周期节点出块奖励为{},节点质押奖励为{}".format(first_block_reward, first_staking_reward))
#     economic.wait_settlement_blocknum()
#     economic.wait_consensus_blocknum()
#     second_block_reward, second_staking_reward = economic.get_current_year_reward()
#     print("第二个结算周期节点出块奖励为{},节点质押奖励为{}".format(second_block_reward, second_staking_reward))
#
#     first_settlement_block = economic.get_settlement_switchpoint() - economic.settlement_size
#     first_blocknum = economic.get_block_count_number(first_settlement_block, 10)
#     print("第一个结算周期的出块数{}".format(first_blocknum))
#     economic.wait_settlement_blocknum()
#     economic.wait_consensus_blocknum()
#     second_settlement_block = economic.get_settlement_switchpoint() - economic.settlement_size
#     second_blocknum = economic.get_block_count_number(second_settlement_block, 20)
#     print("第一个结算周期的出块数{}".format(second_blocknum - first_blocknum))
#     first_block_reward_total, first_node_block_reward, first_delegate_block_reward = block_reward_total(first_block_reward, first_blocknum)
#     print("第一个结算周期总出块奖励 {}".format(first_block_reward_total))
#     print("第一个结算周期节点出块奖励 {}".format(first_node_block_reward))
#     print("第一个结算周期委托者出块奖励 {}".format(first_delegate_block_reward))
#     first_reward_total = first_block_reward_total + first_staking_reward
#     print("第一个结算周期总奖励 {}".format(first_reward_total))
#     delegate_staking_reward = int(Decimal(str(first_staking_reward)) * Decimal(str(10 / 100)))
#     print("第一个结算周期委托者质押奖励 {}".format(delegate_staking_reward))
#     delegate_reward_total = first_delegate_block_reward + delegate_staking_reward
#     print("第一个结算周期委托者总奖励 {}".format(delegate_reward_total))
#     node_staking_reward = math.ceil(Decimal(str(first_staking_reward)) * Decimal(str(90 / 100)))
#     print("第一个结算周期节点质押奖励 {}".format(node_staking_reward))
#     node_reward_total = node_staking_reward + first_node_block_reward
#     print("第一个结算周期节点总奖励 {}".format(node_reward_total))
#
#     second_block_reward_total, second_node_block_reward, second_delegate_block_reward = block_reward_total(second_block_reward, second_blocknum - first_blocknum)
#     print("第二个结算周期总出块奖励 {}".format(second_block_reward_total))
#     print("第二个结算周期节点出块奖励 {}".format(second_node_block_reward))
#     print("第二个结算周期委托者出块奖励 {}".format(second_delegate_block_reward))
#     print("第一个 + 第二个结算周期总奖励 {}".format(first_reward_total + second_block_reward_total))
#     print("第一个 + 第二个结算周期节点出块奖励 {}".format(first_node_block_reward + second_node_block_reward))
#
#     balance = node.eth.getBalance(benifit_address, second_settlement_block)
#     print("收益地址余额", balance)
#     result = client.node.ppos.getCandidateInfo(client.node.node_id)
#     print("获取当前节点的信息{}".format(result))
#     result = client.node.ppos.getDelegateReward(delegate_address)
#     print("获取委托者委托分红奖励{}".format(result))

import random

#

x = input('输入x值： ')
y = input('输入y值：')

temp = x
x = y
y = temp

print("x的值为{}，y的值为{}".format(x, y))

