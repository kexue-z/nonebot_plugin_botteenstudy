import json
import os
import secrets
import requests
from anti_useragent import UserAgent

path = os.path.dirname(__file__) + '/data'  # 数据存放目录


def makeHeader(openid):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Connection': 'close',
        'Content-Type': 'application/json;charset=UTF-8',
        'Cookie': 'JSESSIONID=' + secrets.token_urlsafe(40),
        'Host': 'www.jxqingtuan.cn',
        'Origin': 'http://www.jxqingtuan.cn',
        'Referer': 'http://www.jxqingtuan.cn/html/h5_index.html?&accessToken=' + openid,
        'User-Agent': UserAgent(platform="iphone").wechat,
        'X-Requested-With': 'XMLHttpRequest'
    }
    return headers


def getIDInfo(nid, headers):
    url = "http://www.jxqingtuan.cn/pub/vol/config/organization?pid=" + nid
    res = json.loads(requests.get(url, headers=headers).text)
    if res.get("status") == 200:
        return res.get("result")
    else:
        print("查询组织导致未知错误：" + res.text)


def getCourse(headers):
    url = "http://www.jxqingtuan.cn/pub/vol/volClass/current"
    coursejson = requests.get(url, headers=headers).json()
    course = coursejson.get("result")
    try:
        return course.get("id")
    except:
        pass


def getStudy(course, nid, subOrg, cardNo, headers):
    url = "http://www.jxqingtuan.cn/pub/vol/volClass/join?accessToken="
    if len(subOrg) > 0:
        data = {"course": course, "nid": nid, "cardNo": cardNo, "subOrg": subOrg}
    else:
        data = {"course": course, "nid": nid, "cardNo": cardNo}
    res = json.loads((requests.post(url=url, data=json.dumps(data), headers=headers)).text)
    if res.get("status") == 200:
        return 1
    else:
        return 0


async def start_use_jx(send_id):
    with open(path + '/dxx_list.json', 'r', encoding='utf-8') as f:
        obj = json.load(f)
    mark = False
    state_code = 0
    for item in obj:
        if int(send_id) == int(item['qq']):
            openid = item['openid']
            nid = item['nid']
            name = item['name']
            suborg = ''
            headers = makeHeader(openid)
            resp = getIDInfo(nid, headers)
            course = getCourse(headers)
            state_code = getStudy(course=course, nid=nid, subOrg=suborg, cardNo=name, headers=headers)
            mark = True
            break
    if not mark:
        state_code = 0
    return state_code
