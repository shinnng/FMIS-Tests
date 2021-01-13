import time
import pytest
from loguru import logger
from pytest import fixture
from alaya import Web3

from lib.chain import assert_voucher_result
from lib.chain.config import EconomicConfig

contract_code = ""
contract_func = ""
LAT_1 = Web3.toWei(1, "ether")
LAT_10 = Web3.toWei(10, "ether")
LAT_100 = Web3.toWei(100, "ether")
# send_address = EconomicConfig.REMAIN_ACCOUNT_ADDRESS
gas_limit = 21000


def transfer(consensus_client):
    amount = 0
    address, _ = consensus_client.account.generate_account(consensus_client.node.web3, amount)
    return amount, address


def assert_balance(client, from_address, to_address):
    client.assert_balance(from_address)
    client.assert_balance(to_address)


def test_transfer_one_to_one(consensus_client):
    """
    一对一转账
    """
    client = consensus_client
    address, _ = client.account.generate_account(client.node.web3, 0)
    amount = LAT_10
    receipt = client.account.sendTransaction(client.node.web3, "", client.account.address_with_money, address, client.node.eth.gasPrice, gas_limit, amount)
    logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))
    result = client.tidb.tb_tx_ori_voucher(receipt.transactionHash.hex())
    assert_voucher_result(result, 1, 9999)
    assert_balance(client, client.account.address_with_money, address)
    print()
    # client.assert_balance(address)


def test_transfer_contuine(consensus_client):
    """
    一对一转账-多次
    """
    client = consensus_client
    amount, address = transfer(client)
    receipt1 = client.account.sendTransaction(client.node.web3, "", client.account.address_with_money, address, client.node.eth.gasPrice, gas_limit, LAT_1)
    logger.info("transfer transaction hash：{}".format(receipt1.transactionHash.hex()))
    receipt2 = client.account.sendTransaction(client.node.web3, "", client.account.address_with_money, address, client.node.eth.gasPrice, gas_limit, LAT_1)
    logger.info("transfer transaction hash：{}".format(receipt2.transactionHash.hex()))
    result = client.tidb.tb_tx_ori_voucher(receipt1.transactionHash.hex())
    assert result
    result = client.tidb.tb_tx_ori_voucher(receipt2.transactionHash.hex())
    assert result
    assert_balance(client, client.account.address_with_money, address)


def test_transfer_one2much(consensus_client):
    """
    一对多转账
    """
    client = consensus_client
    amount, address1 = transfer(consensus_client)
    amount, address2 = transfer(consensus_client)
    to_address_list = [address1, address2]
    for to_address in to_address_list:
        receipt = client.account.sendTransaction(client.node.web3, "", client.account.address_with_money, to_address, client.node.eth.gasPrice, gas_limit, LAT_1)
        logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))
        result = client.tidb.tb_tx_ori_voucher(receipt.transactionHash.hex())
        assert result
    assert_balance(client, client.account.address_with_money, address1)
    assert_balance(client, client.account.address_with_money, address2)


def test_transfer_much2one(consensus_client):
    """
    多对一转账
    """
    client = consensus_client
    send_address, _ = client.account.generate_account(client.node.web3, LAT_10)
    amount, address = transfer(client)
    send_addr = [send_address, send_address]
    for from_address in send_addr:
        receipt = client.account.sendTransaction(client.node.web3, "", from_address, address, client.node.eth.gasPrice,gas_limit, LAT_1)
        logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))
        result = client.tidb.tb_tx_ori_voucher(receipt.transactionHash.hex())
        assert result
    assert_balance(client, send_address, send_address)
    assert_balance(client, send_address, address)


def test_send_benifi_addr(consensus_client):
    """
    委托收益地址转入
    """
    client = consensus_client
    receipt = client.account.sendTransaction(client.node.web3, "", client.account.address_with_money, client.node.web3.delegateRewardAddress, client.node.eth.gasPrice, gas_limit, LAT_1)
    logger.info("transfer transaction hash：{}".format(receipt.transactionHash.hex()))
    result = client.tidb.tb_tx_ori_voucher(receipt.transactionHash.hex())
    assert result
    assert_balance(client, client.account.address_with_money, client.node.web3.delegateRewardAddress)


@pytest.mark.parametrize("amount", [0, LAT_1])
def test_deploy_contract(consensus_client, amount):
    """
    部署合约
    """
    contract_address = deploy_contract(consensus_client, amount)
    consensus_client.assert_balance(contract_address)
    # assert_balance(consensus_client)


@pytest.mark.parametrize("amount", [0, LAT_1])
def test_use_contract(consensus_client, amount):
    """
    调用合约
    """
    contract_address = deploy_contract(consensus_client, amount)
    res = consensus_client.account.sendTransaction(consensus_client.node.web3, contract_func, consensus_client.account.address_with_money, contract_address, consensus_client.node.eth.gasPrice,
                                                   gas_limit, amount)
    consensus_client.assert_balance(contract_address)
    # assert_balance(consensus_client)


def deploy_contract(consensus_client, amount):
    res = consensus_client.account.sendTransaction(consensus_client.node.web3, contract_code, consensus_client.account.address_with_money, None, consensus_client.node.eth.gasPrice,
                                                   gas_limit, amount)
    return res["contractAddress"]



# if __name__ == '__main__':
#     # assert_balance()