import math, time

import pytest
from loguru import logger

#  创建地址并转账后，使用自由金额进行非共识节点的质押操作--返回结果已解析
from lib.chain import assert_code, Decimal, get_block_count_number

gas_limit = 21000

#创建质押地址，收益地址，委托地址，并进行质押100万，委托10LAT，并等待2个结算周期进行退出质押操作，此时可查看节点收益
def test_trans_staking_unstaking(noconsensus_client):
    client = noconsensus_client
    staking_address, _ = client.account.generate_account(client.node.web3, client.economic.create_staking_limit * 5)
    logger.info("创建的质押地址address为: {}".format(staking_address))
    benefit_address, _ = client.account.generate_account(client.node.web3, 0)
    logger.info("创建的收益地址address2为: {}".format(benefit_address))
    delegate_address, _ = client.account.generate_account(client.node.web3, client.economic.delegate_limit * 2)
    logger.info("创建的委托地址address3为: {}".format(delegate_address))
    system_address = "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj"
    # staking_address = "lax150tlrn2p42sm264z05yulz5rc98sqsfz7cpy3e"
    # delegate_address = "lax1ldxpama6qh7f446ec6uzjutdxuzfvvcvxt6drz"
    # benefit_address = "lax13g0wphcym9wy0h3ztwdlu4407zhappmz39q7yj"
    client.account.sendTransaction(client.node.web3, "", system_address, staking_address, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(2000010, 'ether'))
    client.account.sendTransaction(client.node.web3, "", system_address, delegate_address, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(10, 'ether'))

    result = client.builtin_rpc.create_staking(0, benefit_address, staking_address, reward_per=1000)
    assert_code(result, 0)
    result = client.builtin_rpc.delegate(0, delegate_address)
    assert_code(result, 0)

    client.economic.wait_settlement_blocknum(1)
    client.economic.wait_consensus_blocknum()
    a, staking_reward = client.economic.get_current_year_reward()
    block_number = client.builtin_rpc.staking_block_number()
    result = client.builtin_rpc.withdrew_delegate(block_number, delegate_address)
    assert_code(result, 0)
    result = client.builtin_rpc.withdrew_staking(client.staking_address)
    assert_code(result, 0)
    number = get_block_count_number(client.node, 400)
    print("当前出块个数为：{}".format(number))
    block_reward = int(Decimal(str(number)) * Decimal(str(a)))
    print("当前交易的总出块奖励为{}以及总质押奖励为{}".format(block_reward, staking_reward))
    result = client.node.ppos.getVerifierList()
    print("获取验证人列表的信息{}".format(result))
    result = client.node.ppos.getCandidateInfo(client.node.node_id)
    print("获取当前节点的信息{}".format(result))
    result = client.node.ppos.getDelegateReward(delegate_address)
    print("获取委托者委托分红奖励{}".format(result))

#   赎回委托及退出质押
def test_get_reward(consensus_client):
    address = 'lax1duml6ur69z7fe99nc0j40scpqm0wrlddvqtvs3'
    block_number = 122358
    delegate_address = "lax1f4rrdsths6q0uh2x5de3tmh8s03jfj6430780c"
    node_id1 = "13915ba5e9f988d1438aab6b66828887c2445f746af799a679a153c2b7704e10d24500ba600ec53c259a859aa3544d1a225f26d38e0ab6f1b58db2847fe3a93b"
    node_id2 = "f8f7b7ec03b6fd58334df4fd565a26024a1c5d64868880803f63c6c3b06d3dabd051c3251549ccf186c3d83afce12fa0a32c2188872aafa620b10bd337ea2a64"
    node_id3 = "2d25f7686573602334589ac2e606a3743d34fcae0c7d34c6eadc01dbecd21f349d93ec227b2c43a5f61eab7fff1e0382e8a9f61a2cce9cf8eb0730a697a98159"
    node_id4 = "d3f54cf2fbcb06e372573079f432513f328dde846ceebcc8915ea1ea9abf91e4ffefe42dc42f411850c23e177e81271703bbc16add6754c7df1a9c6ac6cbe63f"
    client = consensus_client
    result = client.builtin_rpc.withdrew_delegate(block_number, delegate_address, node_id=node_id4, amount=10000000000000000000)
    assert_code(result, 0)
    res = client.node.eth.getBalance(address) - client.node.eth.getBalance(address, block_number+100)
    print("当前节点委托金：{}".format(res))
    result = client.builtin_rpc.withdrew_staking(address, node_id4)
    assert_code(result, 0)

#  领取奖励  且 赎回委托
def test_get_reward1(consensus_client):
    address = 'lax1qw5lqampcpkmj4vhe9c4ckqwqc2plmfth7va0y'
    block_number = 24827
    node_id1 = "5801350aa672441894c753f41e5c7c52b2a4374e7902e52f4a8cacdc33cd1a6ca63bdb7ecda710b5a6500bfb53bb80bd046aba63fc326f11a0971b91bfb1225a"
    node_id2 = "aef93e9cb7c4488de216f8ed12cad9ddecfd2150ae4cc6a5045ba286ce26276910cf8c6e4df633c2964160cc3bca8015cff2c55a41294e979767d5b0effb48b0"
    client = consensus_client
    # result = client.builtin_rpc.withdraw_delegate_reward("lax1zp7lcz9mju46eeqwlq85j8et7at23qhye4k2cs")
    # assert_code(result, 0)
    result = client.builtin_rpc.withdrew_delegate(block_number, address, node_id=node_id1, amount=10000000000000000000)
    assert_code(result, 0)
    res = client.node.eth.getBalance(address) - client.node.eth.getBalance(address, block_number+100)
    print("当前节点委托金：{}".format(res))

