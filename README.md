<div align="center">
    <img src="https://s4.ax1x.com/2022/03/05/bw2k9A.png" alt="bw2k9A.png" border="0"/>
    <h1>nonebot_plugin_youthstudy</h1>
    <b>基于nonebot2的青年大学习自动提交插件，用于自动完成大学习，在后台留下记录，返回完成截图</b>
    <br/>
    <a href="https://github.com/ZMXC01/nonebot_plugin_botteenstudy/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/ayanamiblhx/nonebot_plugin_youthstudy?style=flat-square"></a>
    <a href="https://github.com/ZMXC01/nonebot_plugin_botteenstudy/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/ZMXC01/nonebot_plugin_botteenstudy?style=flat-square"></a>
    <a href="https://github.com/ZMXC01/nonebot_plugin_botteenstudy/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/ZMXC01/nonebot_plugin_botteenstudy?style=flat-square"></a>
    <a href="https://github.com/ZMXC01/nonebot_plugin_botteenstudy/blob/main/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/ZMXC01/nonebot_plugin_botteenstudy?style=flat-square"></a>
</div>


## 各地区使用方式

- [江西地区](./nonebot_plugin_botteenstudy/resource/江西地区.md)
- [湖北地区](./nonebot_plugin_botteenstudy/resource/湖北地区.md)

## 参考

- [江西共青团自动提交](https://github.com/XYZliang/JiangxiYouthStudyMaker)

- [青春湖北自动提交](https://github.com/Samueli924/TeenStudy)

- [28位openid随机生成和抓包](https://hellomango.gitee.io/mangoblog/2021/09/26/other/%E9%9D%92%E5%B9%B4%E5%A4%A7%E5%AD%A6%E4%B9%A0%E6%8A%93%E5%8C%85/)

##  安装及更新

1. 使用`git clone https://github.com/ZMXC01/nonebot_plugin_botteenstudy.git`指令克隆本仓库或下载压缩包文件
2. 使用`pip install nonebot_plugin_bottenstudy`来进行安装,使用`pip install nonebot_plugin_botteenstudy -U`进行更新

## 导入插件
**使用第一种安装方式**

- 将`nonebot_plugin_botteenstudy`放在nb的`plugins`目录下，运行nb机器人即可

**使用第二种安装方式**
- 在`bot.py`中添加`nonebot.load_plugin("nonebot_plugin_botteenstudy")`或在`pyproject.toml`里的`[tool.nonebot]`中添加`plugins = ["nonebot_plugin_botteenstudy"]`


## 机器人配置

- 在nonebot的.env配置文件中设置好超管账号

  ```py
  SUPERUSERS=[""]
  ```

- 文件作用解释

  ```py
  bot_start.py #获取机器人好友和群列表功能
  crawlid.py #抓取江西省高校所有团支部数据存入mongo db数据库
  dxx_hb.py #湖北地区大学习提交主体文件
  dxx_jx.py #江西地区大学习提交主体文件
  get_src.py #获取青年大学习完成截图文件
  msg_pic.py#将文字转为图片文件，方便查看长文本消息
  ```

  

- 请确保已安装以下第三方库（插件运行失败请检查第三方库有没有装完整）

  ```py
  asyncio 
  anti_useragent 
  secrets
  requests
  string
  bs4
  PIL
  pymongo
  httpx
  ```

  

## 功能列表

### 基础功能

```py
主人专用
1、开启(关闭)图片回复|图片回复开(关)
2、加载bot数据|bot开机|机器人开机
3、查看好友列表|查看bot好友列表|查看机器人好友列表
4、查看bot群列表|查看机器人群列表
5、同意(拒绝)添加好友#QQ号
6、查看好友申请列表
7、删除好友#QQ号
8、发消息(send)#QQ号#内容
9、群发消息(send_all)#内容
10、私聊转发开(关)|消息转发开(关)
全员可用
1、机器人状态
2、帮助、help
3、大学习帮助、大学习功能、dxx_help
```
### 大学习

```py
一、主人专用
1、添加大学习配置|添加大学习用户|add_dxx
指令格式：添加大学习配置#QQ号#地区#姓名#学校#团委(学院)#团支部(班级)
2、删除大学习配置|删除大学习用户|del_dxx
指令格式：删除大学习配置#QQ号
3、查看大学习用户列表
4、查看大学习用户|查看大学习配置|check_dxx_user
指令格式：查看大学习用户#QQ号
5、完成大学习|finish_dxx
指令格式：完成大学习#QQ号
二、全员可用
1、提交大学习
2、我的大学习|查看我的大学习|my_dxx
3、大学习功能|大学习帮助|dxx_help
4、设置大学习配置|set_dxx
指令格式：设置大学习#地区#姓名#学校#团委(学院)#团支部(班级)
5、查组织|查班级|check_class
指令格式：查组织#地区简写(例江西为：jx)#学校名称#团委名称
Ps:查组织功能对湖北用户无效！
```

## To Do

- [ ] 增加更多地区支持
- [ ] 优化 Bot
- [ ] 能力有限，将逐步使用异步请求替代使用requests同步请求
- [ ] ~~逐步升级成群管插件~~



## 更新日志

### 2022/05/28

- 将代码上传至pypi，可使用`pip install nonebot_plugin_bottenstudy`指令安装本插件
- 增加已支持地区使用提示
###  2022/05/25
- 上传基础代码
- 支持江西和湖北地区自动完成大学习（可在后台留记录）返回完成截图
