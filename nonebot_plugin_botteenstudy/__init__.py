import os
import json
import time
import asyncio
from datetime import datetime

import nonebot
from nonebot.log import logger
from nonebot.rule import to_me
from nonebot.plugin import on_command, on_message, on_request
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (Event, MessageSegment,
                                         FriendRequestEvent,
                                         PrivateMessageEvent)

from .dxx_hb import start, gen_rand_str, start_use_hb
from .dxx_jx import start_use_jx
from .get_src import get_pic
from .msg_pic import pic
from .bot_start import start as botstart

super_id = nonebot.get_driver().config.superusers  # 超管id
path = os.path.dirname(__file__) + "/data"  # 数据存放目录
pic_msg = False  # 初始机器人图片回复状态，默认关闭
to_su = True  # 将私聊消息转发给超管,默认打开
# 开启机器人图片回复功能
pic_msg_open = on_command(
    "开启图片回复", aliases={"图片回复开"}, rule=to_me(), permission=SUPERUSER
)


@pic_msg_open.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    global pic_msg
    pic_msg = True
    if send_id in super_id:
        message = "机器人开启图片回复成功!"
        pict = await pic(message)
        await nonebot.get_bot().send(
            user_id=send_id,
            message=MessageSegment.image(pict),
            event=event,
            at_sender=True,
        )


# 关闭机器人图片回复功能
pic_msg_close = on_command(
    "关闭图片回复", aliases={"图片回复关"}, rule=to_me(), permission=SUPERUSER
)


@pic_msg_close.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    global pic_msg
    pic_msg = False
    if send_id in super_id:
        message = "机器人关闭图片回复成功!"
        await nonebot.get_bot().send(
            user_id=send_id, message=message, event=event, at_sender=True
        )


# 初始化机器人
bot_data = on_command("加载bot数据", aliases={"bot开机", "机器人开机"}, permission=SUPERUSER)


@bot_data.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    code = await botstart()
    if pic_msg:
        if code == 200:
            message = "Bot数据加载成功！"
            pict = await pic(message)
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    at_sender=True,
                    event=event,
                )
        else:
            message = "Bot数据加载失败！"
            pict = await pic(message)
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
        pass
    else:
        if code == 200:
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id, message="Bot数据加载成功！", at_sender=True, event=event
                )
        else:
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id, message="Bot数据加载失败！", event=event, at_sender=True
                )


# 查看机器人好友列表
check_friend_list = on_command(
    "查看bot好友列表", aliases={"查看机器人好友列表", "查看好友列表"}, permission=SUPERUSER
)


@check_friend_list.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    with open(path + "/friend_list.json", "r", encoding="utf-8") as f:
        friend_list = json.load(f)
    message = "<-->好友昵称<-->好友备注<--->好友QQ号\n"
    num = 1
    for item in friend_list:
        nickname = item["nickname"]
        remark = item["remark"]
        user_id = item["user_id"]
        message = message + f"<-{num}->{nickname}<-->{remark}<-->{user_id}\n"
        num += 1
    if pic_msg:
        pict = await pic(message)
        if send_id in super_id:
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
    else:
        if send_id in super_id:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )


# 查询机器人群列表
check_group_list = on_command("查看bot群列表", aliases={"查看机器人群列表"}, permission=SUPERUSER)


@check_group_list.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    with open(path + "/group_list.json", "r", encoding="utf-8") as f:
        group_list = json.load(f)
    message = "<-->群昵称<--->群号\n"
    num = 1
    for item in group_list:
        group_name = item["group_name"]
        group_id = item["group_id"]
        message = message + f"<-{num}->{group_name}<-->{group_id}\n"
        num += 1
    if pic_msg:
        pict = await pic(message)
        if send_id in super_id:
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
    else:
        if send_id in super_id:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )


# 将私聊机器人的消息转发给超管
formsg = on_message(priority=5)


@formsg.handle()
async def _(event: PrivateMessageEvent):
    sent_id = event.get_user_id()
    try:
        if to_su:
            if sent_id not in super_id:
                msg = event.get_message()
                with open(path + "/friend_list.json", "r", encoding="utf-8") as f:
                    friend_list = json.load(f)
                name = ""
                for item in friend_list:
                    send_id = item["user_id"]
                    if int(sent_id) == int(send_id):
                        name = item["remark"]
                message = f"机器人好友：{name}({sent_id})\n向机器人发送了一条消息！\n消息内容：" + str(msg)
                for su in super_id:
                    await nonebot.get_bot().send_msg(
                        message_type="private",
                        user_id=int(su),
                        message=message,
                        at_sender=True,
                    )
        else:
            pass
    except Exception as e:
        for su in super_id:
            await nonebot.get_bot().sent_msg(
                message_type="private",
                user_id=int(su),
                message=f"错误信息{e}",
                at_sender=True,
            )


# 关闭私聊信息转给超管
formsg_close = on_command(
    "私聊转发关", aliases={"消息转发关", "formsg_close"}, permission=SUPERUSER
)


