import pytest
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from conf.config import globalTimeOut
@pytest.fixture(scope='session', autouse=False)
def driver() -> WebElement:
    # 清理环境，关闭谷歌浏览器相关进程
    # os.system('taskkill /IM chromedriver.exe /F')
    # os.system('taskkill /IM chrome.exe /F')

    # 启动chrome
    chrome_options = webdriver.ChromeOptions()
    wd = webdriver.Chrome(chrome_options=chrome_options)
    # driver_path = r'D:/ProgramFiles/Python/msedgedriver.exe'
    # wd = webdriver.Edge(executable_path=driver_path)
    wd.maximize_window()
    wd.implicitly_wait(globalTimeOut)

    yield wd

    # 清理环境，关闭谷歌浏览器相关进程
    # os.system('taskkill /IM chromedriver.exe /F')
    # os.system('taskkill /IM chrome.exe /F')
