from .basepage import BasePage
from data.Locator import LoginLocator as loc
from data.Locator import DashboardLocator as dbloc


class LoginPage(BasePage):

    def login(self, username, password, authcode):
        self.clean_Input_Text(loc.username_input, mark='清除页面记录的用户名')
        self.input_Text(loc.username_input, username, mark='输入用户名')
        self.clean_Input_Text(loc.password_input, mark='清除页面记录的密码')
        self.input_Text(loc.password_input, password, mark='输入密码')
        self.input_Text(loc.authcode_input, authcode, mark='输入验证码')
        self.click_Element(loc.login_button, mark='点击登陆按钮')

    def get_login_errormsg(self):
        self.wait_eleVisible(loc.login_errormsg_txt, mark='等待登陆错误提示出现')
        msg = self.get_Text(loc.login_errormsg_txt, mark='获取登陆错误提示信息')
        return msg

    def get_login_required_username_input(self):
        self.wait_eleVisible(loc.username_warningmsg_txt, mark='等待用户名不能为空提示信息')
        username_required_msg = self.get_Text(loc.username_warningmsg_txt, mark='获取用户名不能为空提示信息')
        return username_required_msg

    def get_login_required_password_input(self):
        self.wait_eleVisible(loc.password_warningmsg_txt, mark='等待密码不能为空提示信息')
        password_required_msg = self.get_Text(loc.password_warningmsg_txt, mark='获取密码不能为空提示信息')
        return password_required_msg

    def get_login_required_authcode_input(self):
        self.wait_eleVisible(loc.authcode_warningmsg_txt, mark='等待验证码不能为空提示信息')
        authcode_required_msg = self.get_Text(loc.authcode_warningmsg_txt, mark='获取验证码不能为空提示信息')
        return authcode_required_msg

    def get_title(self):
        title = self.get_Text(loc.title_txt, mark='获取页面title')
        return title

    def get_url(self):
        title = self.browser.current_url(loc.title_txt, mark='获取页面title')
        return title


    def login_out(self):
        self.click_Element(dbloc.login_out_button, mark="点击登出按钮")
        title = self.get_title()
        return title