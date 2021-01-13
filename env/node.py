from common.connect import connect_linux, run_ssh
from loguru import logger
from common.load_file import LoadFile
from alaya import Web3, HTTPProvider

failed_msg = "Node-{} do {} failed:{}"
success_msg = "Node-{} do {} success"


class NodeEnv:

    def __init__(self, node, node_conf):
        self.host = node['host']
        self.uaername = node_conf['username']
        self.password = node_conf['password']
        self.rpc_port = node['rpcport']
        self.p2p_port = node['port']
        self.node_name = f"node-{self.p2p_port}"
        self.public_key = node['id']
        self.private_key = node['nodekey']
        self.bls_public_key = node['blspubkey']
        self.bls_private_key = node['blsprikey']
        self.ssh, _, _ = connect_linux(self.host, self.uaername, self.password)
        self.path = f"{node_conf['deploy_path']}/{self.node_name}"
        self.remote_bin_file = f'{self.path}/platon'
        self.remote_genesis_file = f'{self.path}/genesis.json'
        self.remote_data_dir = f'{self.path}/data'
        self.remote_log_dir = f'{self.path}/log'

    def running(self, p2p_port) -> bool:
        p_id = self.run_ssh("ps -ef|grep platon|grep port|grep %s|grep -v grep|awk {'print $2'}" % p2p_port())
        if len(p_id) == 0:
            return False
        return True

    def init(self):
        """
        Initialize
        :return:
        """
        def __init():
            cmd = '{} --datadir {} init {}'.format(self.remote_bin_file, self.remote_data_dir, self.remote_genesis_file)
            result = self.run_ssh(cmd)
            # todo ：fix init complete
            # Adding a query here can only alleviate the problem of starting deployment without initialization.
            self.run_ssh("ls {}".format(self.remote_data_dir))
            if len(result) > 0:
                logger.error(failed_msg.format(self.node_name, "init", result[0]))
                raise Exception("Init failed:{}".format(result[0]))
            logger.debug("node-{} init success".format(self.node_name))
        self.try_do(__init)

    def start(self, is_init=False) -> tuple:
        """
        boot node
        :param is_init:
        :return:
        """
        logger.debug("Start node:{}".format(self.node_name))

        def __start():
            is_success = self.stop()
            if not is_success:
                raise Exception("Stop failed")
            if is_init:
                self.init()
            result = self.run_ssh("sudo -S -p '' supervisorctl start " + self.node_name, True)
            for r in result:
                if "ERROR" in r or "Command 'supervisorctl' not found" in r:
                    raise Exception("Start failed:{}".format(r.strip("\n")))

        return self.try_do_resturn(__start)

    def stop(self):
        """
        close node
        :return:
        """
        logger.debug("Stop node:{}".format(self.node_name))

        def __stop():
            self.__is_connected = False
            self.__is_ws_connected = False
            if not self.running:
                return True, "{}-node is not running".format(self.node_name)
            self.run_ssh("sudo -S -p '' supervisorctl stop {}".format(self.node_name), True)
        return self.try_do_resturn(__stop)

    def restart(self) -> tuple:
        """
        restart node
        :return:
        """
        def __restart():
            result = self.run_ssh("sudo -S -p '' supervisorctl restart " + self.node_name, True)
            for r in result:
                if "ERROR" in r:
                    raise Exception("restart failed:{}".format(r.strip("\n")))
        return self.try_do_resturn(__restart)

    def clean_db(self):
        """
        clear the node database
        :return:
        """
        def __clean_db():
            is_success = self.stop()
            if not is_success:
                raise Exception("Stop failed")
            self.run_ssh("sudo -S -p '' rm -rf {}".format(self.remote_data_dir), True)
        return self.try_do_resturn(__clean_db)

    def clean_log(self):
        """
        clear node log
        :return:
        """
        def __clean_log():
            is_success = self.stop()
            if not is_success:
                raise Exception("Stop failed")
            self.run_ssh("rm -rf {}".format(self.remote_log_dir))
        self.try_do(__clean_log)

    def try_do(self, func):
        try:
            func()
        except Exception as e:
            raise Exception(failed_msg.format(self.node_name, func.__name__, e))

    def try_do_resturn(self, func):
        try:
            func()
        except Exception as e:
            return False, failed_msg.format(self.node_name, func.__name__, e)
        return True, success_msg.format(self.node_name, func.__name__)

    def run_ssh(self, cmd, need_password=False):
        if need_password:
            return run_ssh(self.ssh, cmd, self.password)
        return run_ssh(self.ssh, cmd)


if __name__ == '__main__':
    logger.add("./log/file_{time}.log", rotation="500 MB", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
    url = 'http://192.168.120.121:6789'
    config_file = 'F:/Gitlab/PlatON_Tracking/conf/config.yaml'
    config = LoadFile(config_file).get_data()
    node_conf = config["node"]
    node = config["node"]["consensus"][0]
    w3 = Web3(HTTPProvider(url), chain_id=101)
    env = NodeEnv(node, node_conf)
    result = env.start()
    print(result)
