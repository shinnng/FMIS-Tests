from typing import List

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, datetime
from loguru import logger
from conf.config import screenshot_path


class BasePage:

    def __init__(self, driver: WebElement):
        self.driver = driver

    def current_url(self):
            return self.driver.currentURL

    def wait_eleVisible(self, loc, timeout=20, poll_frequency=0.5, mark=None):
        """
        :param loc:元素定位表达;元组类型,表达方式(元素定位类型,元素定位方法)
        :param timeout:等待的上限
        :param poll_frequency:轮询频率
        :param mark:等待失败时,截图操作,图片文件中需要表达的功能标注
        :return:None
        """
        logger.info('{} 等待元素可见:{}'.format(mark, loc))
        try:
            start = time.time()
            WebDriverWait(self.driver, timeout, poll_frequency).until(EC.visibility_of_element_located(loc))
            end = time.time()
            logger.info('等待时长:%.2f 秒' % (end - start))
        except:
            logger.exception('{} 等待元素可见失败:{}'.format(mark, loc))
            # 截图
            self.save_webImgs(mark)
            raise

    # 等待元素不可见
    def wait_eleNoVisible(self, loc, timeout=20, poll_frequency=0.5, mark=None):
        """
        :param loc:元素定位表达;元组类型,表达方式(元素定位类型,元素定位方法)
        :param timeout:等待的上限
        :param poll_frequency:轮询频率
        :param mark:等待失败时,截图操作,图片文件中需要表达的功能标注
        :return:None
        """
        logger.info('{} 等待元素不可见:{}'.format(mark, loc))
        try:
            start = time.time()
            WebDriverWait(self.driver, timeout, poll_frequency).until_not(EC.visibility_of_element_located(loc))
            end = time.time()
            logger.info('等待时长:%.2f 秒' % (end - start))
        except:
            logger.exception('{} 等待元素不可见失败:{}'.format(mark, loc))
            # 截图
            self.save_webImgs(mark)
            raise

    # 查找一个元素element
    def find_Element(self, loc, mark=None) -> WebElement:
        logger.info('{} 查找元素 {}'.format(mark, loc))
        try:
            return self.driver.find_element(*loc)
        except:
            logger.exception('查找元素失败.')
            # 截图
            self.save_webImgs(mark)
            raise

    # 查找元素elements
    def find_Elements(self, loc, mark=None) -> List[WebElement]:
        logger.info('{} 查找元素 {}'.format(mark, loc))
        try:
            logger.info(f'type == {type(self.driver.find_elements(*loc))}, eles == {self.driver.find_elements(*loc)}')
            return self.driver.find_elements(*loc)
        except:
            logger.exception('查找元素失败.')
            # 截图
            self.save_webImgs(mark)
            raise

    # 输入操作
    def input_Text(self, loc, text, mark=None):
        # 查找元素
        ele = self.find_Element(loc, mark)
        # 输入操作
        logger.info('{} 在元素 {} 中输入文本: {}'.format(mark, loc, text))
        try:
            ele.send_keys(text)
        except:
            logger.exception('输入操作失败')
            # 截图
            self.save_webImgs(mark)
            raise

    # 清除操作
    def clean_Input_Text(self, loc, mark=None):
        ele = self.find_Element(loc, mark)
        # 清除操作
        logger.info('{} 在元素 {} 中清除'.format(mark, loc))
        try:
            ele.clear()
            ele.send_keys('')
        except:
            logger.exception('清除操作失败')
            # 截图
            self.save_webImgs(mark)
            raise

    # 点击操作
    def click_Element(self, loc, mark=None):
        # 先查找元素在点击
        ele = self.find_Element(loc, mark)
        # 点击操作
        logger.info('{} 在元素 {} 中点击'.format(mark, loc))
        try:
            ele.click()
        except:
            logger.exception('点击操作失败')
            # 截图
            self.save_webImgs(mark)
            raise

    # 获取文本内容
    def get_Text(self, loc, mark=None):
        # 先查找元素再获取文本内容
        ele = self.find_Element(loc, mark)
        # 获取文本
        logger.info('{} 在元素 {} 中获取文本'.format(mark, loc))
        try:
            text = ele.text
            logger.info('{} 元素 {} 的文本内容为 {}'.format(mark, loc, text))
            return text
        except:
            logger.exception('获取元素 {} 的文本内容失败,报错信息如下:'.format(loc))
            # 截图
            self.save_webImgs(mark)
            raise

    # 获取属性值
    def get_Element_Attribute(self, loc, mark=None):
        # 先查找元素再去获取属性值
        ele = self.find_Element(loc, mark)
        # 获取元素属性值
        logger.info('{} 在元素 {} 中获取属性值'.format(mark, loc))
        try:
            ele_attribute = ele.get_attribute()
            logger.info('{} 元素 {} 的文本内容为 {}'.format(mark, loc, ele_attribute))
            return ele_attribute
        except:
            logger.exception('获取元素 {} 的属性值失败,报错信息如下:'.format(loc))
            self.save_webImgs(mark)
            raise

    # iframe 切换
    def switch_iframe(self, frame_refer, timeout=20, poll_frequency=0.5, mark=None):
        # 等待 iframe 存在
        logger.info('iframe 切换操作:')
        try:
            # 切换 == index\name\id\WebElement
            WebDriverWait(self.driver, timeout, poll_frequency).until(
                EC.frame_to_be_available_and_switch_to_it(frame_refer))
            time.sleep(0.5)
            logger.info('切换成功')
        except:
            logger.exception('iframe 切换失败!')
            # 截图
            self.save_webImgs(mark)
            raise

    # 窗口切换：new - 切换到新窗口，default - 回到默认的窗口
    def switch_window(self, name, cur_handles=None, timeout=20, poll_frequency=0.5, mark=None):
        """
        调用之前要获取window_handles
        :param name: new 代表最新打开的一个窗口. default 代表第一个窗口. 其他的值表示为窗口的 handles
        :param cur_handles:
        :param timeout:等待的上限
        :param poll_frequency:轮询频率
        :param mark:等待失败时,截图操作,图片文件中需要表达的功能标注
        :return:
        """
        try:
            if name == 'new':
                if cur_handles is not None:
                    logger.info('切换到最新打开的窗口')
                    WebDriverWait(self.driver, timeout, poll_frequency).until(EC.new_window_is_opened(cur_handles))
                    window_handles = self.driver.window_handles
                    self.driver.swich_to.window(window_handles[-1])
                else:
                    logger.exception('切换失败,没有要切换窗口的信息!')
                    self.save_webImgs(mark)
                    # raise
            elif name == 'default':
                logger.info('切换到默认页面')
                self.driver.switch_to.default()
            else:
                logger.info('切换到为 handles 的窗口')
                self.driver.swich_to.window(name)
        except:
            logger.exception('切换窗口失败!')
            # 截图
            self.save_webImgs(mark)
            raise

    # 截图
    def save_webImgs(self, mark=None):
        # filepath = 指图片保存目录/mark(页面功能名称)_当前时间到秒.png
        # 当前时间
        dateNow = str(datetime.datetime.now()).split('.')[0]
        # 路径
        filePath = '{}/{}_{}.png'.format(screenshot_path, mark, dateNow)
        try:
            self.driver.save_screenshot(filePath)
            logger.info('截屏成功,图片路径为{}'.format(filePath))
        except:
            logger.exception('截屏失败!')
