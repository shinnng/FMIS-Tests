from selenium.webdriver.common.by import By


class DashboardLocator:

    # 元素locator
    overview_button = (By.XPATH, '//*[@id="hamburger-container"]/svg')
    login_out_button = (By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div/div[2]/div[1]')
    change_password_button = (By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div/div[2]/div[2]')

    # 检查locator
    title_txt = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/h1')
    login_txt = (By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div/div[2]/div[1]')