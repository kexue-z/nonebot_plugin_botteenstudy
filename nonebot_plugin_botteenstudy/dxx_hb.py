import os
import random
import string
import requests
import json
from bs4 import BeautifulSoup

path = os.path.dirname(__file__) + '/data'  # 数据存放目录
s = requests.session()


# 生成随机openid
def gen_rand_str(len):
    return ''.join(random.sample(string.ascii_letters + string.digits, len))


def get_code():
    """
        调用API获取最新一期青春学习的CODE
        :return:
        """

    url = "https://h5.cyol.com/special/weixin/sign.json"
    headers = {
        "Host": "h5.cyol.com",
        "Connection": "keep-alive",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; PACM00 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3164 MMWEBSDK/20211001 Mobile Safari/537.36 MMWEBID/556 MicroMessenger/8.0.16.2040(0x28001056) Process/toolsmp WeChat/arm32 Weixin NetType/WIFI Language/zh_CN ABI/arm64",
        "Origin": "http://h5.cyol.com",
        "X-Requested-With": "com.tencent.mm",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    resp = s.get(url, headers=headers).json()
    return list(resp)[-1]


def get_user(openid, send_id):
    headers = {
        "Host": "api.fjg360.cn",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; PACM00 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3164 MMWEBSDK/20211001 Mobile Safari/537.36 MMWEBID/556 MicroMessenger/8.0.16.2040(0x28001056) Process/toolsmp WeChat/arm32 Weixin NetType/WIFI Language/zh_CN ABI/arm64",
        "Accept": "*/*",
        "X-Requested-With": "com.tencent.mm",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Dest": "script",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    url = "https://api.fjg360.cn/index.php?m=vote&c=index&a=get_members&openid=" + openid
    resp = s.get(url, headers=headers).json()
    if resp.get("code") == 1:
        return resp.get("h5_ask_member")
    else:
        pass


def get_course(code):
    headers = {
        "Host": "h5.cyol.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; PACM00 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3164 MMWEBSDK/20211001 Mobile Safari/537.36 MMWEBID/556 MicroMessenger/8.0.16.2040(0x28001056) Process/toolsmp WeChat/arm32 Weixin NetType/WIFI Language/zh_CN ABI/arm64",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/wxpic,image/tpg,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "X-Requested-With": "com.tencent.mm",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    url = 'https://h5.cyol.com/special/daxuexi/' + code + '/m.html'
    resp = s.get(url, headers=headers)
    soup = BeautifulSoup(resp.content.decode("utf8"), "lxml")
    course = soup.title.string[7:]
    return course


def sent_user(openid, user_data, course):
    headers = {
        "Host": "cp.fjg360.cn",
        "Connection": "keep-alive",
        "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; PACM00 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3164 MMWEBSDK/20211001 Mobile Safari/537.36 MMWEBID/556 MicroMessenger/8.0.16.2040(0x28001056) Process/toolsmp WeChat/arm32 Weixin NetType/WIFI Language/zh_CN ABI/arm64",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    url = "https://cp.fjg360.cn/index.php?m=vote&c=index&a=save_door&sessionId=&imgTextId=&ip="
    url += "&username=" + user_data['name']
    url += "&phone=" + "未知"
    url += "&city=" + user_data['danwei1']
    url += "&danwei2=" + user_data['danwei3']
    url += "&danwei=" + user_data['danwei2']
    url += "&openid=" + openid
    url += "&num=10"
    url += "&lesson_name=" + course
    resp = s.get(url, headers=headers).json()
    if resp.get("code") == 1:
        return 1
    else:
        return 0


def start(send_id):
    with open(path + '/dxx_list.json', 'r', encoding='utf-8') as f:
        obj = json.load(f)
    mark = False
    state_code = 0
    for item in obj:
        if int(send_id) == int(item['qq']):
            openid = item['openid']
            code = get_code()
            course = get_course(code)
            user_data = get_user(openid, send_id)
            state_code = sent_user(openid, user_data, course)
            mark = True
            break
    if not mark:
        state_code = 0

    return state_code


async def start_use_hb(send_id):
    with open(path + '/dxx_list.json', 'r', encoding='utf-8') as f:
        obj = json.load(f)
    mark = False
    state_code = 0
    for item in obj:
        if int(send_id) == int(item['qq']):
            openid = item['openid']
            code = get_code()
            course = get_course(code)
            user_data = {'uid': '', 'name': item['name'], 'danwei1': item['danwei1'], 'danwei2': item['danwei2'],
                         'danwei3': item['danwei3'], 'class_name': ''}
            state_code = sent_user(openid, user_data, course)
            mark = True
            break
    if not mark:
        state_code = 0

    return state_code
