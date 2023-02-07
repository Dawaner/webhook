import pathlib
import sys
import requests
import json
import schedule
import time

webhook = ""
uid = ""
text = []
send_time = []
status = []
bv_id = ""
zl_id = ""
title = ""
data = {}
follower = ""


def print_text(str_):
    print()
    print("------------------------------------")
    print(str_)
    print("------------------------------------")
    print()


def default_config():
    default = """webhook地址:
www.xxx.com

要爬取的b站用户的uid:
589183005

要爬取的视频BV号(选填):


要爬取的专栏cv号(选填):


标题名称:
**哔哩哔哩账号数据**

文本内容:
开始{
当前粉丝数量:[粉丝数]
视频播放量:[视频播放量]
[视频action([视频标题])]
[专栏action([专栏标题])]
}结束

定时发送(以,为间隔):
10:00,12:00,16:00,18:00

文本内容格式：
>可获取内容：(粉丝数，视频标题，视频播放量，视频点赞数，视频投币数，视频收藏数，视频转发数，
专栏标题，专栏浏览量，专栏点赞数，专栏投币数，专栏收藏数，专栏转发数)
>获取内容加上[]即可，例如[粉丝数]
>链接按钮可选:[视频action(自订文字内容)]，[专栏action(自订文字内容)]
>文字内容格式lark_md(markdown格式)
"""
    path = pathlib.Path("config.txt")
    if not path.is_file():
        with open("config.txt", "w", encoding='UTF-8', errors='ignore') as f:
            f.write(default)
        print("config.txt初始化")
    path = pathlib.Path("config_backup.txt")
    if not path.is_file():
        with open("config_backup.txt", "w", encoding='UTF-8', errors='ignore') as f:
            f.write(default)
        print("config_backup.txt初始化")


def config_backup():
    with open("config.txt", "r", encoding='UTF-8', errors='ignore') as f:
        config = f.read()
    f.close()
    with open("config_backup.txt", "w", encoding='UTF-8', errors='ignore') as f:
        f.write(config)


def is_number(number):
    if "0" <= number <= "9":
        return True
    else:
        return False


def read_config():
    global webhook, uid, bv_id, zl_id, text, send_time, title
    txt = []

    with open("config.txt", "r", encoding='UTF-8', errors='ignore') as f:
        for line in f.readlines():
            line = line.strip('\n')
            txt.append(line)
    f.close()
    for i in range(len(txt)):
        if txt[i] == "webhook地址:":
            webhook = txt[i + 1]
        elif txt[i] == "要爬取的b站用户的uid:":
            uid = txt[i + 1]
        elif txt[i] == "要爬取的视频BV号(选填):":
            bv_id = txt[i + 1]
        elif txt[i] == "要爬取的专栏cv号(选填):":
            zl_id = txt[i + 1]
        elif txt[i] == "标题名称:":
            title = txt[i + 1]
        elif txt[i] == "定时发送(以,为间隔):":
            send_time = txt[i + 1].split(',')
            break

    if webhook == "" or uid == "" or text == "" or send_time == [] or title == "":
        print_text("数据为空，或者破坏了文件格式")
        sys.exit()
    for u in uid:
        if not is_number(u):
            print_text("uid应为纯数字")
            sys.exit()
    for st in send_time:
        if len(st) != 5:
            print_text("时间格式错误")
            sys.exit()
        elif st[2] != ":":
            print_text("时间格式错误")
            sys.exit()
        else:
            for sti in range(5):
                if sti == 2:
                    sti = sti + 1
                    continue
                if not is_number(st[sti]):
                    print_text("时间格式错误")
                    sys.exit()

    with open("config.txt", "r", encoding='UTF-8', errors='ignore') as f:
        txt_text = f.read()
    f.close()
    txt_text = txt_text.split("开始{\n")[1]
    txt_text = txt_text.split("}结束")[0]
    txt_text = text_handle(txt_text)
    text = txt_text.splitlines()


