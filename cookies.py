import json

def get_cookies(driver):
    # 获取cookie
    cookies = driver.get_cookies()
    json_cookies = json.dumps(cookies)
    with open('./cookies.json', 'w') as f:
        f.write(json_cookies)

def add_cookies(driver):
    driver.delete_all_cookies()
    dict_cookies = {}
    with open('./cookies.json', 'r', encoding='utf-8') as f:
        list_cookies = json.loads(f.read())
    for i in list_cookies:
        driver.add_cookie(i)