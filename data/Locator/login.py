from selenium.webdriver.common.by import By


class LoginLocator:

    # 元素locator
    username_input = (By.XPATH, '//*[@id="app"]/div/form/div[2]/div/div/input')
    password_input = (By.XPATH, '//*[@id="app"]/div/form/div[3]/div/div/input')
    authcode_input = (By.XPATH, '//*[@id="app"]/div/form/div[4]/div/div/input')
    refresh_authcode_button = (By.XPATH, '//*[@id="app"]/div/form/div[5]/div/span')
    login_button = (By.XPATH, '//*[@id="app"]/div/form/button/span')

    # 检查locator
    login_errormsg_txt = (By.XPATH, '/html/body/div[2]')
    username_warningmsg_txt = (By.XPATH, '//*[@id="app"]/div/form/div[2]/div/div[2]')
    password_warningmsg_txt = (By.XPATH, '//*[@id="app"]/div/form/div[3]/div/div[2]')
    authcode_warningmsg_txt = (By.XPATH, '//*[@id="app"]/div/form/div[4]/div/div[2]')
    title_txt = (By.XPATH, '//*[@id="app"]/div/form/div[1]/h1')  #退出登录后回到登录页面的检查点--财务系统标题
