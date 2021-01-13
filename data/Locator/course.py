from selenium.webdriver.common.by import By


class CourseLocator:
    # 元素locator
    datebase_button = (By.XPATH, '//*[@id="app"]/div/div[1]/div/div[1]/div/ul/div[4]/li/div/span')  # 基础设置按钮
    course_button = (By.XPATH, '//*[@id="app"]/div/div[1]/div/div[1]/div/ul/div[4]/li/ul/div/a/li/span')  # 科目按钮
    course_bread = (By.XPATH, '//*[@id="breadcrumb-container"]/span/span[2]/span[1]/span')  # 面包屑-科目管理
    course_menu_button = (By.XPATH, '//*[@id="app"]/div/div[1]/div/div[1]/div/ul/div[4]/li/ul/div/a/li')  # 菜单下的科目管理按钮
    add_button = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[1]/button[1]/span')  # 新增按钮
    export_button = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[1]/button[2]/span')  # 导出按钮
    list_add_button = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[2]/div[3]/table/tbody/tr[1]/td[8]/div/a[1]/span')  # 列表-编辑按钮
    list_edit_button = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[2]/div[3]/table/tbody/tr[1]/td[8]/div/a[2]/span')  # 列表-编辑按钮
    course_menu_title = (By.XPATH, '//*[@id="app"]/div/div[1]/div/div[1]/div/ul/div[4]/li/ul/div/a/li')  # 菜单下的科目管理
    rows_path = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[2]/div[3]/table/tbody/*')
    rows_one =  (By.XPATH, './td[8]/div/a[1]/span')
    #   列表新增操作
    course_title = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[1]/span')  # 新增科目弹框标题
    course_code_txt = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[2]/form/div[1]/div/div/input')  # 新增科目编码
    course_name_txt = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[2]/form/div[2]/div/div/input')  # 新增科目名称
    course_kind_button = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[2]/form/div[4]/div/div/div/input')  # 点击科目类别
    course_kind_area = (By.XPATH, '/html/body/div[3]/div[1]/div[1]/ul')  # 科目区域
    choose_course_kind_option1 = (By.XPATH, '//span[text()="资产类"]')  # 选择科目类别-资产
    choose_course_kind_option2 = (By.XPATH, '//span[text()="负债类"]')  # 选择科目类别-负债
    choose_course_kind_option3 = (By.XPATH, '//span[text()="所有者权益类"]')  # 选择科目类别-所有者权益
    choose_course_kind_option4 = (By.XPATH, '//span[text()="损益类"]')  # 选择科目类别-损益
    account_kind_button = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[2]/form/div[5]/div/div/div[2]/input')  # 点击账户类别
    account_kind_area = (By.XPATH, '/html/body/div[4]/div[1]/div[1]/ul')  # 账户区域
    choose_account_kind_option1 = (By.XPATH, '/html/body/div[4]/div[1]/div[1]/ul/li[1]')  # 选择账户类别-1111
    choose_account_kind_option2 = (By.XPATH, '/html/body/div[4]/div[1]/div[1]/ul/li[2]')  # 选择账户类别-2222
    account_pack_up = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[2]/form/div[5]/div/div/div[2]/span/span/i')   #收起账户类别
    directer_in = (By.XPATH, '//span[text()="借"]')  # 余额方向-借
    directer_out = (By.XPATH, '//span[text()="借"]')  # 余额方向-贷
    course_status = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[2]/form/div[7]/div/div/div/input')  # 科目状态下拉框
    course_status_enable = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[2]/form/div[7]/div/div/div/input')  # 科目状态-启用
    course_status_disable = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[2]/form/div[7]/div/div/div/input')  # 科目状态-禁用
    course_cancle = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[3]/div/button[1]/span')  # 科目状态--取消
    course_confirm = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[3]/div/button[2]/span')  # 科目状态--确定
    course_close = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[1]/button/i')  # 新增科目--关闭
    course_title = (By.XPATH, '//*[@id="breadcrumb-container"]/span/span[2]/span[1]/span')  # 科目title
    course_code_list = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[2]/div[3]/table/tbody')  # 科目title
    edit_course_title = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[1]/span')  # 编辑科目弹框标题
    add_course_test = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[2]/div[3]/table/tbody/tr[24]/td[8]/div/a[1]/span')  # 列表最下方的新增
    # 检查locator
    course_add_edit_msg = (By.XPATH, '/html/body/div[3]/p')  # 科目新增成功提示语
    course_update_success_msg = (By.XPATH, '/html/body/div[3]/p')  # 科目更新成功提示语
    course_account_kind_exist_msg = (By.XPATH, '/html/body/div[2]/p')  # 请删除账户类别后添加下级科目提示语


    course_code_error_msg = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[2]/form/div[1]/div/div[2]')  # 科目编码输入为空，或者输入格式错误
    course_name_error_msg = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[2]/form/div[2]/div/div[2]')  # 科目名称输入为空，输入格式错误
    course_kind_error_msg = (By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[3]/div/div[2]/form/div[4]/div/div[2]')  # 科目类别未选中
    course_data_exist_msg = (By.XPATH, '/html/body/div[4]/p')  # 数据库中已存在该记录