@formsg_close.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    global to_su
    to_su = False
    if send_id in super_id:
        message = "机器人关闭私聊转发成功!"
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.text(message),
                event=event,
                at_sender=True,
            )


# 开启私聊转发给超管
formsg_open = on_command(
    "私聊转发开", aliases={"消息转发开", "formsg_open"}, permission=SUPERUSER
)


@formsg_open.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    global to_su
    to_su = True
    if send_id in super_id:
        message = "机器人开启私聊转发成功!"
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.text(message),
                event=event,
                at_sender=True,
            )


# 机器人添加好友事件
add_friend = on_request(priority=5, block=True)


@add_friend.handle()
async def _(event: FriendRequestEvent):
    try:
        add_req = json.loads(event.json())
        add_qq = add_req["user_id"]  # 请求添加QQ号
        flag = add_req["flag"]
        realtime = time.strftime(
            "%Y年%m月%d日 %H:%M:%S", time.localtime(add_req["time"])
        )  # 请求添加时间
        with open(path + "/add_friend.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        if len(obj) == 0:
            data = []
            t = {"add_qq": add_qq, "flag": flag, "time": realtime}
            comment = add_req["comment"]  # 验证信息
            data.append(t)
            with open(path + "/add_friend.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            message = f"QQ：{add_qq}请求添加机器人为好友！\n验证信息：{comment}\n{realtime}"
            if pic_msg:
                pict = await pic(message)
                for su in super_id:
                    await nonebot.get_bot().send_msg(
                        message_type="private",
                        user_id=int(su),
                        message=MessageSegment.image(pict),
                        at_sender=True,
                    )
            else:
                for su in super_id:
                    await nonebot.get_bot().send_msg(
                        message_type="private",
                        user_id=int(su),
                        message=message,
                        at_sender=True,
                    )
        else:
            num = False
            for item in obj:
                if int(add_qq) == int(item["add_qq"]):
                    num = True
                    break
                else:
                    num = False
            if not num:
                data = []
                t = {"add_qq": add_qq, "flag": flag, "time": realtime}
                comment = add_req["comment"]  # 验证信息
                data.append(t)
                with open(path + "/add_friend.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                message = f"QQ：{add_qq}请求添加机器人为好友！\n验证信息：{comment}\n{realtime}"
                if pic_msg:
                    pict = await pic(message)
                    for su in super_id:
                        await nonebot.get_bot().send_msg(
                            message_type="private",
                            user_id=int(su),
                            message=MessageSegment.image(pict),
                            at_sender=True,
                        )
                else:
                    for su in super_id:
                        await nonebot.get_bot().send_msg(
                            message_type="private",
                            user_id=int(su),
                            message=message,
                            at_sender=True,
                        )
    except Exception as e:
        message = f"机器人出错了！\n错误信息：{e}"
        if pic_msg:
            pict = await pic(message)
            for su in super_id:
                await nonebot.get_bot().send_msg(
                    message_type="private",
                    user_id=int(su),
                    message=MessageSegment.image(pict),
                    at_sender=True,
                )
        else:
            for su in super_id:
                await nonebot.get_bot().send_msg(
                    message_type="private",
                    user_id=int(su),
                    message=f"机器人出错了！\n错误信息：{e}",
                    at_sender=True,
                )


# 同意机器人添加好友
agree_add_friend = on_command("同意添加好友", permission=SUPERUSER)


@agree_add_friend.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        agree_id = int(str(event.get_message()).split("#")[-1])
        with open(path + "/add_friend.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        mark = False
        list1 = {}
        for item in obj:
            if agree_id == int(item["add_qq"]):
                flag = item["flag"]
                list1 = item
                await nonebot.get_bot().set_friend_add_request(
                    flag=flag, approve=True, remark=""
                )
                await botstart()
                message = f"已同意添加{agree_id}为好友！"
                if pic_msg:
                    pict = await pic(message)
                    if send_id in super_id:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.image(pict),
                            event=event,
                            at_sender=True,
                        )
                else:
                    if send_id in super_id:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=message,
                            event=event,
                            at_sender=True,
                        )
                mark = True
                break
        if not mark:
            message = f"失败！\nQQ:{agree_id}不在申请列表中。"
            if pic_msg:
                pict = await pic(message)
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        event=event,
                        at_sender=True,
                    )
            else:
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id, message=message, event=event, at_sender=True
                    )
        else:
            obj.remove(list1)
            with open(path + "/add_friend.json", "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=4, ensure_ascii=False)
    except Exception as e:
        message = f"出错了\n错误信息：{e}"
        if pic_msg:
            pict = await pic(message)
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
        else:
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id, message=message, event=event, at_sender=True
                )


# 拒绝机器人添加好友
refuse_add_friend = on_command("拒绝添加好友", permission=SUPERUSER)


