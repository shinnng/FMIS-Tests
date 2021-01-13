import os


# project path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# account file path
ACCOUNT_TMP = os.path.join(BASE_DIR, "conf/env/account_tmp.yaml")

# selenium全局隐性超时设置
globalTimeOut = 0

# 文件目录设置
logfile_path = './log/file_{time}.log'
screenshot_path = './report/image/'
