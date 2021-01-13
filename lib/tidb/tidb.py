import time

from pymysql import connect
from alaya.utils.threads import (
    Timeout,
)
import pymysql
from decimal import Decimal


def to_int(func):
    def wrap(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, dict):
            for k, v in res.items():
                if isinstance(v, Decimal):
                    res[k] = int(v)
        elif isinstance(res, Decimal):
            res = int(res)
        return res

    return wrap


def wait_fetch(func):
    def wrap(*args, **kwargs):
        with Timeout(10) as _timeout:
            while True:
                res = func(*args, **kwargs)
                if res is not None:
                    break
                _timeout.sleep(0.1)
        return res
    return wrap

class Tidb:
    def __init__(self, host=None, user=None, password="",
                 database=None, port=0, unix_socket=None,
                 charset='', **kwargs):
        self.con = connect(host=host, user=user, password=password,
                           database=database, port=port, unix_socket=unix_socket,
                           charset=charset, **kwargs)
        self.cursor = self.con.cursor(pymysql.cursors.DictCursor)

    def close(self):
        self.con.close()

    @to_int
    @wait_fetch
    def fetchone(self, sql):
        with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql)
            self.con.commit()
            return cursor.fetchone()

    def fetchall(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    # Dominant
    def query_balance(self, address, blocknumber):
        sql = "SELECT sum(dr_amount) - sum(cr_amount) as balance FROM tb_track_account_book WHERE main_address='%s' AND block_number <= '%s'" % (address, blocknumber)
        # sql = "SELECT sum(dr_amount) - sum(cr_amount) as balance FROM tb_track_account_book WHERE main_address='%s'" % address
        return self.fetchone(sql)

    def tb_tx_ori_voucher(self, tx_hash):
        sql = """SELECT * FROM tb_tx_ori_voucher where tx_hash='%s' """ % tx_hash
        return self.fetchone(sql)

    def tb_tx_ori_voucher_staking_delegate_detail_status(self, node_id, address):
        sql = """SELECT record_type,opt_type FROM tb_tx_ori_voucher_staking_degate_detail WHERE node_id = '%s' AND address = '%s' order by create_time desc""" % (
        node_id, address)
        return self.fetchone(sql)

    def tb_tx_ori_voucher_staking_delegate_detail(self, node_id, address):
        sql = """SELECT SUM(free_amount) AS free_amount,SUM(lock_amount) AS lock_amount FROM tb_tx_ori_voucher_staking_degate_detail WHERE node_id = '%s' AND address = '%s'""" % (
            node_id, address)
        return self.fetchone(sql)

    def tb_tx_ori_voucher_contract_attach(self, tx_hash):
        sql = """SELECT * FROM tb_tx_ori_voucher_contract_attach WHERE tx_hash='%s'""" % tx_hash
        return self.fetchone(sql)

    def tb_tx_ori_voucher_unstaking_attach(self, node_id, address):
        sql = "SELECT * FROM tb_tx_ori_voucher_unstaking_attach WHERE node_id='%s' AND staking_address='%s' ORDER BY create_time DESC" % (
        node_id, address)
        return self.fetchone(sql)

    def tb_tx_ori_voucher_undelegation_attach(self, node_id, address):
        sql = "SELECT * FROM tb_tx_ori_voucher_undelegation_attach WHERE node_id='%s' AND delegate_address='%s'" % (
        node_id, address)
        return self.fetchone(sql)

    def tb_tx_ori_voucher_double_sign_attach(self, node_id):
        sql = "SELECT * FROM tb_tx_ori_voucher_double_sign_attach WHERE node_id='%s'" % node_id
        return self.fetchone(sql)

    def tb_tx_ori_voucher_delegate_detail_attach(self, node_id, address):
        sql = "SELECT * FROM tb_tx_ori_voucher_delegate_detail_attach WHERE delegate_addr='%s' AND node_id='%s'" % (
        address, node_id)
        return self.fetchone(sql)

    def tb_tx_ori_voucher_receive_delegate_reward_attach(self, node_id, address):
        sql = "SELECT * FROM tb_tx_ori_voucher_receive_delegate_reward_attach WHERE delegate_address='%s' AND node_Id='%s'" % (
        address, node_id)
        return self.fetchone(sql)

    def tb_tx_ori_voucher_create_lock_plan_attach(self, address):
        sql = "SELECT * FROM tb_tx_ori_voucher_create_lock_plan_attach WHERE lock_address='%s'" % address
        return self.fetchone(sql)

    # Recessive
    def tb_slash_ori_voucher(self, node_id):
        sql = "SELECT * FROM tb_slash_ori_voucher WHERE node_id='%s' order by block_timestamp desc" % node_id
        return self.fetchone(sql)

    def tb_block_reward_ori_voucher(self, node_id, block_number):
        sql = "SELECT * FROM tb_block_reward_ori_voucher WHERE node_id='%s' AND block_number=%d" % (
        node_id, block_number)
        return self.fetchone(sql)

    def tb_staking_reward_ori_voucher(self, node_id, block_number):
        sql = "SELECT * FROM tb_staking_reward_ori_voucher WHERE node_id='%s' AND block_number=%d" % (
        node_id, block_number)
        return self.fetchone(sql)

    def tb_delegate_reward_alloc_ori_voucher(self, node_id, block_number):
        sql = "SELECT * FROM tb_delegate_reward_alloc_ori_voucher WHERE node_id='%s' AND block_number=%d" % (
        node_id, block_number)
        return self.fetchone(sql)

    def tb_additional_ori_voucher(self, block_number):
        sql = "SELECT * FROM tb_additional_ori_voucher WHERE block_number=%d" % block_number
        return self.fetchone(sql)

    def tb_staking_lock_ori_voucher(self, node_id, address):
        sql = "SELECT * FROM tb_staking_lock_ori_voucher WHERE node_id='%s' AND staking_address='%s'" % (
        node_id, address)
        return self.fetchone(sql)

    def tb_unfreeze_staking_ori_voucher(self, node_id, address):
        sql = "SELECT * FROM tb_unfreeze_staking_ori_voucher WHERE node_id='%s' AND staking_addr='%s'" % (
        node_id, address)
        return self.fetchone(sql)

    def tb_restrict_release_ori_voucher(self, address):
        sql = "SELECT * FROM tb_restrict_release_ori_voucher WHERE restric_addr='%s'" % address
        return self.fetchone(sql)

    def tb_initial_alloc_ori_voucher(self, block_number):
        sql = "SELECT * FROM tb_initial_alloc_ori_voucher WHERE block_number=%d" % block_number
        return self.fetchone(sql)

    def tb_delegate_lock_ori_voucher(self, node_id, address):
        sql = "SELECT * FROM tb_delegate_lock_ori_voucher WHERE node_id='%s' AND benefit_addr='%s'" % (node_id, address)
        return self.fetchone(sql)

    def tb_delegate_detail(self, node_id, address):
        sql = "SELECT * FROM tb_delegate_detail WHERE node_id='%s' AND delegate_addr='%s'" % (
        node_id, address)
        return self.fetchone(sql)

    def tb_reward_alloc_ori_voucher(self, node_id, address):
        sql = "SELECT * FROM tb_reward_alloc_ori_voucher WHERE node_id='%s' AND benefit_addr='%s' ORDER BY create_time DESC" % (node_id, address)
        return self.fetchone(sql)

    # General
    def tb_track_account_book(self, address):
        sql = "SELECT max(block_number)  as tidb_block FROM tb_track_account_book where main_address = '%s'" % address
        return self.fetchone(sql)

    def tb_node(self, node_id):
        sql = "SELECT * FROM tb_node WHERE node_id='%s'" % node_id
        return self.fetchone(sql)

    def tb_sync_status(self):
        sql = "SELECT last_block_number FROM tb_sync_status where type = 'BN'"
        return self.fetchone(sql)

    def tb_address(self, address):
        sql = "SELECT balance FROM tb_address where address ='%s'" % address
        return self.fetchone(sql)




if __name__ == '__main__':
    from conf.config import BASE_DIR
    import os
    from common.load_file import LoadFile

    config_file = os.path.join(BASE_DIR, "conf/env/config.yaml")
    config = LoadFile(config_file).get_data()
    tidb_conf = config["tidb"]
    tidb = Tidb(tidb_conf["host"], tidb_conf["username"], tidb_conf["password"], database=tidb_conf['database'],
                port=tidb_conf["port"])
    print(tidb.tb_tx_ori_voucher("0x818d13b43037f246161343fade2e212899d8456fd98eb190d2c20e0153053fc2"))
    # tidb.con.cursor().fetchone()

    tidb.close()