@refuse_add_friend.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        agree_id = int(str(event.get_message()).split("#")[-1])
        with open(path + "/add_friend.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        mark = False
        list1 = {}
        for item in obj:
            if agree_id == int(item["add_qq"]):
                flag = item["flag"]
                list1 = item
                await nonebot.get_bot().set_friend_add_request(flag=flag, approve=False)
                await botstart()
                message = f"已拒绝添加{agree_id}为好友！"
                if pic_msg:
                    pict = await pic(message)
                    if send_id in super_id:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.image(pict),
                            event=event,
                            at_sender=True,
                        )
                else:
                    if send_id in super_id:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=message,
                            event=event,
                            at_sender=True,
                        )
                mark = True
                break
        if not mark:
            message = f"失败！\nQQ:{agree_id}不在申请列表中。"
            if pic_msg:
                pict = await pic(message)
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        event=event,
                        at_sender=True,
                    )
            else:
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id, message=message, event=event, at_sender=True
                    )
        else:
            obj.remove(list1)
            with open(path + "/add_friend.json", "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=4, ensure_ascii=False)
    except Exception as e:
        message = f"出错了\n错误信息：{e}"
        if pic_msg:
            pict = await pic(message)
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
        else:
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id, message=message, event=event, at_sender=True
                )


# 查看好友请求列表
add_qq_list = on_command("查看好友申请列表", permission=SUPERUSER)


@add_qq_list.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        with open(path + "/add_friend.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        message = ""
        num = 1
        for item in obj:
            message = f"{num}:" + message + item["add_qq"] + "\n"
            num += 1
        if not obj:
            message = "好友请求列表为空！"
            if pic_msg:
                pict = await pic(message)
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        event=event,
                        at_sender=True,
                    )
            else:
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id, message=message, event=event, at_sender=True
                    )
        else:
            if pic_msg:
                pict = await pic(message)
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        event=event,
                        at_sender=True,
                    )
            else:
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id, message=message, event=event, at_sender=True
                    )
    except Exception as e:
        message = f"出错了\n错误信息：{e}"
        if pic_msg:
            pict = await pic(message)
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
        else:
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id, message=message, event=event, at_sender=True
                )


# 删除好友指令
delete_friend = on_command("删除好友", permission=SUPERUSER)


@delete_friend.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        delete_id = int(str(event.get_message()).split("#")[-1])
        with open(path + "/friend_list.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        mark = False
        list1 = {}
        for item in obj:
            if delete_id == int(item["user_id"]):
                name = item["nickname"]
                list1 = item
                await nonebot.get_bot().delete_friend(friend_id=item["user_id"])
                message = f"已将{name}({delete_id})删除！"
                if pic_msg:
                    pict = await pic(message)
                    if send_id in super_id:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.image(pict),
                            event=event,
                            at_sender=True,
                        )
                else:
                    if send_id in super_id:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=message,
                            event=event,
                            at_sender=True,
                        )
                mark = True
                break
        if not mark:
            message = f"失败！\nQQ:{delete_id}不在好友列表中。"
            if pic_msg:
                pict = await pic(message)
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        event=event,
                        at_sender=True,
                    )
            else:
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id, message=message, event=event, at_sender=True
                    )
        else:
            obj.remove(list1)
            with open(path + "/friend_list.json", "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=4)
    except Exception as e:
        message = f"出错了\n错误信息：{e}"
        if pic_msg:
            pict = await pic(message)
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
        else:
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id, message=message, event=event, at_sender=True
                )


# 给好友发消息
sent_msg = on_command("发消息", aliases={"send"}, permission=SUPERUSER)


@sent_msg.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        sent_id = int(str(event.get_message()).split("#")[-2])
        with open(path + "/friend_list.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        mark = False
        for item in obj:
            if sent_id == int(item["user_id"]):
                name = item["nickname"]
                message = str(event.get_message()).split("#")[-1]
                message1 = f"成功向{name}({sent_id})发送消息！"
                if pic_msg:
                    pict = await pic(message1)
                    await nonebot.get_bot().send_msg(
                        message_type="private",
                        user_id=sent_id,
                        message=message,
                        at_sender=True,
                    )
                    if send_id in super_id:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.image(pict),
                            event=event,
                            at_sender=True,
                        )
                else:
                    await nonebot.get_bot().send_msg(
                        message_type="private",
                        user_id=sent_id,
                        message=message,
                        at_sender=True,
                    )
                    if send_id in super_id:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=message1,
                            event=event,
                            at_sender=True,
                        )
                mark = True
                break
        if not mark:
            message = f"失败！\nQQ:{sent_id}不在好友列表中。"
            if pic_msg:
                pict = await pic(message)
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        event=event,
                        at_sender=True,
                    )
            else:
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id, message=message, event=event, at_sender=True
                    )
    except Exception as e:
        message = f"出错了\n错误信息：{e}"
        if pic_msg:
            pict = await pic(message)
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
        else:
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id, message=message, event=event, at_sender=True
                )


# 给列表中所有的好友发消息（群发，慎用，易封号）
sent_msg_all = on_command("群发消息", aliases={"sent_all"}, permission=SUPERUSER)


