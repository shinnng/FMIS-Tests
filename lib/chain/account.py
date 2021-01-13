from alaya.eth import Eth
from hexbytes import HexBytes
import random


class Account:
    def __init__(self, account_conf, chainId):
        """
        accounts 包含的属性: address,prikey,nonce,balance,node_id,passwd
        :param account_conf:
        :param chainId:
        """
        self.accounts = {}
        self.raw_accounts = account_conf
        self.chain_id = chainId
        self.account_with_money = self.raw_accounts[0]
        self.address_with_money = self.account_with_money["address"]
        self.reset()

    def reset(self):
        self.accounts = {}
        for account in self.raw_accounts:
            self.accounts[account['address']] = account

    def get_all_accounts(self):
        accounts = []
        for account in self.accounts.values():
            accounts.append(account)
        return accounts

    def get_rand_account(self):
        return random.choice(list(self.accounts.values()))

    def sendTransaction(self, connect, data, from_address, to_address, gasPrice, gas, value):
        platon = Eth(connect)
        account = self.accounts[from_address]
        nonce = platon.getTransactionCount(from_address)
        if to_address is None:
            transaction_dict = {
                "gasPrice": gasPrice,
                "gas": gas,
                "nonce": nonce,
                "data": data,
                "chainId": self.chain_id,
                "value": value,
            }
        else:
            transaction_dict = {
                "to": to_address,
                "gasPrice": gasPrice,
                "gas": gas,
                "nonce": nonce,
                "data": data,
                "chainId": self.chain_id,
                "value": value,
            }
        signedTransactionDict = platon.account.signTransaction(
            transaction_dict, account['prikey']
        )

        data = signedTransactionDict.rawTransaction
        result = HexBytes(platon.sendRawTransaction(data)).hex()
        # logger.debug("result:::::::{}".format(result))
        res = platon.waitForTransactionReceipt(result)
        account['nonce'] = nonce + 1
        self.accounts[from_address] = account
        return res

    def generate_account(self, web3, balance=0):
        platon = Eth(web3)
        account = platon.account.create(net_type=web3.net_type)
        address = account.address

        prikey = account.privateKey.hex()[2:]
        if balance != 0:
            self.sendTransaction(web3, '', self.account_with_money['address'], address, web3.platon.gasPrice, 21000,
                                 balance)
        account = {
            "address": address,
            "nonce": 0,
            "balance": balance,
            "prikey": prikey,
        }
        self.accounts[address] = account

        def debug():
            from conf.config import ACCOUNT_TMP
            from ruamel import yaml
            accounts = list(self.accounts.values())
            with open(ACCOUNT_TMP, mode="w", encoding="UTF-8") as f:
                yaml.dump(accounts, f, Dumper=yaml.RoundTripDumper)

        debug()
        return address, prikey

    def find_pri_key(self, address):
        return self.accounts[address]["prikey"]
