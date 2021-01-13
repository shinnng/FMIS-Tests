import pytest
from loguru import logger
from typing import List
from common.load_file import LoadFile
from common.connect import connect_web3
from env.node import NodeEnv
from lib.chain.genesis import to_genesis
from lib.chain.account import Account
from lib.tidb import Tidb
from lib.chain.client import Client
from lib.chain.node import ClientNode
from lib.chain.config import StakingConfig
from conf.config import ACCOUNT_TMP


def pytest_addoption(parser):
    parser.addoption("--genesis", action="store", help="genesis: the chain genesis file")
    parser.addoption("--config", action="store", help="config: the config file")


@pytest.fixture(scope="session", autouse=False)
def global_test_clients(request) -> List[List[Client]]:
    logger.add("./log/file_{time}.log", rotation="500 MB", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
    logger.info("start global_test_clients>>>>>>>>>>>>>>")
    genesis_file = request.config.getoption("--genesis")
    config_file = request.config.getoption("--config")

    account_tmp = ACCOUNT_TMP

    config = LoadFile(config_file).get_data()
    genesis_data = LoadFile(genesis_file).get_data()
    accounts = config["accounts"] + LoadFile(account_tmp).get_data() or []
    genesis = to_genesis(genesis_data)
    staking_cfg = StakingConfig("externalId", "nodeName", "website", "details")
    node_conf = config["node"]
    tidb_conf = config["tidb"]
    tidb = Tidb(tidb_conf["host"], tidb_conf["username"], tidb_conf["password"], database=tidb_conf['database'], port=tidb_conf["port"])

    account = Account(accounts, genesis.config.chainId)

    def gen_clients(nodes):
        clients = []
        for node in nodes:
            url = node["url"]
            web3 = connect_web3(url, genesis.config.chainId)
            env = NodeEnv(node, node_conf)
            client_node = ClientNode(web3, env)
            client = Client(client_node, staking_cfg, tidb, account, genesis)
            clients.append(client)
        return clients

    # consensus_clients = gen_clients(config["node"])
    consensus_clients = gen_clients(config["node"]["consensus"])
    noconsensus_clients = gen_clients(config["node"]["noconsensus"])
    yield consensus_clients, noconsensus_clients
    tidb.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # we only look at actual failing test calls, not setup/teardown
    if rep.when == "call" and not rep.passed:

        if 'global_test_env' in item.fixturenames:
            # download log in here
            pass