@sent_msg_all.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    msg = "群发易封号，慎用！！！！！！"
    if pic_msg:
        pict = await pic(msg)
        if send_id in super_id:
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
    else:
        if send_id in super_id:
            await nonebot.get_bot().send(
                user_id=send_id, message=msg, event=event, at_sender=True
            )
    try:
        with open(path + "/friend_list.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        message1 = "已成功发送好友列表\n"
        num = 1
        for item in obj:
            sent_id = item["user_id"]
            name = item["nickname"]
            if sent_id in super_id:
                await asyncio.sleep(1.5)
                pass
            else:
                message = str(event.get_message()).split("#")[-1]
                if pic_msg:
                    await nonebot.get_bot().send_msg(
                        message_type="private",
                        user_id=sent_id,
                        message=message,
                        at_sender=True,
                    )
                else:
                    await nonebot.get_bot().send_msg(
                        message_type="private",
                        user_id=sent_id,
                        message=message,
                        at_sender=True,
                    )
                message1 = message1 + f"{num}<-->{name}<-->{sent_id}\n"
                await asyncio.sleep(1.5)
        if pic_msg:
            pict = await pic(message1)
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
        else:
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id, message=message1, event=event, at_sender=True
                )
    except Exception as e:
        message = f"出错了\n错误信息：{e}"
        if pic_msg:
            pict = await pic(message)
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
        else:
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id, message=message, event=event, at_sender=True
                )


# 机器人状态查询
bot_status = on_command("机器人状态", aliases={"bot_status"}, priority=5)


@bot_status.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        statistics = await nonebot.get_bot().get_status()
        packetreceived = statistics["stat"]["PacketReceived"]
        packetsent = statistics["stat"]["PacketSent"]
        packetlost = statistics["stat"]["PacketLost"]
        messagereceived = statistics["stat"]["MessageReceived"]
        messagesent = statistics["stat"]["MessageSent"]
        disconnecttimes = statistics["stat"]["DisconnectTimes"]
        losttimes = statistics["stat"]["LostTimes"]
        lastmessagetime = time.strftime(
            "%Y年%m月%d日 %H:%M:%S", time.localtime(statistics["stat"]["LastMessageTime"])
        )
        message = f"机器人状态\n收到的数据包总数:{packetreceived}\n发送的数据包总数:{packetsent}\n数据包丢失总数:{packetlost}\n接受信息总数:{messagereceived}\n发送信息总数:{messagesent}\nTCP 链接断开次数:{disconnecttimes}\n账号掉线次数:{losttimes}\n最后一条消息时间:{lastmessagetime}"
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )
    except Exception as e:
        message = f"出错了\n错误信息：{e}"
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )


# 机器人功能菜单
hele_list = on_command("帮助", aliases={"help"}, priority=5)


@hele_list.handle()
async def help_list(event: Event):
    send_id = event.get_user_id()
    try:
        message = "主人专用\n1、开启(关闭)图片回复|图片回复开(关)\n2、加载bot数据|bot开机|机器人开机\n3、查看好友列表|查看bot好友列表|查看机器人好友列表\n4、查看bot群列表|查看机器人群列表\n5、同意(拒绝)添加好友#QQ号\n6、查看好友申请列表\n7、删除好友#QQ号\n8、发消息(send)#QQ号#内容\n9、群发消息(send_all)#内容\n10私聊转发开(关)|消息转发开(关)\n全员可用\n1、机器人状态\n2、帮助、help\n3、大学习帮助、大学习功能、dxx_help"
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )
    except Exception as e:
        message = f"出错了\n错误信息：{e}"
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )


# 大学习功能，用于提交大学习，全员可用
dxx = on_command("提交大学习", aliases={"sub_dxx"}, priority=5)


@dxx.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        mark = False
        with open(path + "/dxx_list.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        for item in obj:
            if int(send_id) == int(item["qq"]):
                if item["area"] == "湖北":
                    code = await start_use_hb(send_id)
                elif item["area"] == "江西":
                    code = await start_use_jx(send_id)
                else:
                    code = 0
                mark = True
                if code == 1:
                    content = await get_pic()
                    end = content["end"]
                    area = item["area"]
                    name = item["name"]
                    openid = item["openid"]
                    danwei1 = item["danwei1"]
                    danwei2 = item["danwei2"]
                    danwei3 = item["danwei3"]
                    message = f"大学习提交成功!\n用户信息\n姓名：{name}\nQQ号:{send_id}\n地区：{area}\nopenid:{openid}\n学校：{danwei1}\n学院：{danwei2}\n班级：{danwei3}"
                    if pic_msg:
                        pict = await pic(message)
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.image(pict),
                            at_sender=True,
                            event=event,
                        )
                        await asyncio.sleep(1)
                        c = "你也可以点击链接进行截图以获取带手机状态栏的完成截图\nhttps://qndxx.scubot.live/\n如果QQ不能直接打开请复制到微信打开！"
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.text("完成截图\n")
                            + MessageSegment.image(end)
                            + MessageSegment.text(c),
                            event=event,
                            at_sender=True,
                        )
                    else:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=message,
                            event=event,
                            at_sender=True,
                        )
                        await asyncio.sleep(1)
                        c = "你也可以点击链接进行截图以获取带手机状态栏的完成截图\nhttps://qndxx.scubot.live/\n如果QQ不能直接打开请复制到微信打开！"
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.text("完成截图\n")
                            + MessageSegment.image(end)
                            + MessageSegment.text(c),
                            event=event,
                            at_sender=True,
                        )
                else:
                    message = "提交失败！"
                    if pic_msg:
                        pict = await pic(message)
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.image(pict),
                            at_sender=True,
                            event=event,
                        )
                    else:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=message,
                            event=event,
                            at_sender=True,
                        )
                break
        if not mark:
            message = "用户数据不存在，请先配置用户文件！"
            if pic_msg:
                pict = await pic(message)
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    at_sender=True,
                    event=event,
                )
            else:
                await nonebot.get_bot().send(
                    user_id=send_id, message=message, event=event, at_sender=True
                )
    except Exception as e:
        message = f"出错了\n错误信息:{e}"
        logger.error(f"{datetime.now()}: 错误信息：{e}")
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )


