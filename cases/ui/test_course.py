import time
import random

import pytest
from data.urls import dashboard_url, login_url, course_url
from lib.fmis import LoginPage, DashBordPage, ChangepwPage, CoursePage

@pytest.fixture()
def course_page(driver):
    url = driver.get(course_url)
    print(f'url ============ {url}')
    if url == login_url:
        lp = LoginPage(driver)
        lp.login('admin', 'admin123', '123456')
    cp = CoursePage(driver)
    return cp

@pytest.fixture()
def login_page(driver):
    driver.get(login_url)
    lp = LoginPage(driver)
    lp.login('admin', 'admin123', '123456')
    return lp

class TestCourse:

    #  查看科目管理跳转正常
    @pytest.mark.parametrize(('username', 'password', 'authcode'), [('admin', 'admin123', '123456')])
    def test_goto_course_success(self, login_page, course_page, username, password, authcode):
        msg = course_page.goto_course_interface()
        print(msg)
        assert msg == "科目管理"

    # @pytest.mark.parametrize(('cour_code', 'cour_name'), [('1313', 'testing')])
    def test_add_course_exist(self, login_page, course_page):
        cour_code = random.randint(100100, 110000)
        cour_name = "test" + str(random.randint(1, 1000))
        course_page.add_course(cour_code, cour_name)
        # txt = course_page.add_course_success_msg()      #因为新增成功的弹框的xpath抓取的不对所以这个弹框校验后续优化
        # assert txt == " 新增成功"
        title = course_page.pop_up()
        assert title == '科目管理'
        time.sleep(2)
        course_page.add_course(cour_code, cour_name)
        time.sleep(2)
        txt = course_page.add_course_exist_msg()
        assert txt == "科目编码[{}]已存在!".format(cour_code)

    @pytest.mark.parametrize(( 'cour_name'), [('testing')])
    def test_add_course_success(self, login_page, course_page, cour_name):
        cour_code = random.randint(100100, 110000)
        course_page.add_course(cour_code, cour_name)
        time.sleep(1)
        txt = course_page.add_course_success_msg()
        assert txt == "添加成功"

    @pytest.mark.parametrize(('cour_name'), [('')])
    def test_empty_course_name(self, login_page, course_page, cour_name):
        cour_code = random.randint(100100, 110000)
        course_page.add_course(cour_code, cour_name)
        txt = course_page.course_name_error_msg()
        assert txt == "请输入科目名称"

    @pytest.mark.parametrize(('cour_name'),  [('12345678910'), ('testing12345')])
    def test_empty_course_name(self, login_page, course_page, cour_name):
        cour_code = random.randint(100100, 110000)
        course_page.add_course(cour_code, cour_name)
        txt = course_page.course_name_error_msg()
        assert txt == "超过10个字符限制"

    @pytest.mark.parametrize(('cour_code'), [('')])
    def test_empty_course_name(self, login_page, course_page, cour_code):
        cour_name = "test" + str(random.randint(1, 100))
        course_page.add_course(cour_code, cour_name)
        time.sleep(2)
        txt = course_page.course_code_error_msg()
        assert txt == "请输入科目编码"

    @pytest.mark.parametrize(('cour_code'), [('nihao'), ('你好'), ('123456789112345678911234567891123456789112345678911')])
    def test_error_course_code(self, login_page, course_page, cour_code):
        cour_name = "test" + str(random.randint(1, 100))
        course_page.add_course(cour_code, cour_name)
        time.sleep(3)
        txt = course_page.course_code_error_msg()
        assert txt == "超过50个字符限制或编码错误"

    def test_empty_course_kind(self, login_page, course_page):
        cour_name = "test" + str(random.randint(1, 100))
        cour_code = random.randint(100100, 110000)
        course_page.add_course_kind_empty(cour_code, cour_name)
        time.sleep(1)
        txt = course_page.course_kind_error_msg()
        assert txt == "请选择类别"

    def test_edit_course_error(self, login_page, course_page):
        cour_code = 1001110
        course_page.edit_course_kind_error(cour_code)
        time.sleep(2)
        txt = course_page.edit_course_error_msg()
        assert txt == "科目编码[{}]已被其它科目占用!".format(cour_code)

    # def test_edit_course_error(self, login_page, course_page):
    #     cour_code = 1000
    #     cour_name = 'testing'
    #     course_page.edit_course_empty(cour_code, cour_name)
    #     # txt1 = course_page.course_code_error_msg()
    #     # assert txt1 == "请输入科目编码"
    #     # txt = course_page.course_name_error_msg()
    #     # assert txt == "请输入科目名称"
    #     ## txt = course_page.course_update_success_msg()
    #     ## assert txt == "更新成功"

    def test_edit_course_success(self, login_page, course_page):
        course_page.edit_course_success()
        time.sleep(2)
        txt = course_page.course_update_success_msg()
        assert txt == '更新成功'


    # def test_accout_kind_exist_add(self, login_page, course_page):
    #     cour_name = "test" + str(random.randint(1, 100))
    #     cour_code = random.randint(100100, 110000)
    #     course_page.accout_kind_exist_add(cour_code, cour_name)
    #     txt = course_page.account_kind_exist_add_msg()
    #     assert txt == '请删除账户类别后添加下级科目'


    # def test_table_rows(self, login_page, course_page):
    #     course_page.goto_course_interface()
    #     list = course_page.get_table_rows()
    #     print(list)
