import pytest,time
from data.urls import dashboard_url, login_url
from lib.fmis import LoginPage, DashBordPage, ChangepwPage

@pytest.fixture()
def changepw_page(driver):
    # driver.get(dashboard_url)
    url = driver.get(dashboard_url)
    print(f'url ============ {url}')
    if url == login_url:
        lp = LoginPage(driver)
        lp.login('admin', 'admin123', '123456')
    dp = DashBordPage(driver)
    dp.goto_change_password()
    cp = ChangepwPage(driver)
    return cp

@pytest.fixture()
def login_page(driver):
    driver.get(dashboard_url)
    lp = LoginPage(driver)
    lp.login('admin', 'admin123', '123456')
    return lp

class TestChangepw:

    #修改密码并点击取消按钮，界面依旧显示在dashboard页面
    @pytest.mark.parametrize(('cur_password', 'new_password', 'con_password'), [('admin123', 'admin123', 'admin123')])
    def test_changepw_cancle(self, login_page, changepw_page, cur_password, new_password, con_password):
        msg = changepw_page.change_password_cancle(cur_password, new_password, con_password)
        assert msg == "PlatON运营支撑系统欢迎您"

    #修改密码，输入的旧密码错误
    @pytest.mark.parametrize(('cur_password', 'new_password', 'con_password'), [('admin456', 'admin123', 'admin123')])
    def test_changepw_current_error(self, login_page, changepw_page, cur_password, new_password, con_password):
        changepw_page.get_changepw_input(cur_password, new_password, con_password)
        msg = changepw_page.get_error_toast()
        assert msg == "原密码不正确"

    #修改密码，输入的旧密码为空
    @pytest.mark.parametrize(('cur_password', 'new_password', 'con_password'), [('', 'admin123', 'admin123'), ('', '', 'admin123'), ('', 'admin123', '')])
    def test_changepw_current_empty(self, login_page, changepw_page, cur_password, new_password, con_password):
        changepw_page.get_changepw_input(cur_password, new_password, con_password)
        msg = changepw_page.get_error_cur_msg()
        assert msg == "请输入旧密码"

    #修改密码，输入的新密码为空
    @pytest.mark.parametrize(('cur_password', 'new_password', 'con_password'), [('admin', '', 'admin123'), ('', '', 'admin123'), ('admin', '', '')])
    def test_changepw_new_empty(self, login_page, changepw_page, cur_password, new_password, con_password):
        changepw_page.get_changepw_input(cur_password, new_password, con_password)
        msg = changepw_page.get_error_new_msg()
        assert msg == "请输入新密码"

    #修改密码，输入的确认密码为空
    @pytest.mark.parametrize(('cur_password', 'new_password', 'con_password'), [('admin', 'admin123', ''), ('', 'admin123', ''), ('admin', '', '')])
    def test_changepw_confirm_empty(self, login_page, changepw_page, cur_password, new_password, con_password):
        changepw_page.get_changepw_input(cur_password, new_password, con_password)
        msg = changepw_page.get_error_conf_msg()
        assert msg == "请重复输入新密码"

    #修改密码，输入的所有密码均为空
    @pytest.mark.parametrize(('cur_password', 'new_password', 'con_password'), [('', '', '')])
    def test_changepw_all_empty(self, login_page, changepw_page, cur_password, new_password, con_password):
        changepw_page.get_changepw_input(cur_password, new_password, con_password)
        msg = changepw_page.get_error_cur_msg()
        assert msg == "请输入旧密码"
        msg = changepw_page.get_error_new_msg()
        assert msg == "请输入新密码"
        msg = changepw_page.get_error_conf_msg()
        assert msg == "请重复输入新密码"
        msg = changepw_page.get_error_toast()
        assert msg == '请确认表单内容正确'

  #修改密码，输入的新旧密码一致
    @pytest.mark.parametrize(('cur_password', 'new_password', 'con_password'), [('admin123', 'admin123', 'admin123')])
    def test_changepw_confirm_empty(self, login_page, changepw_page, cur_password, new_password, con_password):
        changepw_page.get_changepw_input(cur_password, new_password, con_password)
        msg = changepw_page.get_error_new_msg()
        assert msg == "新旧密码一致"
        msg = changepw_page.get_error_toast()
        assert msg == '请确认表单内容正确'

    #修改密码并点击确认按钮，提示正常
    @pytest.mark.parametrize(('cur_password', 'new_password', 'con_password'), [('admin123', 'admin124', 'admin124')])
    def test_changepw_success(self, login_page, changepw_page, cur_password, new_password, con_password):
        changepw_page.change_password_success(cur_password, new_password, con_password)
        msg = changepw_page.change_password_success_msg()
        assert msg == '密码修改成功'
        # time.sleep(2)
        title = login_page.get_title()
        assert title == '运营支撑系统'