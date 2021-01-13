from selenium.webdriver.common.by import By

class ChangepwLocator:

    # 元素locator
    current_password_input = (By.XPATH, '//*[@id="app"]/div/form/div[2]/div/div/input')    #当前密码输入文本框
    new_password_input = (By.XPATH, '//*[@id="app"]/div/form/div[3]/div/div/input')    #新密码输入文本框
    confirm_password_input = (By.XPATH, '//*[@id="app"]/div/form/div[4]/div/div/input')    #确认密码输入文本框

    # 检查locator
    change_password_txt = (By.XPATH, '//*[@id="app"]/div/form/div[1]/h1')   #修改密码的title
    cancle_button = (By.XPATH, '//*[@id="app"]/div/form/button[1]/span')    #取消按钮
    confirm_button = (By.XPATH, '//*[@id="app"]/div/form/button[2]/span')   #确认按钮
    changepw_msg_toast = (By.XPATH, '/html/body/div[2]/p')    #原密码不正确  密码修改成功
    changepw_cur_txt = (By.XPATH, '//*[@id="app"]/div/form/div[2]/div/div[2]')   # 旧密码不能为空  密码格式错误
    changepw_new_txt = (By.XPATH, '//*[@id="app"]/div/form/div[3]/div/div[2]')   # 新密码不能为空  密码格式错误
    changepw_conf_txt = (By.XPATH, '//*[@id="app"]/div/form/div[4]/div/div[2]')   # 确认密码不能为空   两次输入密码不一致
    login_title_txt = (By.XPATH, '//*[@id="app"]/div/form/div[1]/h1')  #退出登录后回到登录页面的检查点--财务系统标题