#  发起锁仓交易
def test_testricting(consensus_client):
    client = consensus_client
    from_address = "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj"
    account = "lax1yw9j8yj969ntvvws6ls0732yv67h4ek863k8cy"
    plan = [{'Epoch': 10, 'Amount': 200000000000000000000}]
    result = client.builtin_rpc.createRestrictingPlan(account, plan, from_address)
    # print(tx_hash)
    # logger.info(" create Restricting Plan transaction hash: {}".format(tx_hash))
    # result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)
    restricting_info = client.node.ppos.getRestrictingInfo(account)
    print(restricting_info)

#   使用锁仓金额进行质押，委托，解质押操作
def test_resrict_delegate(consensus_client):
    client = consensus_client
    from_address = "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj"
    restrict_address = "lax1yw9j8yj969ntvvws6ls0732yv67h4ek863k8cy"
    benefit_address = "lax1fghze73na8f7m9jrpatwwlt8xmdnl7pmygdyjk"
    plan = [{'Epoch': 10, 'Amount': 2000000000000000000000000}]
    result = client.builtin_rpc.createRestrictingPlan(restrict_address, plan, from_address)
    assert_code(result, 0)
    restricting_info = client.node.ppos.getRestrictingInfo(restrict_address)
    print("输出锁仓信息为：{}".format(restricting_info))
    client.builtin_rpc.create_staking(1, benefit_address, restrict_address, reward_per=5000)
    client.economic.wait_settlement_blocknum(8)
    result = client.builtin_rpc.withdrew_staking(client.staking_address)
    assert_code(result, 0)

def test_sss(noconsensus_client):
    """

    """
    client = noconsensus_client
    economic = client.economic
    node = client.node
    address, _ = client.account.generate_account(node.web3, economic.create_staking_limit * 3)
    benifit_address, _ = client.account.generate_account(node.web3, 0)
    delegate_address, _ = client.account.generate_account(node.web3, economic.delegate_limit * 2)
    result = client.builtin_rpc.create_staking(0, benifit_address, address, amount=economic.create_staking_limit * 2, reward_per=1000)
    assert_code(result, 0)
    result = client.builtin_rpc.delegate(0, delegate_address)
    assert_code(result, 0)
    economic.wait_settlement_blocknum()
    economic.wait_consensus_blocknum()
    result = client.builtin_rpc.withdrew_staking(address)
    assert_code(result, 0)
    block_reward, staking_reward = economic.get_current_year_reward()
    print(block_reward, staking_reward)
    economic.wait_settlement()
    settlement_block = economic.get_settlement_switchpoint() - economic.settlement_size()
    blocknum = economic.get_block_count_number(node, settlement_block, 10)
    block_reward_total = math.ceil(Decimal(str(block_reward)) * blocknum)
    delegate_block_reward = 0
    for i in range(blocknum):
        delegate_block = int(Decimal(str(block_reward)) * Decimal(str(10 / 100)))
        delegate_block_reward = delegate_block_reward + delegate_block
    node_block_reward = block_reward_total - delegate_block_reward
    print('node_block_reward', node_block_reward)
    reward_total = block_reward_total + staking_reward
    # delegate_block_reward = int(Decimal(str(block_reward_total)) * Decimal(str(10 / 100)))
    delegate_staking_reward = int(Decimal(str(staking_reward)) * Decimal(str(10 / 100)))
    delegate_reward_total = delegate_block_reward + delegate_staking_reward
    # node_block_reward = int(Decimal(str(block_reward_total)) * Decimal(str(90 / 100)))
    node_staking_reward = math.ceil(Decimal(str(staking_reward)) * Decimal(str(90 / 100)))
    print('node_staking_reward ', node_staking_reward)
    node_reward_total = node_staking_reward + node_block_reward
    logger.info("reward_total {}".format(reward_total))
    logger.info("delegate_reward {}".format(delegate_reward_total))
    logger.info("node_reward {}".format(node_reward_total))
    print(delegate_reward_total + node_reward_total)
    result = node.ppos.getDelegateReward(delegate_address)
    print("getDelegateReward", result)
    balance = node.eth.getBalance(benifit_address, settlement_block)
    print("benifit_balance", balance)
#   赎回委托
def test112(consensus_client):
    # res = consensus_client.node.ppos.getCandidateInfo('aef93e9cb7c4488de216f8ed12cad9ddecfd2150ae4cc6a5045ba286ce26276910cf8c6e4df633c2964160cc3bca8015cff2c55a41294e979767d5b0effb48b0')
    # print(res)
    #创建质押地址，收益地址，委托地址，并进行质押100万，委托10LAT
    a = 117649111088766073671642298000 * 1.25
    b = 94119288871012858937313838370
    c = a + b
    print(c)
    print(int(Decimal(str(c)) * Decimal(str(90 / 100))))
    d = 193532787741.020191189851580173 / 0.9
    f = (d - 94119288871.012858937313838370)
    print("出块数为：{}".format(f))

