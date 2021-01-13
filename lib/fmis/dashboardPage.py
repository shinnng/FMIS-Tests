from .basepage import BasePage

from data.Locator import DashboardLocator as dbloc
from data.Locator import LoginLocator as loc

class DashBordPage(BasePage):

    def show_overview(self):
        self.click_Element(dbloc.overview_button, mark='点击概览按钮，显示侧边概览栏')

    def hide_overview(self):
        self.click_Element(dbloc.overview_button, mark='点击概览按钮，隐藏侧边概览栏')

    def get_title(self):
        return self.get_Text(dbloc.title_txt, mark='获取概览title文本内容')

    def login_out(self):
        self.click_Element(dbloc.login_out_button, mark='点击退出登录按钮，跳转至登录页面')
        return self.get_Text(loc.login_title_txt, mark='获取登录页面文本内容')

    def goto_change_password(self):
        self.click_Element(dbloc.change_password_button, mark='点击修改密码按钮，跳转至修改密码页面')