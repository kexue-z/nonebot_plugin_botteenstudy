from datetime import datetime
import nonebot
import json
import os
from nonebot.log import logger

path = os.path.dirname(__file__) + '/data'


async def bot_start():
    try:
        friend_list = await nonebot.get_bot().get_friend_list()
        with open(path + '/friend_list.json', 'w', encoding='utf-8') as f:
            json.dump(friend_list, f, indent=4,ensure_ascii=False)
        group_list = await nonebot.get_bot().get_group_list()
        with open(path + '/group_list.json', 'w', encoding='utf-8') as f:
            json.dump(group_list, f, indent=4,ensure_ascii=False)
        code = 200
    except Exception as e:
        code = 404
        logger.error(f"{datetime.now()}: 错误信息：{e}")
    return code