def test_trans_staking(noconsensus_client):
    client = noconsensus_client
    address, _ = client.account.generate_account(client.node.web3, client.economic.create_staking_limit * 2)
    logger.info("创建的质押地址address为: {}".format(address))
    address2, _ = client.account.generate_account(client.node.web3, 0)
    logger.info("创建的收益地址address2为: {}".format(address2))
    result = client.builtin_rpc.create_staking(0, address2, address)
    assert_code(result, 0)
    delegate_address, _ = client.account.generate_account(client.node.web3, client.economic.delegate_limit * 10)
    res = client.builtin_rpc.delegate(0, delegate_address)
    logger.info("创建的委托地址{}进行委托操作，结果为: {}".format(delegate_address, res))
    assert_code(result, 0)

#  创建地址并转账后，使用自由金额进行非共识节点的质押操作--返回结果未解析
def test_unanalyze_trans_staking(noconsensus_client_unanalyze):
    client = noconsensus_client_unanalyze
    address, _ = client.account.generate_account(client.node.web3, client.economic.create_staking_limit * 2)
    tx_hash = client.builtin_rpc.create_staking(0, address, address)
    logger.info("create staking hash : {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    print(result)

#  创建地址并转账后，使用锁仓金额进行非共识节点的质押操作--返回结果已解析
def test_trans_staking1(noconsensus_client, unstaking):
    client = noconsensus_client
    amount = client.economic.create_staking_limit * 2
    address, _ = client.account.generate_account(client.node.web3, client.node.web3.toWei(100, 'ether'))
    epoch = 1
    plan = [{'Epoch': epoch, 'Amount': amount}]
    tx_hash = client.builtin_rpc.createRestrictingPlan(address, plan, client.account.address_with_money)
    # assert_code(result, 0)
    logger.info("create staking hash : {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    print(result)
    benifit_address, _ = client.account.generate_account(client.node.web3, 0)
    client.builtin_rpc.create_staking(1, benifit_address, address)
    logger.info("创建的质押地址address为: {}".format(address))
    logger.info("创建的收益地址address2为: {}".format(benifit_address))

#  创建地址并转账后，使用锁仓金额进行非共识节点的质押操作--返回结果未解析
def test_unanalyze_trans_staking1(noconsensus_client_unanalyze):
    client = noconsensus_client_unanalyze
    address, _ = client.account.generate_account(client.node.web3, client.economic.create_staking_limit * 2)
    tx_hash = client.builtin_rpc.create_staking(1, address, address, reward_per=1000)
    logger.info("create staking hash : {}".format(tx_hash))
    result = client.node.platon.analyzeReceiptByHash(tx_hash)
    print(result)

# 获取当前各地址的余额及余额总计（系统账户，topool运营，topool节点）
def test_getBalance_inner(consensus_client):
    block = 6073
    client = consensus_client
    incentice_pool = "lax1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqrzpqayr"
    staking_address = "lax1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzlh5ge3"
    restricting_address = "lax1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqp3yp7hw"
    delegate_reward_address = "lax1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqxsakwkt"
    punishment_address = "lax1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqyrchd9x"
    print("激励池合约余额为：{}".format(client.node.eth.getBalance(incentice_pool, block)))
    print("委托奖励合约余额为：{}".format(client.node.eth.getBalance(delegate_reward_address, block)))
    print("质押合约余额为：{}".format(client.node.eth.getBalance(staking_address, block)))
    print("锁仓合约余额为：{}".format(client.node.eth.getBalance(restricting_address, block)))
    print("惩罚合约余额为：{}".format(client.node.eth.getBalance(punishment_address, block)))
    address1 = "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj"
    address2 = "lax12jn6835z96ez93flwezrwu4xpv8e4zatc4kfru"
    address3 = "lax1fyeszufxwxk62p46djncj86rd553skpptsj8v6"
    reserved = "lax1cm9yeqjpkxqgaw8waaxznjev5fyx5fqqkgc80c"
    print("lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj的账户余额为：{}".format(client.node.eth.getBalance(address1, block)))
    print("lax12jn6835z96ez93flwezrwu4xpv8e4zatc4kfru的账户余额为：{}".format(client.node.eth.getBalance(address2, block)))
    print("lax1fyeszufxwxk62p46djncj86rd553skpptsj8v6的账户余额为：{}".format(client.node.eth.getBalance(address3, block)))
    print("lax1cm9yeqjpkxqgaw8waaxznjev5fyx5fqqkgc80c：{}".format(client.node.eth.getBalance(reserved, block)))
    result = client.node.eth.getBalance(address1) + client.node.eth.getBalance(address2) + client.node.eth.getBalance(address3)
    res = client.node.web3.fromWei(result, 'ether')
    print("系统3个账户地址+预留账户的余额为：{}".format(res+result))
    topool_node1 = "lax1yw9j8yj969ntvvws6ls0732yv67h4ek863k8cy"
    topool_node2 = "lax16tzkxy23gqg0d5w3n77g2ppksnsykzz96gtm4e"
    topool_node3 = "lax10cs3z72f45fd89lhm6h6uq856893g599lxj553"
    topool_node4 = "lax1ksnrgp60rpw8s5l8ssahjrwdjryf7z53e07sh3"
    topool_node5 = "lax1xxe39tmj6v2ydc7ydatch0he0nzlagmx9acx5z"
    # print("topool节点1余额为：{}".format(client.node.eth.getBalance(topool_node1, block)))
    res1 = client.node.eth.getBalance(topool_node1, block) + client.node.eth.getBalance(topool_node2, block) + client.node.eth.getBalance(topool_node3, block)+ client.node.eth.getBalance(topool_node4, block)+client.node.eth.getBalance(topool_node5, block)
    print("topool节点1+2+3+4+5的总计余额为：{}".format(res1))
    topool_operation1 = "lax1mshcf7khenfzan6v69wn9q9j7v5n9d3ndr7u59"
    topool_operation2 = "lax1wy98638j97xup4e0py0edvc3jg9dvcuvae039r"
    topool_operation3 = "lax1wxfdpldyk2pc7fep5hrmh34lx9p9pfzzw4gtq2"
    topool_operation4 = "lax1kjrhr84slrdqffzye6mafe45uexd44cmgxcpm7"
    result = client.node.eth.getBalance(topool_operation1, block) + client.node.eth.getBalance(topool_operation2, block) + client.node.eth.getBalance(topool_operation3, block) + client.node.eth.getBalance(topool_operation4, block)
    res2 = client.node.web3.fromWei(result, 'ether')
    print("topool运营1+2+3+4的总计余额为：{}".format(res2))

#   查询各地址的余额及小计总和
def test_getBalance(consensus_client):
    client = consensus_client
    topool_node1 = "lax1mtguvg38fmdqz8gjucmj4d972qywuq7lars5zd"
    topool_node2 = "lax162llg2puqjunp8ljn0cp8z8sghq7utggexwymt"
    print(client.node.eth.getBalance(topool_node1))
    print(client.node.eth.getBalance(topool_node2))
    res1 = client.node.eth.getBalance(topool_node1) + client.node.eth.getBalance(topool_node2)
    print(res1)
    topool_operation1 = "lax1mshcf7khenfzan6v69wn9q9j7v5n9d3ndr7u59"
    topool_operation2 = "lax1wy98638j97xup4e0py0edvc3jg9dvcuvae039r"
    print(client.node.eth.getBalance(topool_operation1))
    print(client.node.eth.getBalance(topool_operation2))
    result = client.node.eth.getBalance(topool_operation1) + client.node.eth.getBalance(topool_operation2)
    res2 = client.node.web3.fromWei(result, 'ether')
    print(res2)

#   进行地址A的创建并转账操作，再进行A转账给B的转账操作
def test_get_transation_1(consensus_client):
    client = consensus_client
    address, _ = client.account.generate_account(client.node.web3, client.node.web3.toWei(2000, 'ether'))
    logger.info("创建的转账地址address为: {}".format(address))
    to_address = "lax1mshcf7khenfzan6v69wn9q9j7v5n9d3ndr7u59"
    receipt = client.account.sendTransaction(client.node.web3, "", address, to_address, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(1900, 'ether'))
    logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))
    result = client.tidb.tb_tx_ori_voucher(receipt.transactionHash.hex())
    assert result