# 大学习功能，用于设置大学习配置，全员可用
set_dxx = on_command("设置大学习配置", aliases={"set_dxx"}, priority=5)


@set_dxx.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    mark = False
    try:
        with open(path + "/dxx_list.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        for item in obj:
            if int(send_id) == int(item["qq"]):
                message = "用户数据存在"
                if pic_msg:
                    pict = await pic(message)
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        event=event,
                        at_sender=True,
                    )
                else:
                    await nonebot.get_bot().send(
                        user_id=send_id, message=message, event=event, at_sender=True
                    )
                mark = True
                break
        if not mark:
            qq = int(send_id)
            area = str(event.get_message()).split("#")[-5]
            name = str(event.get_message()).split("#")[-4]
            openid = gen_rand_str(28)
            uid = "4836251"
            danwei1 = str(event.get_message()).split("#")[-3]
            danwei2 = str(event.get_message()).split("#")[-2]
            danwei3 = str(event.get_message()).split("#")[-1]
            class_name = "第十二季第13期"
            if area == "湖北":
                data = {
                    "qq": qq,
                    "area": area,
                    "openid": openid,
                    "uid": uid,
                    "name": name,
                    "danwei1": danwei1,
                    "danwei2": danwei2,
                    "danwei3": danwei3,
                    "class_name": class_name,
                }
                obj.append(data)
                with open(path + "/dxx_list.json", "w", encoding="utf-8") as f:
                    json.dump(obj, f, ensure_ascii=False, indent=4)
                code = await start_use_hb(send_id)
            elif area == "江西":
                with open(path + "/dxx_jx.json", "r", encoding="utf-8") as f:
                    n = json.load(f)
                mark1 = False
                nid = ""
                for item1 in n:
                    if (
                        item1["school"] == danwei1
                        and item1["college"] == danwei2
                        and item1["class"] == danwei3
                    ):
                        nid = item1["id3"]
                        mark1 = True
                        break
                if mark1:
                    data = {
                        "qq": qq,
                        "area": area,
                        "openid": openid,
                        "uid": uid,
                        "name": name,
                        "danwei1": danwei1,
                        "danwei2": danwei2,
                        "danwei3": danwei3,
                        "nid": nid,
                        "class_name": class_name,
                    }
                    obj.append(data)
                    with open(path + "/dxx_list.json", "w", encoding="utf-8") as f:
                        json.dump(obj, f, ensure_ascii=False, indent=4)
                    code = await start_use_jx(send_id)
                else:
                    code = 0
            else:
                code = 0
            if code == 1:
                message = f"大学习用户信息设置成功!\n用户信息\n姓名：{name}\nQQ号:{send_id}\n地区：{area}\nopenid:{openid}\n学校：{danwei1}\n学院：{danwei2}\n班级：{danwei3}"
                if pic_msg:
                    pict = await pic(message)
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        at_sender=True,
                        event=event,
                    )
                else:

                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.text(message),
                        at_sender=True,
                        event=event,
                    )
            else:
                message = "设置失败"
                if pic_msg:
                    pict = await pic(message)
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        at_sender=True,
                        event=event,
                    )
                else:
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.text(message),
                        at_sender=True,
                        event=event,
                    )
    except Exception as e:
        message = f"设置失败！您指令输入有误！\n正确指令格式：设置大学习配置#地区#姓名#学校名称#团委名称#班级\nps:班级名称一定要输入正确，不清楚请使用指令：查组织"
        logger.error(f"{datetime.now()}: 错误信息：{e}")
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )


delete_dxx = on_command("删除大学习配置", aliases={"删除大学习用户", "del_dxx"}, permission=SUPERUSER)


