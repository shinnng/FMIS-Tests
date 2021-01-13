import pytest
from data.urls import login_url
from lib.fmis import LoginPage, DashBordPage


@pytest.fixture()
def login_page(driver):
    driver.get(login_url)
    lp = LoginPage(driver)
    return lp


@pytest.fixture()
def dashboard_page(driver):
    dp = DashBordPage(driver)
    return dp


class TestLogin:

    #  登录成功
    @pytest.mark.parametrize('username, password, authcode', [('admin', 'admin123', '123456')])
    def test_login_success(self, login_page, dashboard_page, username, password, authcode):
        login_page.login(username, password, authcode)
        page_title = dashboard_page.get_title()
        assert page_title == 'PlatON运营支撑系统欢迎您'


    #  登录失败
    @pytest.mark.parametrize('username, password, authcode', [('admin', 'test1234', '123456')])
    def test_login_failure(self, login_page, username, password, authcode):
        login_page.login(username, password, authcode)
        msg = login_page.get_login_errormsg()
        print(msg)
        assert msg == '用户名或密码错误'

    #  登录失败
    @pytest.mark.parametrize('username, password, authcode', [('', 'admin123', '123456'), ('', '', '123456'),
                                                              ('', 'admin123', ''), ('', '', '')])
    def test_login_required_username_input(self, login_page, username, password, authcode):
        login_page.login(username, password, authcode)
        required_msg = login_page.get_login_required_username_input()
        print(required_msg)
        assert required_msg == '账户名不能输入为空'

    @pytest.mark.parametrize('username, password, authcode', [('admin', '', '123456'), ('admin', '', ''),
                                                              ('', '', '123456'), ('', '', '')])
    def test_login_required_password_input(self, login_page, username, password, authcode):
        login_page.login(username, password, authcode)
        required_msg = login_page.get_login_required_password_input()
        print(required_msg)
        assert required_msg == '密码不能输入为空'

    @pytest.mark.parametrize('username, password, authcode', [('admin', 'admin123', ''), ('', 'admin123', ''),
                                                              ('admin', '', ''), ('', '', '')])
    def test_login_required_authcode_input(self, login_page, username, password, authcode):
        login_page.login(username, password, authcode)
        required_msg = login_page.get_login_required_authcode_input()
        print(required_msg)
        assert required_msg == '验证码不能输入为空'

    @pytest.mark.parametrize('username, password, authcode', [('12345', 'admin', '123456'),
                                                              ('admin111111', 'admin', '123456'),
                                                              ('testing', 'admin', '123456')])
    def test_invalid_username_input(self, login_page, username, password, authcode):
        login_page.login(username, password, authcode)
        required_msg = login_page.get_login_required_username_input()
        print(required_msg)
        assert required_msg == '用户名错误'

    @pytest.mark.parametrize('username, password, authcode', [('admin', '123456789', '123456'),
                                                              ('admin', '123', '123456')])
    def test_invalid_password_input(self, login_page, username, password, authcode):
        login_page.login(username, password, authcode)
        required_msg = login_page.get_login_required_password_input()
        print(required_msg)
        assert required_msg == '密码格式错误'

    #登出成功
    @pytest.mark.parametrize('username, password, authcode', [('admin', 'admin123', '123456')])
    def test_login_required_authcode_input(self, login_page, username, password, authcode):
        login_page.login(username, password, authcode)
        login_out_msg = login_page.login_out()
        print(login_out_msg)
        assert login_out_msg == '运营支撑系统'