#   从初始账户进行转账给到A地址，再由A地址转账给到B地址
def test_get_transation_2(consensus_client):
    client = consensus_client
    from_address = "lax1wy98638j97xup4e0py0edvc3jg9dvcuvae039r"
    receipt = client.account.sendTransaction(client.node.web3, "", "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj", from_address, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(10000, 'ether'))
    logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))
    client.tidb.tb_tx_ori_voucher(receipt.transactionHash.hex())
    to_address1 = "lax1mshcf7khenfzan6v69wn9q9j7v5n9d3ndr7u59"
    receipt1 = client.account.sendTransaction(client.node.web3, "", from_address, to_address1, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(1000, 'ether'))
    logger.info("transfer transaction hash：{}".format(receipt1.transactionHash.hex()))
    result = client.tidb.tb_tx_ori_voucher(receipt1.transactionHash.hex())
    assert result
    to_address2 = "lax1wxfdpldyk2pc7fep5hrmh34lx9p9pfzzw4gtq2"
    receipt2 = client.account.sendTransaction(client.node.web3, "", from_address, to_address2, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(2000, 'ether'))
    logger.info("transfer transaction hash：{}".format(receipt2.transactionHash.hex()))
    result = client.tidb.tb_tx_ori_voucher(receipt2.transactionHash.hex())
    assert result
    to_address3 = "lax1kjrhr84slrdqffzye6mafe45uexd44cmgxcpm7"
    receipt3 = client.account.sendTransaction(client.node.web3, "", from_address, to_address3, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(3000, 'ether'))
    logger.info("transfer transaction hash：{}".format(receipt3.transactionHash.hex()))
    result = client.tidb.tb_tx_ori_voucher(receipt3.transactionHash.hex())
    assert result

