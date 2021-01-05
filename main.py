# 自动刷新灯塔在线视频
from selenium import webdriver
import time
import re  # 用于正则
from PIL import Image  # 用于打开图片和对图片处理
import pytesseract  # 用于图片转文字
from aip import AipOcr
import math


class AutoPlay():
    def __init__(self) -> None:
        self.driver = webdriver.Chrome(executable_path=r"F:\dtzx\chromedriver.exe")
        self.uid = "账号";
        self.pwd = "密码"
        self.url = "https://sso.dtdjzx.gov.cn/sso/login"

    def baiduOCR(self):  # picfile:图片
        # 百度提供
        """ 你的 APPID AK SK """
        img = self.img
        APP_ID = ''  # 应用的appid
        API_KEY = ''  # 应用的appkey
        SECRET_KEY = ''  # 应用的secretkey
        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        """ 调用通用文字识别（高精度版） """
        img.save("new.png")
        i = open("new.png", 'rb')
        img1 = i.read()
        message = client.basicAccurate(img1)
        # 输出文本内容
        for text in message.get('words_result'):  # 识别的内容
            return text.get('words')

    def get_pictures(self):
        self.driver.save_screenshot('pictures.png')  # 全屏截图
        page_snap_obj = Image.open('pictures.png')
        img = self.driver.find_element_by_id('yanzhengma')  # 验证码元素位置
        time.sleep(1)
        location = img.location
        size = img.size  # 获取验证码的大小参数
        left = location['x'] + 200
        top = location['y'] + 130
        right = left + size['width'] + 20
        bottom = top + size['height'] + 8
        image_obj = page_snap_obj.crop((left, top, right, bottom))  # 按照验证码的长宽，切割验证码
        # image_obj.show()  # 打开切割后的完整验证码
        # self.driver.close()  # 处理完验证码后关闭浏览器
        return image_obj

    def processing_image(self):
        image_obj = self.get_pictures()  # 获取验证码
        img = image_obj.convert("L")  # 转灰度
        pixdata = img.load()
        w, h = img.size
        threshold = 160
        # 遍历所有像素，大于阈值的为黑色
        for y in range(h):
            for x in range(w):
                if pixdata[x, y] < threshold:
                    pixdata[x, y] = 0
                else:
                    pixdata[x, y] = 255
        return img

    def delete_spot(self):
        images = self.processing_image()
        data = images.getdata()
        w, h = images.size
        black_point = 0
        for x in range(1, w - 1):
            for y in range(1, h - 1):
                mid_pixel = data[w * y + x]  # 中央像素点像素值
                if mid_pixel < 50:  # 找出上下左右四个方向像素点像素值
                    top_pixel = data[w * (y - 1) + x]
                    left_pixel = data[w * y + (x - 1)]
                    down_pixel = data[w * (y + 1) + x]
                    right_pixel = data[w * y + (x + 1)]
                    # 判断上下左右的黑色像素点总个数
                    if top_pixel < 10:
                        black_point += 1
                    if left_pixel < 10:
                        black_point += 1
                    if down_pixel < 10:
                        black_point += 1
                    if right_pixel < 10:
                        black_point += 1
                    if black_point < 1:
                        images.putpixel((x, y), 255)
                    black_point = 0
        # images.show()
        return images

    def image_str(self):
        image = self.delete_spot()
        self.img = image
        card_str = self.baiduOCR()
        # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # 设置pyteseract路径
        # result = pytesseract.image_to_string(image)  # 图片转文字
        # resultj = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", result)  # 去除识别出来的特殊字符
        # result_four = result[0:4]  # 只获取前4个字符
        # print(resultj)  # 打印识别的验证码
        card = ""
        if card_str is not None:
            card = card_str.replace(" ", "")
        return card

    def work(self):
        flag = "djzx"
        self.driver.get(self.url)
        self.driver.maximize_window()
        time.sleep(2)
        while len(flag) > 0:
            self.driver.refresh()
            self.driver.find_element_by_id("username").send_keys(self.uid)
            self.driver.find_element_by_id("password").send_keys(self.pwd)
            cardstr = str(self.image_str())
            print("验证码："+str(cardstr))
            self.driver.find_element_by_id("validateCode").send_keys(cardstr)
            # # 30秒钟内登录系统
            time.sleep(2)
            self.driver.find_element_by_xpath('//*[@id="loginForm"]/div[4]/a[1]').click()
            time.sleep(1)
            try:
                self.driver.find_element_by_id('validateCodeMessage')
            except:
                flag = ""
            # js = "return document.getElementById('validateCodeMessage').innerText"
            # flag = str(self.driver.execute_script(js))
        time.sleep(10)
        self.driver.find_element_by_xpath('/html/body/div[6]/div[3]/div/div/div[2]/div/div[1]/div[4]').click()
        time.sleep(2)
        toHandle = self.driver.window_handles
        self.driver.switch_to.window(toHandle[1])
        time.sleep(2)
        self.driver.find_element_by_xpath('//*[@id="app"]/div/div[3]/div/ul/li[10]/a').click()
        time.sleep(2)
        self.driver.find_element_by_xpath('//*[@id="app"]/div/div[3]/div/ul/li[10]/a').click()
        time.sleep(5)
        tr_list = self.driver.find_elements_by_xpath(
            '//*[@id="app"]/div/div[4]/div[4]/div/div[1]/div[3]/table/tbody/tr')
        list_count = len(tr_list)
        while list_count > 0:
            print(list_count)
            self.driver.find_element_by_xpath(
                '//*[@id="app"]/div/div[4]/div[4]/div/div[1]/div[3]/table/tbody/tr[1]/td[7]/div/span[2]/i').click()
            time.sleep(5)
            toHandle = self.driver.window_handles
            self.driver.switch_to.window(toHandle[2])
            js = "return parseInt(document.getElementsByTagName('video')[0].duration)"
            sc = self.driver.execute_script(js)
            #判断是否自动播放，如果没有播放则手动播放
            js = "return parseInt(document.getElementsByTagName('video')[0].currentTime)"
            start_time = self.driver.execute_script(js)
            time.sleep(3)
            js = "return parseInt(document.getElementsByTagName('video')[0].currentTime)"
            end_time = self.driver.execute_script(js)
            print("播放时间差:"+str(math.ceil(end_time) - math.ceil(start_time)))
            if math.ceil(end_time) - math.ceil(start_time) < 1:
                js = "return document.getElementsByTagName('video')[0].play()"
                self.driver.execute_script(js)
            #开启倍速，经验证无效
            js = "return document.getElementsByTagName('video')[0].playbackRate=2"
            self.driver.execute_script(js)
            js = "return parseInt(document.getElementsByTagName('video')[0].currentTime)"
            e_time = self.driver.execute_script(js)
            time.sleep(3)
            print("已播放时间:"+str(math.ceil(e_time)))
            print("开启定时："+str(math.ceil((sc-e_time)/2)+5))
            time.sleep(math.ceil((sc-e_time)/2) + 5)
            self.driver.close()
            toHandle = self.driver.window_handles
            self.driver.switch_to.window(toHandle[1])
            self.driver.refresh()
            time.sleep(10)
            tr_list = self.driver.find_elements_by_xpath(
                '//*[@id="app"]/div/div[4]/div[4]/div/div[1]/div[3]/table/tbody/tr')
            list_count = len(tr_list)


if __name__ == '__main__':
    auto_play = AutoPlay()
    auto_play.work();