@delete_dxx.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        delete_id = int(str(event.get_message()).split("#")[-1])
        with open(path + "/dxx_list.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        mark = False
        list1 = {}
        for item in obj:
            if delete_id == int(item["qq"]):
                name = item["name"]
                list1 = item
                message = f"已将用户：{name}信息删除！"
                if pic_msg:
                    pict = await pic(message)
                    if send_id in super_id:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.image(pict),
                            event=event,
                            at_sender=True,
                        )
                else:
                    if send_id in super_id:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=message,
                            event=event,
                            at_sender=True,
                        )
                mark = True
                break
        if not mark:
            message = f"失败！\n用户QQ:{delete_id}不在大学习信息配置表中。"
            if pic_msg:
                pict = await pic(message)
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        event=event,
                        at_sender=True,
                    )
            else:
                if send_id in super_id:
                    await nonebot.get_bot().send(
                        user_id=send_id, message=message, event=event, at_sender=True
                    )
        else:
            obj.remove(list1)
            with open(path + "/dxx_list.json", "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=4)
    except Exception as e:
        message = f"出错了\n错误信息：{e}"
        if pic_msg:
            pict = await pic(message)
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
        else:
            if send_id in super_id:
                await nonebot.get_bot().send(
                    user_id=send_id, message=message, event=event, at_sender=True
                )


add_dxx = on_command("添加大学习配置", aliases={"添加大学习用户", "add_dxx"}, permission=SUPERUSER)


@add_dxx.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    qq = str(event.get_message()).split("#")[-6]
    mark = False
    try:
        with open(path + "/dxx_list.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        for item in obj:
            if int(qq) == int(item["qq"]):
                message = "用户数据存在"
                if pic_msg:
                    pict = await pic(message)
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        event=event,
                        at_sender=True,
                    )
                else:
                    await nonebot.get_bot().send(
                        user_id=send_id, message=message, event=event, at_sender=True
                    )
                mark = True
                break
        if not mark:
            area = str(event.get_message()).split("#")[-5]
            name = str(event.get_message()).split("#")[-4]
            openid = gen_rand_str(28)
            uid = "4836251"
            danwei1 = str(event.get_message()).split("#")[-3]
            danwei2 = str(event.get_message()).split("#")[-2]
            danwei3 = str(event.get_message()).split("#")[-1]
            class_name = "第十二季第13期"
            if area == "湖北":
                data = {
                    "qq": qq,
                    "area": area,
                    "openid": openid,
                    "uid": uid,
                    "name": name,
                    "danwei1": danwei1,
                    "danwei2": danwei2,
                    "danwei3": danwei3,
                    "class_name": class_name,
                }
                obj.append(data)
                with open(path + "/dxx_list.json", "w", encoding="utf-8") as f:
                    json.dump(obj, f, ensure_ascii=False, indent=4)
                code = await start_use_hb(qq)
            elif area == "江西":
                with open(path + "/dxx_jx.json", "r", encoding="utf-8") as f:
                    n = json.load(f)
                mark1 = False
                nid = ""
                for item1 in n:
                    if (
                        item1["school"] == danwei1
                        and item1["college"] == danwei2
                        and item1["class"] == danwei3
                    ):
                        nid = item1["id3"]
                        mark1 = True
                        break
                if mark1:
                    data = {
                        "qq": qq,
                        "area": area,
                        "openid": openid,
                        "uid": uid,
                        "name": name,
                        "danwei1": danwei1,
                        "danwei2": danwei2,
                        "danwei3": danwei3,
                        "nid": nid,
                        "class_name": class_name,
                    }
                    obj.append(data)
                    with open(path + "/dxx_list.json", "w", encoding="utf-8") as f:
                        json.dump(obj, f, ensure_ascii=False, indent=4)
                    code = await start_use_jx(qq)
                else:
                    code = 0
            else:
                code = 0
            if code == 1:
                message = f"大学习用户信息设置成功!\n用户信息\n姓名：{name}\nQQ号:{qq}\n地区：{area}\nopenid:{openid}\n学校：{danwei1}\n学院：{danwei2}\n班级：{danwei3}"
                if pic_msg:
                    pict = await pic(message)
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        at_sender=True,
                        event=event,
                    )
                else:

                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.text(message),
                        at_sender=True,
                        event=event,
                    )
            else:
                message = "设置失败"
                if pic_msg:
                    pict = await pic(message)
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        at_sender=True,
                        event=event,
                    )
                else:
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.text(message),
                        at_sender=True,
                        event=event,
                    )
    except Exception as e:
        message = f"设置失败！您指令输入有误！\n正确指令格式：添加大学习用户#QQ号#地区#姓名#学校名称#团委名称#班级\nps:班级名称一定要输入正确，不清楚请使用指令：查组织"
        logger.error(f"{datetime.now()}: 错误信息：{e}")
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )


check_dxx_list = on_command(
    "查看大学习用户列表", aliases={"check_dxx_list"}, permission=SUPERUSER
)