#   直接从超有钱账户对各地址进行转账操作
def test_get_transation_3(consensus_client):
    client = consensus_client
    from_address1 = "lax1vvljcsf2pgax3zd6wsy4u3p05cpw5pd50dkd0d"
    from_address2 = "lax1vhetgq823kgn2cvdjcrjnxyk4x2zk5cnzaxzsj"
    node_id1 = "5801350aa672441894c753f41e5c7c52b2a4374e7902e52f4a8cacdc33cd1a6ca63bdb7ecda710b5a6500bfb53bb80bd046aba63fc326f11a0971b91bfb1225a"
    node_id2 = "aef93e9cb7c4488de216f8ed12cad9ddecfd2150ae4cc6a5045ba286ce26276910cf8c6e4df633c2964160cc3bca8015cff2c55a41294e979767d5b0effb48b0"
    benefit_address = "lax1w5zf5ej8l75x4n5jjlpgj5h0vrk4xp765zl3m2"
    benefit_address2 = "lax1w7uuzedjprdvfz2d420a74vw2k6n35zy5zamx6"
    # receipt = client.account.sendTransaction(client.node.web3, "", "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj", from_address1, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(1000, 'ether'))
    # logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))
    # print("89的钱包地址余额为{}".format(client.node.eth.getBalance(from_address1)))
    # receipt = client.account.sendTransaction(client.node.web3, "", "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj", from_address2, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(1000, 'ether'))
    # logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))
    # print("89的钱包地址余额为{}".format(client.node.eth.getBalance(from_address2)))
    #
    # result = client.builtin_rpc.edit_candidate(from_address2, benefit_address, node_id2)
    # assert_code(result, 0)
    result = client.node.ppos.getCandidateInfo(node_id1)
    print("获取当前节点的信息{}".format(result))
    result = client.node.pip.listProposal()
    # print("提案列表：{}".format(result))
    # print("收钱的钱包地址余额为{}".format(client.node.eth.getBalance("lax1vr8v48qjjrh9dwvdfctqauz98a7yp5se77fm2e")))
    # print("出钱的钱包地址余额为{}".format(client.node.eth.getBalance("lax1vvljcsf2pgax3zd6wsy4u3p05cpw5pd50dkd0d")))

#    直接从A地址对B地址进行转账操作
def test_get_transation(consensus_client):
    client = consensus_client
    from_address = "lax1kjrhr84slrdqffzye6mafe45uexd44cmgxcpm7"
    to_address = "lax1fghze73na8f7m9jrpatwwlt8xmdnl7pmygdyjk"
    receipt1 = client.account.sendTransaction(client.node.web3, "", from_address, to_address, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(1000, 'ether'))
    logger.info("transfer transaction hash：{}".format(receipt1.transactionHash.hex()))
    result = client.tidb.tb_tx_ori_voucher(receipt1.transactionHash.hex())
    assert result

 #  委托操作
def test_delegate(consensus_client):
    client = consensus_client
    result = client.builtin_rpc.delegate(0, "lax1mshcf7khenfzan6v69wn9q9j7v5n9d3ndr7u59", node_id="5801350aa672441894c753f41e5c7c52b2a4374e7902e52f4a8cacdc33cd1a6ca63bdb7ecda710b5a6500bfb53bb80bd046aba63fc326f11a0971b91bfb1225a", amount=client.node.web3.toWei(100, 'ether'))
    logger.info("create delegate result : {}".format(result))
    assert result == 0

def test_getcandidateinfo(consensus_client):
    client = consensus_client
    result = client.node.ppos.getCandidateInfo("5801350aa672441894c753f41e5c7c52b2a4374e7902e52f4a8cacdc33cd1a6ca63bdb7ecda710b5a6500bfb53bb80bd046aba63fc326f11a0971b91bfb1225a")
    print(result)

