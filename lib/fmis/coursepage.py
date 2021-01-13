import time

from .basepage import BasePage
from data.Locator import LoginLocator as loc
from data.Locator import ChangepwLocator as cploc
from data.Locator import DashboardLocator as dbloc
from data.Locator import CourseLocator as clloc


class CoursePage(BasePage):
    # 验证成功进入科目管理页面
    def goto_course_interface(self):
        self.click_Element(clloc.datebase_button, mark='点击基础设置按钮')
        self.wait_eleVisible(clloc.course_menu_button, mark='等待科目菜单出现')
        self.click_Element(clloc.course_button, mark='点击科目管理按钮')
        self.wait_eleVisible(clloc.add_button, mark='等待新增按钮出现')
        text = self.get_Text(clloc.course_title, mark='获取科目管理标题')
        return text

    # def execute_export(self,username, password, authcode):

    def add_course(self, cour_code, cour_name):
        self.wait_eleVisible(clloc.add_button, mark='等待新增按钮出现')
        self.click_Element(clloc.add_button, mark='点击新增按钮')
        self.wait_eleVisible(clloc.course_title, mark='等待新增科目标题出现')
        self.input_Text(clloc.course_code_txt, cour_code, mark='输入科目编码')
        self.input_Text(clloc.course_name_txt, cour_name, mark='输入科目名称')
        self.click_Element(clloc.course_kind_button, mark='下拉科目类别')
        self.wait_eleVisible(clloc.course_kind_area, mark='等待科目类别出现')
        self.click_Element(clloc.choose_course_kind_option1, mark='选择资产类')
        self.click_Element(clloc.course_confirm, mark='点击保存按钮')

    def add_course_kind_empty(self, cour_code, cour_name):
        self.wait_eleVisible(clloc.add_button, mark='等待新增按钮出现')
        self.click_Element(clloc.add_button, mark='点击新增按钮')
        self.wait_eleVisible(clloc.course_title, mark='等待新增科目标题出现')
        self.input_Text(clloc.course_code_txt, cour_code, mark='输入科目编码')
        self.input_Text(clloc.course_name_txt, cour_name, mark='输入科目名称')
        # self.click_Element(clloc.course_kind_button, mark='下拉科目类别')
        # self.wait_eleVisible(clloc.course_kind_area, mark='等待科目类别出现')
        # self.click_Element(clloc.choose_course_kind_option1, mark='选择资产类')
        self.click_Element(clloc.course_confirm, mark='点击保存按钮')

    def edit_course_kind_error(self, cours_code):         #输入已存在的编码
        self.wait_eleVisible(clloc.list_edit_button, mark='等待编辑按钮出现')
        self.click_Element(clloc.list_edit_button, mark='点击编辑按钮')
        self.wait_eleVisible(clloc.edit_course_title, mark='等待编辑科目标题出现')
        self.clean_Input_Text(clloc.course_code_txt, mark='清除科目编码')
        self.input_Text(clloc.course_code_txt, cours_code, mark='输入科目编码')
        self.click_Element(clloc.course_confirm, mark='点击保存按钮')

    def edit_course_empty(self, cour_code, cour_name):  # 清空编码+名称
        self.wait_eleVisible(clloc.list_edit_button, mark='等待编辑按钮出现')
        self.click_Element(clloc.list_edit_button, mark='点击编辑按钮')
        self.wait_eleVisible(clloc.edit_course_title, mark='等待编辑科目标题出现')
        self.clean_Input_Text(clloc.course_code_txt, mark='清除科目编码')
        self.input_Text(clloc.course_code_txt, cour_code,  mark='输入科目编码')
        self.clean_Input_Text(clloc.course_code_txt, mark='清除科目编码')
        self.wait_eleVisible(clloc.course_code_error_msg, mark='等待请输入科目编码出现')
        self.clean_Input_Text(clloc.course_name_txt, mark='清除科目名称')
        self.input_Text(clloc.course_name_txt, cour_name, mark='输入科目名称')
        self.clean_Input_Text(clloc.course_name_txt, mark='清除科目名称')
        self.wait_eleVisible(clloc.course_name_error_msg, mark='等待请输入科目名称出现')
        self.click_Element(clloc.course_confirm, mark='点击保存按钮')

    def edit_course_success(self):
        self.wait_eleVisible(clloc.list_edit_button, mark='等待编辑按钮出现')
        self.click_Element(clloc.list_edit_button, mark='点击编辑按钮')
        self.wait_eleVisible(clloc.edit_course_title, mark='等待编辑科目标题出现')
        self.click_Element(clloc.directer_out, mark='点击借贷方向为贷按钮')
        self.click_Element(clloc.course_status_disable, mark="点击当前科目状态为禁用")
        self.click_Element(clloc.course_confirm, mark='点击保存按钮')

    def accout_kind_exist_add(self, cour_code, cour_name):
        self.wait_eleVisible(clloc.add_button, mark='等待新增按钮出现')
        self.click_Element(clloc.add_button, mark='点击新增按钮')
        self.wait_eleVisible(clloc.course_title, mark='等待新增科目标题出现')
        self.input_Text(clloc.course_code_txt, cour_code, mark='输入科目编码')
        self.input_Text(clloc.course_name_txt, cour_name, mark='输入科目名称')
        self.click_Element(clloc.course_kind_button, mark='下拉科目类别')
        self.wait_eleVisible(clloc.course_kind_area, mark='等待科目类别出现')
        self.click_Element(clloc.choose_course_kind_option1, mark='选择资产类')
        self.click_Element(clloc.account_kind_button, mark='下拉账户类别')
        self.wait_eleVisible(clloc.choose_account_kind_option1, mark='等待账户类别出现')
        self.click_Element(clloc.choose_account_kind_option1, mark='选择第一个选项')
        self.click_Element(clloc.account_pack_up, mark='收起选项')
        self.click_Element(clloc.course_confirm, mark='点击保存按钮')
        self.wait_eleVisible(clloc.add_course_test, mark='等待新增按钮出现')
        self.click_Element(clloc.add_course_test, mark='点击新增按钮')

    def course_update_success_msg(self):
        msg = self.get_Text(clloc.course_update_success_msg, mark='获取新增/更新成功的提示条')
        return msg

    def add_course_exist_msg(self):
        msg = self.get_Text(clloc.course_data_exist_msg, mark='获取科目信息已存在的提示条')
        return msg

    def course_code_list(self):
        msg = self.get_Text(clloc.course_code_list, mark='获取科目编码')
        return msg

    def pop_up(self):
        self.wait_eleVisible(clloc.course_bread, mark='等待面包屑可见')
        txt = self.get_Text(clloc.course_bread, mark='获取科目管理面包屑')
        return txt

    def course_name_error_msg(self):
        txt = self.get_Text(clloc.course_name_error_msg, mark='获取科目名称异常的提示')
        return txt

    def course_code_error_msg(self):
        txt = self.get_Text(clloc.course_code_error_msg, mark='获取科目编码异常的提示')
        return txt

    def course_kind_error_msg(self):
        txt = self.get_Text(clloc.course_kind_error_msg, mark='获取科目类别异常的提示')
        return txt

    def edit_course_error_msg(self):
        txt = self.get_Text(clloc.course_add_edit_msg, mark='获取科目编码[1001110]已被其它科目占用!的提示')
        return txt

    def account_kind_exist_add_msg(self):
        txt = self.get_Text(clloc.course_account_kind_exist_msg)
        return txt


    def get_table_rows(self):
        rows = self.find_Elements(clloc.rows_path, mark='查找全部数据')
        print(rows[0])
        raw = rows[0].find_Elements(clloc.rows_one, mark='查找部分数据').click()
        # raw = rows[0].find_Elements(clloc.rows_one, mark='查找部分数据')
        # self.click_Element(clloc.)
        print(raw)
        return raw
