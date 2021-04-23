import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import send_email
import time
import datetime
import schedule
import train_station
import cookies


class getTicket(object):
    def __init__(self):
        self.login_url = "https://kyfw.12306.cn/otn/resources/login.html"
        self.initmy_url = "https://kyfw.12306.cn/otn/view/index.html"
        self.search_url = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"
        self.passengers_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        self.order_url = ""
        self.driver = webdriver.Chrome(executable_path="/Users/why/PycharmProjects/ticket/chromedriver")
        # self.driver2 = webdriver.Chrome(executable_path="/Users/why/PycharmProjects/ticket/chromedriver")
        # self.driver = webdriver.Chrome(executable_path="D:\\PycharmProjects\\ticket\\chromedriver.exe")
        # self.driver = webdriver.Safari(executable_path="/Applications/Safari.app/Contents/MacOS/Safari").get(self.login_url)

    def _get_time(self):
        time_now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # print(time_now)
        hour = str(time_now).split("-")[3]
        # minute = str(time_now).split("-")[4]
        # print(hour)
        return int(hour)

    def _error(self, error_content):
        send_email.send("程序异常！", error_content)

    def _login(self):
        self.driver.get(self.login_url)
        img_url = "./qr.png"
        while self.driver.find_element_by_id("J-qrImg").get_attribute("src") is None:
            pass
        # self.driver.save_screenshot(img_url)
        qr_url = self.driver.find_element_by_id("J-qrImg").get_attribute("src")
        json_qr_url = json.dumps(qr_url)
        with open('./qr_url.json', 'w') as f:
            f.write(json_qr_url)
        print(qr_url)
        # self.driver2.get(qr_url)
        # 隐示等待
        WebDriverWait(self.driver,1000).until(
            ec.url_to_be(self.initmy_url)
        )
        print("登录成功！")
        # 获取cookies
        cookies.get_cookies(self.driver)
        # 添加cookies到客户端
        # cookies.add_cookies(self.driver)



    def _order_ticket(self):
        # 添加cookies到客户端
        cookies.add_cookies(self.driver)
        # 1. 跳转到查余票的页面
        self.driver.get(self.search_url)

        # 温馨提示是否加载
        WebDriverWait(self.driver,1000).until(
            ec.presence_of_element_located((By.ID,"content_defaultwarningAlert_id"))
        )
        # 确认是否加载
        WebDriverWait(self.driver, 1000).until(
            ec.presence_of_element_located((By.ID, "qd_closeDefaultWarningWindowDialog_id"))
        )
        tip = self.driver.find_element_by_id("qd_closeDefaultWarningWindowDialog_id")
        # 确认是否加载
        WebDriverWait(self.driver, 1000).until(
            ec.element_to_be_clickable((By.ID,"qd_closeDefaultWarningWindowDialog_id"))
        )
        tip.click()

        # 输入出发地
        from_station = self.driver.find_element_by_id("fromStation")
        # from_station.send_keys(self.from_station)
        self.driver.execute_script("arguments[0].value = 'BJP';", from_station)

        # 输入目的地
        to_station = self.driver.find_element_by_id("toStation")
        # to_station.send_keys(self.to_station)
        self.driver.execute_script("arguments[0].value = 'LYF';", to_station)

        # 输入出发时间
        # 先通过日期输入框的id="train_date"来定位输入框，再通过removeAttribute方法移除"readonly"属性
        js = 'document.getElementById("train_date").removeAttribute("readonly");'
        # 调用js脚本
        depart_time = self.driver.find_element_by_id("train_date")
        self.driver.execute_script(js)
        depart_time.clear()
        depart_time.send_keys(self.depart_time)
        depart_time.click()

        # 选择普票
        tickit_type_btn = self.driver.find_element_by_id("sf1_label")
        tickit_type_btn.click()


        # 2. 等待用户填写出发地
        WebDriverWait(self.driver,1000).until(
            ec.text_to_be_present_in_element_value((By.ID,"fromStation"),self.from_station)
        )

        # 3. 等待用户填写目的地
        WebDriverWait(self.driver, 1000).until(
            ec.text_to_be_present_in_element_value((By.ID, "toStation"), self.to_station)
        )

        # 4. 等待用户填写出发时间
        WebDriverWait(self.driver, 1000).until(
            ec.text_to_be_present_in_element_value((By.ID, "train_date"), self.depart_time)
        )

        # 5. 等待是否可以点击查询按钮
        WebDriverWait(self.driver,1000).until(
            ec.element_to_be_clickable((By.ID,"query_ticket"))
        )

        # 无票循环刷新查询
        while(self.order_success == 0 and 7 <= self._get_time() < 23):
            # # 查询次数
            # self.query_count += 1
            # print("查询" + str(self.query_count) + "次")
            # 6. 如果可以点击查询按钮，找到查询按钮，执行点击事件
            searchBtn = self.driver.find_element_by_id("query_ticket")
            try:
                WebDriverWait(self.driver,1000).until(
                    ec.element_to_be_clickable((By.ID,"query_ticket"))
                )
                searchBtn.click()
            except Exception as e:
                # self._error("查询按钮不可以点击")
                print("###错误：查询按钮不可以点击！")
                pass
                continue


            # 7. 等待车次信息是否显示
            try:
                WebDriverWait(self.driver, 0.5).until(
                    ec.presence_of_element_located((By.XPATH, ".//tbody[@id='queryLeftTable']/tr"))
                )
            except Exception as e:
                print("###错误：未加载出车次信息！")
                # self._error("未加载出车次信息")
                pass
                continue
            WebDriverWait(self.driver, 1000).until(
                ec.element_to_be_clickable((By.ID, "query_ticket"))
            )
            self.driver.find_element_by_id("query_ticket").click()

            # 8. 找到所有没有datatran属性的tr标签，这些标签是存储车次信息的
            tr_list = self.driver.find_elements_by_xpath(".//tbody[@id='queryLeftTable']/tr[not(@datatran)]")

            # 9. 遍历tr_list
            for tr in tr_list:
                train_number = tr.find_element_by_class_name("number").text
                # print(train_number)
                # print('='*20)
                if train_number in self.trains:
                    left_ticket = tr.find_element_by_xpath(".//td[4]").text
                    if left_ticket == "有":
                        print(train_number + "：有票")
                        orderBtn = tr.find_element_by_class_name("btn72")
                        orderBtn.click()

                        # 等待是否来到确认乘客的页面
                        WebDriverWait(self.driver,1000).until(
                            ec.url_to_be(self.passengers_url)
                        )
                        print("乘客页面已加载")

                        # 等待所有乘客信息加载进来
                        WebDriverWait(self.driver,1000).until(
                            ec.presence_of_element_located((By.XPATH,".//ul[@id='normal_passenger_id']/li"))
                        )
                        # 找到所有label标签，这些标签中存储的是用户信息
                        passenger_list = self.driver.find_elements_by_xpath(".//ul[@id='normal_passenger_id']/li/label")
                        for passenger in passenger_list:
                            passenger_name = passenger.text
                            if passenger_name in self.passengers:
                                passenger.click()

                        # 获取提交订单的按钮
                        submitBtn = self.driver.find_element_by_id("submitOrder_id")
                        submitBtn.click()

                        # # 学生票确认信息
                        # WebDriverWait(self.driver, 1000).until(
                        #     ec.presence_of_element_located((By.ID, "dialog_xsertcj"))
                        # )
                        # xsBtn = self.driver.find_element_by_id("dialog_xsertcj_cancel")
                        # WebDriverWait(self.driver, 1000).until(
                        #     ec.element_to_be_clickable((By.ID, "dialog_xsertcj_cancel"))
                        # )
                        # xsBtn.click()

                        # 判断提示框是否加载
                        WebDriverWait(self.driver,1000).until(
                            ec.presence_of_element_located((By.ID,"checkticketinfo_id"))
                        )
                        # 判断确认按钮是否加载
                        WebDriverWait(self.driver,1000).until(
                            ec.presence_of_element_located((By.ID,"qr_submit_id"))
                        )
                        # 判断确认按钮是否可以点击
                        WebDriverWait(self.driver, 1000).until(
                            ec.element_to_be_clickable((By.ID, "qr_submit_id"))
                        )
                        qr_submitBtn = self.driver.find_element_by_id("qr_submit_id")
                        time.sleep(1)
                        qr_submitBtn.click()
                        # while qr_submitBtn:
                        #     WebDriverWait(self.driver, 1000).until(
                        #         ec.element_to_be_clickable((By.ID, "qr_submit_id"))
                        #     )
                        #     qr_submitBtn.click()
                        #     qr_submitBtn = self.driver.find_element_by_id("qr_submit_id")

                        # # 等待是订单页面加载
                        # WebDriverWait(self.driver, 1000).until(
                        #     ec.url_to_be(self.order_url)
                        # )

                        # # 判断订单页面是否已经加载
                        # WebDriverWait(self.driver, 1000).until(
                        #     ec.element_to_be_clickable((By.CLASS_NAME, "lay-hd"))
                        # )
                        # 判断车票信息是否已经加载
                        WebDriverWait(self.driver, 1000).until(
                            ec.element_to_be_clickable((By.ID, "show_ticket_message"))
                        )
                        title = self.driver.find_element_by_id("show_title_ticket")
                        title_time = title.find_element_by_xpath(".//strong[1]").text
                        title_train_number = title.find_element_by_xpath(".//strong[2]").text
                        title_from = title.find_element_by_xpath(".//strong[3]").text
                        title_to = title.find_element_by_xpath(".//strong[4]").text.split("）")[1]
                        print("时间：" + title_time + "；车次：" + title_train_number + "；出发地：" + title_from + "；目的地：" + title_to)
                        # email_title = "时间：" + title_time + "；车次：" + title_train_number + "；出发地：" + title_from + "；目的地：" + title_to
                        email_title = "【车票预订成功】-" + title_time + " " + title_train_number + " " + title_from + title_to

                        # 找到所有车票信息
                        ticket_list = self.driver.find_elements_by_xpath(".//tbody[@id='show_ticket_message']/tr")
                        content_list = []
                        for ticket in ticket_list:
                            ticket_name = ticket.find_element_by_xpath(".//td[2]").text
                            ticket_kind = ticket.find_element_by_xpath(".//td[5]").text
                            ticket_level = ticket.find_element_by_xpath(".//td[6]").text
                            ticket_carriage = ticket.find_element_by_xpath(".//td[7]").text
                            ticket_seat = ticket.find_element_by_xpath(".//td[8]").text
                            ticket_price = ticket.find_element_by_xpath(".//td[9]").text
                            print("姓名：" + ticket_name + "；票种：" + ticket_kind + "；席别：" + ticket_level + "；车厢：" + ticket_carriage + ";席位号：" + ticket_seat + "；票价：" + ticket_price)
                            content = "姓名：" + ticket_name + "；票种：" + ticket_kind + "；席别：" + ticket_level + "；车厢：" + ticket_carriage + ";席位号：" + ticket_seat + "；票价：" + ticket_price
                            content_list.append(content)

                        email_content = ""
                        for content in content_list:
                            email_content += content
                            email_content += "\n"
                        print("邮件内容：" + email_content)

                        send_email.send(email_title, email_content)
                        self.order_success = 1
                        self.query_count = 0
                        return

                    else:
                        print(train_number + "：无票")
            # 查询次数
            self.query_count += 1
            print("查询" + str(self.query_count) + "次")
            print("=" * 20)
            # time.sleep(1)

    def run(self):
        self.wait_input()
        self._login()
        # 定时启动
        if (self._get_time() >= 7) and (self._get_time() < 23):
            self._order_ticket()
        schedule.every().day.at('07:00').do(self._order_ticket)
        while True:
            schedule.run_pending()
            time.sleep(1)
        # self._order_ticket()

    def wait_input(self):
        # self.from_station = input("出发地：")
        # self.to_station = input("目的地：")
        # self.depart_time = input("出发时间：")
        # self.passengers = input("乘客姓名（如有多名乘客，用英文逗号隔开）：").split(",")
        # self.trains = input("车次（如有多趟车次，用英文逗号隔开）：").split(",")

        # 测试
        # 北京："BJP" 深圳："SZQ" 洛阳：LYF
        self.from_station = "BJP"
        self.to_station = "LYF"
        # self.to_station = train_station.station.stations("北京")
        self.depart_time = "2021-04-30"
        self.passengers = "吴昊昱"
        self.trains = ["G871","G673","G663","G665"]
        # self.trains = ["G871"]
        self.order_success = 0
        self.query_count = 0

if __name__ == '__main__':
    spider = getTicket()
    spider.run()
    # send_email.send("主题", "测试邮件内容 传参")