#   统计当前所有的账户余额汇总表的数据
def test_total(consensus_client):
    block = 3257
    client = consensus_client
    incentice_pool = "lax1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqrzpqayr"
    staking_address = "lax1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzlh5ge3"
    restricting_address = "lax1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqp3yp7hw"
    delegate_reward_address = "lax1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqxsakwkt"
    punishment_address = "lax1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqyrchd9x"
    print("激励池合约余额为：{}".format(client.node.eth.getBalance(incentice_pool, block)))
    print("委托奖励合约余额为：{}".format(client.node.eth.getBalance(delegate_reward_address, block)))
    print("质押合约余额为：{}".format(client.node.eth.getBalance(staking_address, block)))
    print("锁仓合约余额为：{}".format(client.node.eth.getBalance(restricting_address, block)))
    print("惩罚合约余额为：{}".format(client.node.eth.getBalance(punishment_address, block)))
    result = client.node.eth.getBalance(incentice_pool, block) + client.node.eth.getBalance(staking_address, block) + client.node.eth.getBalance(restricting_address, block) + client.node.eth.getBalance(delegate_reward_address, block)
    res = client.node.web3.fromWei(result, 'ether')
    print("系统账户总余额为{}".format(res))
    address1 = "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj"
    address2 = "lax12jn6835z96ez93flwezrwu4xpv8e4zatc4kfru"
    address3 = "lax1fyeszufxwxk62p46djncj86rd553skpptsj8v6"
    founding_team = "lax1mwpefxfaad0yx6dn6a3n7hmhf2varwnaf7u3jf"  # 创始团队
    academic_fund = "lax18pr6ypt320scrgrf936hk2klgexu96qkp6zd2e"  # 学术基金
    ecological_funds = "lax1zp7lcz9mju46eeqwlq85j8et7at23qhye4k2cs"     #生态基金
    private_equity = "lax1fd07kwzrk7ksc36gq8ml5l9ac2dpnaveseqcp4"      #私募基金
    calculators_fund = "lax10gpn3nhvmhjkfvvhkpedt6trysxpzdnmqmxfhr"    #计算士基金
    reserved = "lax1cm9yeqjpkxqgaw8waaxznjev5fyx5fqqkgc80c"  # 预留
    print("lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj的账户余额为：{}".format(client.node.eth.getBalance(address1, block)))
    print("lax12jn6835z96ez93flwezrwu4xpv8e4zatc4kfru的账户余额为：{}".format(client.node.eth.getBalance(address2, block)))
    print("lax1fyeszufxwxk62p46djncj86rd553skpptsj8v6的账户余额为：{}".format(client.node.eth.getBalance(address3, block)))
    print("lax1cm9yeqjpkxqgaw8waaxznjev5fyx5fqqkgc80c预留账户余额为：{}".format(client.node.eth.getBalance(reserved, block)))
    result2 = client.node.eth.getBalance(address1, block) + client.node.eth.getBalance(address2, block) + client.node.eth.getBalance(address3, block)
    res2 = client.node.web3.fromWei(result2, 'ether')
    print("系统3个账户地址余额为：{}".format(res2))
    result3 = result2 + client.node.eth.getBalance(founding_team, block) + client.node.eth.getBalance(academic_fund, block) + client.node.eth.getBalance(ecological_funds, block) + client.node.eth.getBalance(private_equity, block) + client.node.eth.getBalance(calculators_fund, block) + client.node.eth.getBalance(reserved, block)
    res3 = client.node.web3.fromWei(result3, 'ether')
    print("基金账户总余额为：{}".format(res3))
    staking_fund = "lax1zqh5cy4cxg23lnr0x70gfk0zzcmzasyk0rpg7s"  # 基金会staking基金
    marketing_fund = "lax1zt48cr0chfm4pcfdczuheh9craw6jterttqnhe"  # 基金会做市基金
    market_fund = "lax14kgz4qwhm4s4la7a0j28mm9ku5h2amscg5dn9e"  # 基金会市场基金
    operation_fund = "lax1fghze73na8f7m9jrpatwwlt8xmdnl7pmygdyjk"  # 基金会运营基金
    result4 = client.node.eth.getBalance(staking_fund, block)+client.node.eth.getBalance(marketing_fund, block)+client.node.eth.getBalance(market_fund, block)+client.node.eth.getBalance(operation_fund, block)
    res4 = client.node.web3.fromWei(result4, 'ether')
    print("运营账户总余额为：{}".format(res4))
    topool_node1 = "lax1yw9j8yj969ntvvws6ls0732yv67h4ek863k8cy"
    topool_node2 = "lax16tzkxy23gqg0d5w3n77g2ppksnsykzz96gtm4e"
    topool_node3 = "lax10cs3z72f45fd89lhm6h6uq856893g599lxj553"
    topool_node4 = "lax1ksnrgp60rpw8s5l8ssahjrwdjryf7z53e07sh3"
    topool_node5 = "lax1xxe39tmj6v2ydc7ydatch0he0nzlagmx9acx5z"
    result5 = client.node.eth.getBalance(topool_node1, block) + client.node.eth.getBalance(topool_node2,block) + client.node.eth.getBalance(topool_node3, block) + client.node.eth.getBalance(topool_node4, block) + client.node.eth.getBalance(topool_node5, block)
    res5 = client.node.web3.fromWei(result5, 'ether')
    print("topool节点1+2+3+4+5的总计余额为：{}".format(res5))
    topool_operation1 = "lax1mshcf7khenfzan6v69wn9q9j7v5n9d3ndr7u59"
    topool_operation2 = "lax1wy98638j97xup4e0py0edvc3jg9dvcuvae039r"
    topool_operation3 = "lax1wxfdpldyk2pc7fep5hrmh34lx9p9pfzzw4gtq2"
    topool_operation4 = "lax1kjrhr84slrdqffzye6mafe45uexd44cmgxcpm7"
    result6 = client.node.eth.getBalance(topool_operation1, block) + client.node.eth.getBalance(topool_operation2,block) + client.node.eth.getBalance(topool_operation3, block) + client.node.eth.getBalance(topool_operation4, block)
    res6 = client.node.web3.fromWei(result6, 'ether')
    print("topool运营1+2+3+4的总计余额为：{}".format(res6))
    print("节点账户总余额为：{}".format(res5+res6))
    external_accounts = "lax1t0cu56ykcnf5dzq7keud8ush85ldd24yxcy6ew"
    result7 = client.node.eth.getBalance(external_accounts, block)
    res7 = client.node.web3.fromWei(result7, 'ether')
    print("外部账户地址余额为：{}".format(res7))
    external_accounts_value = 0
    resu = res+res3+res4+res5+res6+res7
    result_total = Decimal(str(external_accounts_value)) + resu
    print("总计所有内部账户余额为：{}".format(result_total))

#   发起版本声明：转账后+质押+发起版本提案+解除质押
def test_declare(noconsensus_client):
    client = noconsensus_client
    system_address = "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj"
    staking_address = "lax1duml6ur69z7fe99nc0j40scpqm0wrlddvqtvs3"
    benefit_address = "lax10sg2j3s0lgh4s2wc6u0kwthw99x0kd48z87kxe"
    receipt = client.account.sendTransaction(client.node.web3, "", system_address, staking_address, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(2000010, 'ether'))
    logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))

    result = client.builtin_rpc.create_staking(0, benefit_address, staking_address, amount= client.economic.create_staking_limit * 2)
    assert_code(result, 0)
    result = client.node.ppos.getCandidateInfo(client.node.node_id)
    print("获取当前节点的信息{}".format(result))

    client.economic.wait_settlement_blocknum()
    # client.economic.wait_consensus_blocknum()
    result = client.node.eth.getBalance(benefit_address)
    print("收益地址的余额为：{}".format(result))
    result = client.builtin_rpc.declareVersion(client.node.node_id, staking_address)
    assert_code(result, 0)

    result = client.builtin_rpc.withdrew_staking(staking_address, client.node.node_id)
    assert_code(result, 0)

