import pytest
import time
from lib.chain.client import Client
from typing import List
from loguru import logger


# @pytest.fixture()
# def duplicate_sign_node(request):
#     config_file = request.config.getoption("--config")
#     config = LoadFile(config_file).get_data()
#     duplicate_sign = config["duplicate_sign"]
#     web3 = connect_web3(duplicate_sign["url"])
#     node = ClientNode(web3)
#     setattr(node, "nodekey", duplicate_sign["nodekey"])
#     setattr(node, "blsprikey", duplicate_sign["blsprikey"])
#     yield node


@pytest.fixture()
def consensus_client(global_test_clients) -> Client:
    return global_test_clients[0][0]


@pytest.fixture()
def consensus_clients(global_test_clients) -> List[Client]:
    return global_test_clients[0]


@pytest.fixture()
def consensus_client_unanalyze(consensus_client) -> Client:
    consensus_client.node.ppos.need_analyze = False
    consensus_client.node.pip.need_analyze = False
    yield consensus_client
    consensus_client.node.ppos.need_analyze = True
    consensus_client.node.pip.need_analyze = True


@pytest.fixture()
def noconsensus_client_unanalyze(noconsensus_client) -> Client:
    noconsensus_client.node.ppos.need_analyze = False
    noconsensus_client.node.pip.need_analyze = False
    yield noconsensus_client
    noconsensus_client.node.ppos.need_analyze = True
    noconsensus_client.node.pip.need_analyze = True


@pytest.fixture()
def noconsensus_clients(global_test_clients) -> List[Client]:
    noconsensus_clients = global_test_clients[1]
    print(noconsensus_clients[0].node.ppos.getCandidateList())
    withdrew_staking_list = []
    for client in noconsensus_clients:
        if isinstance(client.node.candidate, dict):
            withdrew_staking_list.append(client)
    if withdrew_staking_list:
        withdrew_staking_all(withdrew_staking_list)
        withdrew_staking_list[0].economic.wait_settlement_blocknum(2)
        return noconsensus_clients
    return noconsensus_clients



@pytest.fixture()
def noconsensus_clients_unanalyze(noconsensus_clients) -> List[Client]:
    for noconsensus_client in noconsensus_clients:
        noconsensus_client.node.ppos.need_analyze = False
        noconsensus_client.node.pip.need_analyze = False
    yield noconsensus_clients
    for noconsensus_client in noconsensus_clients:
        noconsensus_client.node.ppos.need_analyze = False
        noconsensus_client.node.pip.need_analyze = False


@pytest.fixture()
def noconsensus_client(global_test_clients) -> Client:
    noconsensus_clients = global_test_clients[1]
    if is_has_noconsensus_client(noconsensus_clients):
        return get_noconsensus_client(noconsensus_clients)

    withdrew_staking_all(noconsensus_clients)
    return wait_get_noconsensus_client(noconsensus_clients)


@pytest.fixture()
def staking_client(noconsensus_client_unanalyze):
    amount = noconsensus_client_unanalyze.economic.create_staking_limit * 3
    address, _ = noconsensus_client_unanalyze.account.generate_account(noconsensus_client_unanalyze.node.web3, amount)
    tx_hash = noconsensus_client_unanalyze.builtin_rpc.create_staking(0, address, address, amount=noconsensus_client_unanalyze.economic.create_staking_limit * 2, reward_per=1000)
    logger.info("create staking hash : {}".format(tx_hash))
    result = noconsensus_client_unanalyze.node.platon.analyzeReceiptByHash(tx_hash)
    setattr(noconsensus_client_unanalyze, "staking_hash", tx_hash)
    setattr(noconsensus_client_unanalyze, "staking_result", result)
    yield noconsensus_client_unanalyze
    noconsensus_client_unanalyze.builtin_rpc.withdrew_staking(address)


@pytest.fixture()
def delegate_client(staking_client):
    staking = staking_client.node.ppos.getCandidateInfo(staking_client.node.node_id)
    if staking["Ret"]["DelegateTotalHes"] > 0 or staking["Ret"]["DelegateTotal"] > 0:
        return staking_client
    amount = staking_client.economic.delegate_limit * 2
    address, _ = staking_client.account.generate_account(staking_client.node.web3, amount)
    tx_hash = staking_client.builtin_rpc.delegate(0, address, staking_client.node.node_id)
    result = staking_client.node.platon.analyzeReceiptByHash(tx_hash)
    setattr(staking_client, "delegate_hash", tx_hash)
    setattr(staking_client, "delegate_address", address)
    setattr(staking_client, "delegate_result", result)
    return staking_client


@pytest.fixture()
def unstaking(noconsensus_client_unanalyze):
    logger.info("case execution completed")
    yield
    if noconsensus_client_unanalyze.node.is_candidate:
        noconsensus_client_unanalyze.builtin_rpc.withdrew_staking(noconsensus_client_unanalyze.staking_address)


@pytest.fixture()
def unstaking_all(noconsensus_clients_unanalyze):
    logger.info("case execution completed")
    yield
    print(noconsensus_clients_unanalyze[0].node.ppos.getCandidateList())
    withdrew_staking_list = []
    for client in noconsensus_clients_unanalyze:
        if isinstance(client.node.candidate, dict):
            withdrew_staking_list.append(client)
    if withdrew_staking_list:
        withdrew_staking_all(withdrew_staking_list)
        withdrew_staking_list[0].economic.wait_settlement_blocknum(2)



def wait_get_noconsensus_client(clients: List[Client]):
    client = clients[0]
    node = client.node
    switch_point = client.economic.genesis.economicModel.staking.unStakeFreezeDuration
    end_point_blocknumber = client.economic.get_settlement_switchpoint(switch_point) + 10
    current_blocknumber = node.platon.blockNumber
    use_time = 0
    timeout = (end_point_blocknumber - current_blocknumber) * client.economic.interval
    interval = 3
    while current_blocknumber < end_point_blocknumber:
        if is_has_noconsensus_client(clients):
            return get_noconsensus_client(clients)
        time.sleep(interval)
        use_time += interval
        if use_time > timeout:
            break
        current_blocknumber = client.node.platon.blockNumber
    raise Exception("Not to exist noconsensus")


def is_has_noconsensus_client(clients: List[Client]) -> bool:
    for client in clients:
        if not client.node.is_candidate:
            return True
    return False


def get_noconsensus_client(clients: List[Client]) -> Client:
    for client in clients:
        if not client.node.is_candidate:
            logger.info("Get node: {}".format(client.node.node_id))
            return client


def withdrew_staking_all(clients: List[Client]):
    logger.info("restart node >>>>")
    for client in clients:
        client.builtin_rpc.withdrew_staking(client.node.staking_address)