def get_info():
    global follower
    url1 = "https://api.bilibili.com/x/relation/stat?vmid=" + uid + "&jsonp=jsonp"
    info1 = requests.get(url1)
    data1 = info1.json()
    follower = data1['data']['follower']

    if not bv_id == "":
        url2 = "https://api.bilibili.com/x/player/pagelist?bvid=" + bv_id
        cid = requests.get(url2).json()['data'][0]['cid']
        url2_1 = "https://api.bilibili.com/x/web-interface/view?cid=" + str(cid) + "&bvid=" + str(bv_id)
        data2 = requests.get(url2_1).json()

    if not zl_id == "":
        url3_id = zl_id.split("cv")[1]
        url3 = "https://api.bilibili.com/x/article/viewinfo?id=" + url3_id + "&mobi_app=pc&from=web"
        data3 = requests.get(url3).json()

    return data2, data3


def text_handle(text_str):
    data2 = get_info()[0]
    data3 = get_info()[1]
    text_str = text_str.replace("[粉丝数]", str(follower))

    text_str = text_str.replace("[视频标题]", str(data2['data']['title']))
    text_str = text_str.replace("[视频播放量]", str(data2['data']['stat']['view']))
    text_str = text_str.replace("[视频点赞数]", str(data2['data']['stat']['like']))
    text_str = text_str.replace("[视频投币数]", str(data2['data']['stat']['coin']))
    text_str = text_str.replace("[视频收藏数]", str(data2['data']['stat']['favorite']))
    text_str = text_str.replace("[视频转发数]", str(data2['data']['stat']['share']))

    text_str = text_str.replace("[专栏标题]", str(data3['data']['title']))
    text_str = text_str.replace("[专栏浏览量]", str(data3['data']['stats']['view']))
    text_str = text_str.replace("[专栏点赞数]", str(data3['data']['stats']['like']))
    text_str = text_str.replace("[专栏投币数]", str(data3['data']['stats']['coin']))
    text_str = text_str.replace("[专栏收藏数]", str(data3['data']['stats']['favorite']))
    text_str = text_str.replace("[专栏转发数]", str(data3['data']['stats']['share']))
    return text_str


def add_action(ac_text, ac_url):
    action = {
        "actions": [{
            "tag": "button",
            "text": {
                "content": ac_text,
                "tag": "lark_md"
            },
            "url": ac_url,
            "type": "primary",
            "value": {}
        }],
        "tag": "action"
    }
    return action


def add_text(a_text):
    ls_text = {
        "tag": "div",
        "text": {
            "content": a_text,
            "tag": "lark_md"
        }
    }
    return ls_text


def make_data():
    global data
    data = {
        "msg_type": "interactive",
        "card": {
            "elements": [],
            "header": {
                "title": {
                    "content": title,
                    "tag": "plain_text"
                }
            }
        }
    }
    for i in text:
        if i.startswith("[视频action("):
            get_action_title = i.split("[视频action(")[1]
            get_action_title = get_action_title.split(")]")[0]
            action_url = "https://www.bilibili.com/video/" + bv_id
            data["card"]["elements"].append(add_action(get_action_title, action_url))
        elif i.startswith("[专栏action("):
            get_action_title = i.split("[专栏action(")[1]
            get_action_title = get_action_title.split(")]")[0]
            action_url = "https://www.bilibili.com/read/" + zl_id
            data["card"]["elements"].append(add_action(get_action_title, action_url))
        else:
            data["card"]["elements"].append(add_text(i))


def post():
    read_config()
    make_data()
    headers = {'Content-Type': 'application/json'}
    requests.post(url=webhook, headers=headers, data=json.dumps(data))
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(now_time + " 发送成功")


def main():
    print("------------------------------------")
    print("请勿修改config_backup.txt文件!")
    print("修改配置请到config.txt文件中修改")
    default_config()
    read_config()
    make_data()
    config_backup()
    print("启动成功,配置文件成功备份")
    print("------------------------------------")
    for s_time in send_time:
        schedule.every().day.at(s_time).do(post)
    while True:
        schedule.run_pending()  # 运行所有可以运行的任务
        time.sleep(1)


if __name__ == '__main__':
    main()