#   发起版本提案：转账后+质押+发起版本提案+解除质押
def test_submit_version_proposal(noconsensus_client):
    client = noconsensus_client
    system_address = "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj"
    staking_address = "lax1duml6ur69z7fe99nc0j40scpqm0wrlddvqtvs3"
    benefit_address = "lax10sg2j3s0lgh4s2wc6u0kwthw99x0kd48z87kxe"
    receipt = client.account.sendTransaction(client.node.web3, "", system_address, staking_address, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(2000010, 'ether'))
    logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))

    result = client.builtin_rpc.create_staking(0, benefit_address, staking_address)
    assert_code(result, 0)
    result = client.node.ppos.getCandidateInfo(client.node.node_id)
    print("获取当前节点的信息{}".format(result))

    client.economic.wait_settlement_blocknum()
    client.economic.wait_consensus_blocknum()
    result = client.node.eth.getBalance(benefit_address)
    print("收益地址的余额为：{}".format(result))
    tx_hash = client.builtin_rpc.submitVersion(client.node.node_id, str(time.time()), client.builtin_rpc.pip_cfg.version5, '1', staking_address, transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    logger.info('提交版本提案hash: {}'.format(tx_hash))
    result = client.node.eth.analyzeReceiptByHash(tx_hash)
    assert_code(result, 0)

    result = client.builtin_rpc.withdrew_staking(staking_address, client.node.node_id)
    assert_code(result, 0)

#   发起文本提案：转账后+质押+发起版本提案+解除质押
def test_submit_text_proposal(noconsensus_client):
    client = noconsensus_client
    system_address = "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj"
    staking_address = "lax1duml6ur69z7fe99nc0j40scpqm0wrlddvqtvs3"
    benefit_address = "lax10sg2j3s0lgh4s2wc6u0kwthw99x0kd48z87kxe"
    receipt = client.account.sendTransaction(client.node.web3, "", system_address, staking_address, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(2000010, 'ether'))
    logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))

    result = client.builtin_rpc.create_staking(0, benefit_address, staking_address, amount=client.economic.create_staking_limit * 3)
    assert_code(result, 0)
    result = client.node.ppos.getCandidateInfo(client.node.node_id)
    print("获取当前节点的信息{}".format(result))

    client.economic.wait_settlement_blocknum()
    client.economic.wait_consensus_blocknum()
    result = client.node.eth.getBalance(benefit_address)
    print("收益地址的余额为：{}".format(result))
    result = client.node.ppos.getVerifierList()
    print("获取验证人列表的信息{}".format(result))
    result = client.builtin_rpc.submitText(client.node.node_id, str(time.time()), staking_address, transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    assert_code(result, 0)

    result = client.builtin_rpc.withdrew_staking(staking_address, client.node.node_id)
    assert_code(result, 0)

#   发起参数提案：转账后+质押+发起版本提案+解除质押
def test_submit_param_proposal(noconsensus_client):
    client = noconsensus_client
    system_address = "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj"
    staking_address = "lax1duml6ur69z7fe99nc0j40scpqm0wrlddvqtvs3"
    benefit_address = "lax10sg2j3s0lgh4s2wc6u0kwthw99x0kd48z87kxe"
    receipt = client.account.sendTransaction(client.node.web3, "", system_address, staking_address, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(2000010, 'ether'))
    logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))

    result = client.builtin_rpc.create_staking(0, benefit_address, staking_address, amount=client.economic.create_staking_limit * 2)
    assert_code(result, 0)
    result = client.node.ppos.getCandidateInfo(client.node.node_id)
    print("获取当前节点的信息{}".format(result))


    client.economic.wait_settlement_blocknum()
    client.economic.wait_consensus_blocknum()
    result = client.node.eth.getBalance(benefit_address)
    print("收益地址的余额为：{}".format(result))
    result = client.node.ppos.getVerifierList()
    print("获取验证人列表的信息{}".format(result))
    result = client.builtin_rpc.submitParam(client.node.node_id, str(time.time()), 'slashing', 'slashBlocksReward', '4', staking_address, transaction_cfg=client.builtin_rpc.pip_cfg.transaction_cfg)
    assert_code(result, 0)

    result = client.builtin_rpc.withdrew_staking(staking_address, client.node.node_id)
    assert_code(result, 0)

#   发起锁仓计划，使用锁仓金额进行质押，委托，解除委托，退出质押
def test_restrict_staking_delegate1(noconsensus_client):
    client = noconsensus_client
    system_address = "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj"
    staking_address = "lax1duml6ur69z7fe99nc0j40scpqm0wrlddvqtvs3"
    benefit_address = "lax10sg2j3s0lgh4s2wc6u0kwthw99x0kd48z87kxe"
    delegate_address = "lax1f4rrdsths6q0uh2x5de3tmh8s03jfj6430780c"
    client.account.sendTransaction(client.node.web3, "", system_address, staking_address, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(10, 'ether'))
    client.account.sendTransaction(client.node.web3, "", system_address, delegate_address, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(10, 'ether'))
    plan1 = [{'Epoch': 2, 'Amount': 2000000000000000000000000}]
    result = client.builtin_rpc.createRestrictingPlan(staking_address, plan1, system_address)
    assert_code(result, 0)
    restricting_info = client.node.ppos.getRestrictingInfo(staking_address)
    print("输出质押地址锁仓信息为：{}".format(restricting_info))
    time.sleep(2)
    plan2 = [{'Epoch': 2, 'Amount': 10000000000000000000}]
    result = client.builtin_rpc.createRestrictingPlan(delegate_address, plan2, system_address)
    assert_code(result, 0)
    restricting_info = client.node.ppos.getRestrictingInfo(staking_address)
    print("输出锁仓地址锁仓信息为：{}".format(restricting_info))

    result = client.builtin_rpc.create_staking(1, benefit_address, staking_address)
    assert_code(result, 0)
    result = client.node.ppos.getCandidateInfo(client.node.node_id)
    print("输出当前验证节点的信息", result)
    result = client.builtin_rpc.delegate(1, delegate_address)
    assert_code(result, 0)

    client.economic.wait_settlement_blocknum(1)
    client.economic.wait_consensus_blocknum()

    block_number = client.builtin_rpc.staking_block_number()
    result = client.builtin_rpc.withdrew_delegate(block_number, delegate_address)
    assert_code(result, 0)

    result = client.builtin_rpc.withdrew_staking(staking_address, client.node.node_id)
    assert_code(result, 0)

