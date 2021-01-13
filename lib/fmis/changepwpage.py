from .basepage import BasePage
from data.Locator import LoginLocator as loc
from data.Locator import ChangepwLocator as cploc
from data.Locator import DashboardLocator as dbloc

class ChangepwPage(BasePage):
    #验证修改密码正常+确认
    def change_password_success(self, cur_password, new_password, con_password):
        self.input_Text(cploc.current_password_input, cur_password, mark='输入当前密码')
        self.input_Text(cploc.new_password_input, new_password, mark='输入新密码')
        self.input_Text(cploc.confirm_password_input, con_password, mark='确认密码')
        self.click_Element(cploc.confirm_button, mark='点击确认按钮')

    def change_password_success_msg(self):
        self.wait_eleVisible(loc.login_errormsg_txt, mark='等待密码修改成功提示出现')
        msg = self.get_Text(loc.login_errormsg_txt, mark='获取密码修改成功提示信息')
        return msg

    #验证修改密码正常+取消
    def change_password_cancle(self, cur_password, new_password, con_password):
        self.input_Text(cploc.current_password_input, cur_password, mark='输入当前密码')
        self.input_Text(cploc.new_password_input, new_password, mark='输入新密码')
        self.input_Text(cploc.confirm_password_input, con_password, mark='确认密码')
        self.click_Element(cploc.cancle_button, mark='点击取消按钮')
        dashboard_txt = self.get_Text(dbloc.title_txt, mark='界面正常回到欢迎页面')
        return dashboard_txt

    #验证修改密码异常+确认
    def get_changepw_errormsg(self, cur_password, new_password, con_password):
        self.input_Text(cploc.current_password_input, cur_password, mark='输入当前密码')
        self.input_Text(cploc.new_password_input, new_password, mark='输入新密码')
        self.input_Text(cploc.confirm_password_input, con_password, mark='确认密码')
        self.click_Element(cploc.confirm_button, mark='点击确认按钮')
        self.wait_eleVisible(cploc.changepw_msg_txt, mark='等待修改错误提示出现')
        msg = self.get_Text(cploc.changepw_msg_txt, mark='获取修改错误提示信息')
        return msg

    #  当前密码输入为空
    def get_changepw_input(self, cur_password, new_password, con_password):
        self.input_Text(cploc.current_password_input, cur_password, mark='输入当前密码')
        self.input_Text(cploc.new_password_input, new_password, mark='输入新密码')
        self.input_Text(cploc.confirm_password_input, con_password, mark='确认密码')
        self.click_Element(cploc.confirm_button, mark='点击确认按钮')

    # 获取当前密码不正确的提示条
    def get_error_toast(self):
        self.wait_eleVisible(cploc.changepw_msg_toast, mark='等待修改错误提示出现')
        msg = self.get_Text(cploc.changepw_msg_toast, mark='获取修改错误提示信息')
        return msg

    #  获取旧密码输入框下方的不能为空的提示条
    def get_error_cur_msg(self):
        self.wait_eleVisible(cploc.changepw_cur_txt, mark='等待修改错误提示出现')
        msg = self.get_Text(cploc.changepw_cur_txt, mark='获取修改错误提示信息')
        return msg

    #  获取新密码输入框下方的不能为空的提示条
    def get_error_new_msg(self):
        self.wait_eleVisible(cploc.changepw_new_txt, mark='等待修改错误提示出现')
        msg = self.get_Text(cploc.changepw_new_txt, mark='获取修改错误提示信息')
        return msg

    #  获取确认密码输入框下方的不能为空的提示条
    def get_error_conf_msg(self):
        self.wait_eleVisible(cploc.changepw_conf_txt, mark='等待修改错误提示出现')
        msg = self.get_Text(cploc.changepw_conf_txt, mark='获取修改错误提示信息')
        return msg