@check_dxx_list.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        message = "序号<-->QQ号<-->地区<-->姓名<-->团支部(班级)\n"
        with open(path + "/dxx_list.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        num = 1
        for item in obj:
            qq = item["qq"]
            area = item["area"]
            name = item["name"]
            danwei3 = item["danwei3"]
            message = message + f"{num}<-->{qq}<-->{area}<-->{name}<-->{danwei3}\n"
            num += 1
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )
    except Exception as e:
        message = f"出错了\n错误信息:{e}"
        logger.error(f"{datetime.now()}: 错误信息：{e}")
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )


check_dxx_user = on_command(
    "查看大学习用户", aliases={"check_dxx_user", "查看大学习配置"}, permission=SUPERUSER
)


@check_dxx_user.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        check_id = str(event.get_message()).split("#")[-1]
        with open(path + "/dxx_list.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        mark = False
        for item in obj:
            if int(check_id) == int(item["qq"]):
                area = item["area"]
                name = item["name"]
                openid = item["openid"]
                danwei1 = item["danwei1"]
                danwei2 = item["danwei2"]
                danwei3 = item["danwei3"]
                message = f"大学习用户信息查询成功！\n姓名：{name}\nQQ号：{check_id}\n地区：{area}\nopenid:{openid}\n学校：{danwei1}\n学院：{danwei2}\n团支部(班级)：{danwei3}"
                if pic_msg:
                    pict = await pic(message)
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        event=event,
                        at_sender=True,
                    )
                else:
                    await nonebot.get_bot().send(
                        user_id=send_id, message=message, event=event, at_sender=True
                    )
                mark = True
                break
        if not mark:
            message = f"大学习用户信息查询失败！\n用户：{check_id}不存在！"
            if pic_msg:
                pict = await pic(message)
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
            else:
                await nonebot.get_bot().send(
                    user_id=send_id, message=message, event=event, at_sender=True
                )
    except Exception as e:
        message = f"大学习用户信息查询失败！\n正确指令格式：查看大学习用户#QQ号"
        logger.error(f"{datetime.now()}: 错误信息：{e}")
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )


my_dxx = on_command("我的大学习", aliases={"查看我的大学习", "my_dxx"}, priority=5)


@my_dxx.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        check_id = int(send_id)
        with open(path + "/dxx_list.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        mark = False
        for item in obj:
            if int(check_id) == int(item["qq"]):
                area = item["area"]
                name = item["name"]
                openid = item["openid"]
                danwei1 = item["danwei1"]
                danwei2 = item["danwei2"]
                danwei3 = item["danwei3"]
                if area == "湖北":
                    message = f"大学习用户信息查询成功！\n姓名：{name}\nQQ号：{check_id}\n地区：{area}\nopenid:{openid}\n学校：{danwei1}\n学院：{danwei2}\n团支部(班级)：{danwei3}"
                elif area == "江西":
                    nid = item["nid"]
                    message = f"大学习用户信息查询成功！\n姓名：{name}\nQQ号：{check_id}\n地区：{area}\nopenid:{openid}\nnid:{nid}\n学校：{danwei1}\n学院：{danwei2}\n团支部(班级)：{danwei3}"
                else:
                    pass
                if pic_msg:
                    pict = await pic(message)
                    await nonebot.get_bot().send(
                        user_id=send_id,
                        message=MessageSegment.image(pict),
                        event=event,
                        at_sender=True,
                    )
                else:
                    await nonebot.get_bot().send(
                        user_id=send_id, message=message, event=event, at_sender=True
                    )
                mark = True
                break
        if not mark:
            message = f"大学习用户信息查询失败！\n用户：{check_id}不存在！"
            if pic_msg:
                pict = await pic(message)
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
            else:
                await nonebot.get_bot().send(
                    user_id=send_id, message=message, event=event, at_sender=True
                )
    except Exception as e:
        message = f"出错了\n错误信息:{e}"
        logger.error(f"{datetime.now()}: 错误信息：{e}")
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )


check_class = on_command("查组织", aliases={"查班级", "check_class"}, priority=5)


@check_class.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        area = str(event.get_message()).split("#")[-3]
        school = str(event.get_message()).split("#")[-2]
        college = str(event.get_message()).split("#")[-1]
        with open(path + f"/dxx_{area}.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        mark = False
        class_list = "序号<-->学校<-->班级\n"
        num = 1
        for item in obj:
            if school == item["school"] and college == item["college"]:
                class_name = item["class"]
                class_list = class_list + f"{num}<-->{school}<-->{class_name}\n"
                mark = True
                num += 1
        if mark:
            if pic_msg:
                pict = await pic(class_list)
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
            else:
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.text(class_list),
                    event=event,
                    at_sender=True,
                )
        else:
            message = f"查询失败！\n请检查学校或团委名称是否输入正确！\n正确指令格式：查组织#地区简写(例江西为：jx)#学校名称#团委名称"
            if pic_msg:
                pict = await pic(message)
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    event=event,
                    at_sender=True,
                )
            else:
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.text(message),
                    event=event,
                    at_sender=True,
                )
    except Exception as e:
        message = f"查询失败！\n正确指令格式：查组织#地区简写(例江西为：jx)#学校名称#团委名称"
        logger.error(f"{datetime.now()}: 错误信息：{e}")
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )


dxx_help = on_command("大学习帮助", aliases={"大学习功能", "dxx_help"}, priority=5)


@dxx_help.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    try:
        message = (
            "一、主人专用\n1、添加大学习配置|添加大学习用户|add_dxx\n指令格式：添加大学习配置#QQ号#地区#姓名#学校#团委(学院)#团支部(班级)\n2、删除大学习配置|删除大学习用户|del_dxx\n指令格式：删除大学习配置#QQ号\n"
            "3、查看大学习用户列表\n4、查看大学习用户|查看大学习配置|check_dxx_user\n指令格式：查看大学习用户#QQ号\n5、完成大学习|finish_dxx\n指令格式：完成大学习#QQ号\n二、全员可用\n1、提交大学习\n2、我的大学习|查看我的大学习|my_dxx\n3、大学习功能|大学习帮助|dxx_help\n"
            "4、设置大学习配置|set_dxx\n指令格式：设置大学习配置#地区#姓名#学校#团委(学院)#团支部(班级)\n5、查组织|查班级|check_class\n指令格式：查组织#地区简写(例江西为：jx)#学校名称#团委名称\nPs:查组织功能对湖北用户无效！"
        )
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.text(message),
                event=event,
                at_sender=True,
            )
    except Exception as e:
        message = f"出错了\n错误信息:{e}"
        logger.error(f"{datetime.now()}: 错误信息：{e}")
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )


finish_dxx = on_command("完成大学习", aliases={"finish_dxx"}, permission=SUPERUSER)


@finish_dxx.handle()
async def _(event: Event):
    send_id = event.get_user_id()
    finish_id = str(event.get_message()).split("#")[-1]
    try:
        mark = False
        with open(path + "/dxx_list.json", "r", encoding="utf-8") as f:
            obj = json.load(f)
        for item in obj:
            if int(finish_id) == int(item["qq"]):
                if item["area"] == "湖北":
                    code = await start_use_hb(finish_id)
                elif item["area"] == "江西":
                    code = await start_use_jx(finish_id)
                else:
                    code = 0
                mark = True
                if code == 1:
                    content = await get_pic()
                    end = content["end"]
                    area = item["area"]
                    name = item["name"]
                    openid = item["openid"]
                    danwei1 = item["danwei1"]
                    danwei2 = item["danwei2"]
                    danwei3 = item["danwei3"]
                    message = f"大学习提交成功!\n用户信息\n姓名：{name}\nQQ号:{finish_id}\n地区：{area}\nopenid:{openid}\n学校：{danwei1}\n学院：{danwei2}\n团支部(班级)：{danwei3}"
                    if pic_msg:
                        pict = await pic(message)
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.image(pict),
                            at_sender=True,
                            event=event,
                        )
                        await asyncio.sleep(1)
                        c = "你也可以点击链接进行截图以获取带手机状态栏的完成截图\nhttps://qndxx.scubot.live/\n如果QQ不能直接打开请复制到微信打开！"
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.text("完成截图\n")
                            + MessageSegment.image(end)
                            + MessageSegment.text(c),
                            event=event,
                            at_sender=True,
                        )
                    else:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=message,
                            event=event,
                            at_sender=True,
                        )
                        await asyncio.sleep(1)
                        c = "你也可以点击链接进行截图以获取带手机状态栏的完成截图\nhttps://qndxx.scubot.live/\n如果QQ不能直接打开请复制到微信打开！"
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.text("完成截图\n")
                            + MessageSegment.image(end)
                            + MessageSegment.text(c),
                            event=event,
                            at_sender=True,
                        )
                else:
                    message = "提交失败！"
                    if pic_msg:
                        pict = await pic(message)
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=MessageSegment.image(pict),
                            at_sender=True,
                            event=event,
                        )
                    else:
                        await nonebot.get_bot().send(
                            user_id=send_id,
                            message=message,
                            event=event,
                            at_sender=True,
                        )
                break
        if not mark:
            message = "用户数据不存在，请先配置用户文件！"
            if pic_msg:
                pict = await pic(message)
                await nonebot.get_bot().send(
                    user_id=send_id,
                    message=MessageSegment.image(pict),
                    at_sender=True,
                    event=event,
                )
            else:
                await nonebot.get_bot().send(
                    user_id=send_id, message=message, event=event, at_sender=True
                )
    except Exception as e:
        message = f"出错了\n错误信息:{e}"
        logger.error(f"{datetime.now()}: 错误信息：{e}")
        if pic_msg:
            pict = await pic(message)
            await nonebot.get_bot().send(
                user_id=send_id,
                message=MessageSegment.image(pict),
                event=event,
                at_sender=True,
            )
        else:
            await nonebot.get_bot().send(
                user_id=send_id, message=message, event=event, at_sender=True
            )