#   发起锁仓计划
def test_restrict_1(consensus_client):
    client = consensus_client
    system_address = "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj"
    staking_address = "lax1vvljcsf2pgax3zd6wsy4u3p05cpw5pd50dkd0d"
    plan = [{'Epoch': 10, 'Amount': 20000000000000000000000000}]
    result = client.builtin_rpc.createRestrictingPlan(staking_address, plan, system_address)
    assert_code(result, 0)
    restricting_info = client.node.ppos.getRestrictingInfo(staking_address)
    print("输出质押地址锁仓信息为：{}".format(restricting_info))

# #   低出块和双签交易发送
# def test_low_block_double_signed(noconsensus_client):
#     client = noconsensus_client
#     client.economic.
#     pass

def test_sdsd(consensus_client):
    client = consensus_client
    system_address = "lax184zj2xdms82dvg5ypacsk48qw3ch0q9rtfrmp3"
    staking_address = "lax1382h5d3l9t72fclxea924wnxw0xn8q5j06ex70"
    plan = [{'Epoch': 1, 'Amount': 20000000000000000000000000}]
    result = client.builtin_rpc.createRestrictingPlan(staking_address, plan, system_address)
    assert_code(result, 0)
    restricting_info = client.node.ppos.getRestrictingInfo(staking_address)
    print("输出质押地址锁仓信息为：{}".format(restricting_info))

def test_sdsd(consensus_client):
    client = consensus_client
    system_address = "lax184zj2xdms82dvg5ypacsk48qw3ch0q9rtfrmp3"
    staking_address = "lax1s4u4p9j95lh72a2c0ttj48ntd58s45resjgtza"
    benefit_address = "lax10h68pwlzxa46ndv4fjefux8en2ly4hfhw9qw7r"
    delegate_address = "lax1vvljcsf2pgax3zd6wsy4u3p05cpw5pd50dkd0d"
    client.account.sendTransaction(client.node.web3, "", system_address, staking_address, client.node.eth.gasPrice, gas_limit, client.node.web3.toWei(1000005, 'ether'))
    res = client.builtin_rpc.create_staking(1, benefit_address, staking_address)
    assert_code(res, 0)
    result = client.node.ppos.getCandidateInfo()
    print("输出当前验证节点的信息", result)
    # result = client.builtin_rpc.delegate(1, delegate_address)
    # assert_code(result, 0)

@pytest.fixture()
def test_course(noconsensus_client):
    client = noconsensus_client
    system_address = "lax196278ns22j23awdfj9f2d4vz0pedld8au6xelj"
    staking_address = "lax1duml6ur69z7fe99nc0j40scpqm0wrlddvqtvs3"
    benefit_address = "lax10sg2j3s0lgh4s2wc6u0kwthw99x0kd48z87kxe"
    delegate_address = "lax1f4rrdsths6q0uh2x5de3tmh8s03jfj6430780c"
    staking_value = client.node.eth.getBalance(staking_address)
    delegate_value = client.node.eth.getBalance(delegate_address)
    print("当前系统地址余额为：{}".format(client.node.eth.getBalance(system_address)))
    print("当前质押地址余额为：{}".format(staking_value))
    print("当前系统地址余额为：{}".format(client.node.eth.getBalance(benefit_address)))
    print("当前系统地址余额为：{}".format(delegate_value))
    if staking_address < client.economic.create_staking_limit:
        client.node.eth.sendTransaction(client.node.web3, "", system_address, staking_address, client.node.eth.gasPrice,gas_limit, client.node.web3.toWei(1000005, 'ether'))
    result = client.builtin_rpc.create_staking(0, benefit_address, staking_address)
    assert_code(result, 0)
    result = client.node.ppos.getCandidateInfo(client.node.node_id)
    assert result['Ret']['Shares'] == client.economic.create_staking_limit
    staking_block_num = result['Ret']['StakingBlockNum']

    if delegate_address < client.economic.delegate_limit:
        client.node.eth.sendTransaction(client.node.web3, "", system_address, staking_address, client.node.eth.gasPrice,
                                        gas_limit, client.node.web3.toWei(20, 'ether'))
    result = client.builtin_rpc.delegate(1, delegate_address)
    assert_code(result, 0)
    result = client.node.ppos.getDelegateInfo(staking_block_num, delegate_address, client.node.node_id)
    assert result['Ret']['']
