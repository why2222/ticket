import time
import schedule
import datetime

def job():
    while get_time() < 41:
        print("工作中......")
        time.sleep(5)
    print("结束任务")


def get_time():
    time_now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    # print(time_now)
    # hour = str(time_now).split("-")[3]
    minute = str(time_now).split("-")[4]
    # print(hour)
    return int(minute)

def clear():
    print("清楚定时任务......")
    schedule.cancel_job(job)

schedule.every().day.at("09:40").do(job)
# schedule.every().day.at("17:24").do(clear)

# schedule.every(5).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
    # get_time()
    # str_18 = "18"
    # if str_18 >= "7" :
    #     print("11111111")