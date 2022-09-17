import datetime
from datetime import date
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import random
import json
import time

"""
微信公众号平台  
https://mp.weixin.qq.com/debug/cgi-bin/sandboxinfo?action=showinfo&t=sandbox/index
小接口：
https://www.tianapi.com

"""


Tips = {
    "卵巢周期": {
        "卵泡期": [
            "卵泡期由上次月经停止日开始至卵巢排卵日止，历时10～12天。在这一期中，此期卵泡的粒膜细胞在FSH和LH的作用下产生雌激素，在雌激素的作用下，子宫内膜迅速增殖，血管增生，腺体增宽加长，但不分泌。"],
        "排卵日": [""],
        "黄体期": ["黄体期主要是指女性在排卵期到月经来之前的一个特定阶段，在这段时间内就有可能形成黄体，"
                   "同时会形成生理性的体温增高。排卵之后，卵子和卵泡液流出，卵泡腔下降、塌陷，与周围的结缔组织包绕，从而形成黄体。"
                   "黄体能够分泌雌孕激素，如果患者没有怀孕，雌孕激素会迅速的下降，在维持14天左右体温也会下降，同时来月经。如果怀孕之后，"
                   "黄体则继续起到分泌功能，能够分泌雌孕激素，促进并支持胚胎的发育。如果患者出现黄体功能不全，患者则会出现胚胎停止发育，甚至习惯性流产。"]
    },
    "子宫周期": {
        "经期": [""],
        "增长期": [""],
        "排卵日": [""],
        "分泌期": ["分泌期,也称为黄体期,是月经周期的一个阶段,指从排卵后到下一次来月经前这段时间。月经周期分为三个阶段:"
                   "卵泡期、黄体期、排卵期。首先卵泡发育阶段被称为卵泡增生,"
                   "而卵泡破裂的时期被称为排卵期,排卵后至下一次来月经前称为黄体期,这段时间的子宫内膜会发生分泌期的变化,因此也称为分泌期"]
    },
    "俗称": {
        "经期": ["在饮食方面，月经期间要避免进食辛辣、凉、冷、硬的食物,要注意下腹部的保暖"
                 "因为寒冷有可能会导致痛经的发生,月经期间可以进行温和的运动，例如散步、快走等，但是要避免剧烈的运动"
                 "月经期间一定要注意外阴的清洁，要每天清洗外阴，使用棉质透气的卫生巾，并且要及时更换卫生巾"],
        "安全期（排卵前安全期)": ["安全期避孕并非绝对安全，只是受孕机率小些。 安全期避孕并非绝对安全，只是受孕机率小些"
                                 "如果是在月经刚干净的三天内，一般这个时间段同房是不会怀孕的，也可以不带避孕套"],
        "排卵前期（排卵期，危险期）": ["在排卵期的时候白带会明显的增多，在这个时候一定要注意好个人的卫生，建议勤换内裤"
                                    "适当的用温盐水清洗一下外阴，同时在排卵期的时候，由于受孕概率比较高，这个时候也称之为危险期"],
        "排卵日": ["今天是排卵日哦"],
        "排卵后期（排卵期，危险期）": [
            "女性在排卵的时候可能会出现一个排卵期的出血，这种属于生理现象，不需要去过度的治疗，但是如果经常性地出现排卵期出血，那么可能是存在黄体功能不足，建议尽早的抽血查一下性激素水平"],
        "安全期（排卵后安全期）": ["女性在排卵日后五天一般就是到了安全期，因为在女性在排卵日的时候排卵比较多见，并且卵子排出后，它的存活期是48小时内，所以在排卵之后的五天，"
                                 "此时即便是有卵子已经排出，也已经死亡，在此期间进行同房，精子和卵子就不能够结合发育成受精卵，一般就不会导致女性怀孕。少数的情况下，"
                                 "若女性由于精神压力大劳累或者是等其他因素影响，导致排卵日检测的不准确，出现排卵日后延，卵子排出后仍在存活期，即排卵日后五天卵子在存活期，"
                                 "发生性生活后也有导致意外怀孕的，因此安全期和危险期只是个相对的日期，并不是绝对的准确。如果女性无怀孕欲望，最好全程戴避孕套，以免意外情况的发生。"]
    }
}


def diff_time(start, end):
    start = time.strptime(start, "%Y-%m-%d")
    end = time.strptime(end, "%Y-%m-%d")
    userStart = datetime.datetime(start[0], start[1], start[2])
    userEnd = datetime.datetime(end[0], end[1], end[2])
    return (userEnd - userStart).days


def menstrual_dict(period_per_classes):
    temp = 0
    temp_ls = []
    for value in period_per_classes:
        temp += value
        temp_ls.append(temp)

    name_dict = {
        "卵巢周期": {
            "卵泡期": [0, temp_ls[2]],
            "排卵日": [temp_ls[3], temp_ls[3]],
            "黄体期": [temp_ls[3] + 1, temp_ls[-1]]
        },
        "子宫周期": {
            "经期": [0, temp_ls[0]],
            "增长期": [temp_ls[0] + 1, temp_ls[2]],
            "排卵日": [temp_ls[3], temp_ls[3]],
            "分泌期": [temp_ls[3] + 1, temp_ls[-1]]
        },
        "俗称": {
            "经期": [0, temp_ls[0]],
            "安全期（排卵前安全期)": [temp_ls[0] + 1, temp_ls[1]],
            "排卵前期（排卵期，危险期）": [temp_ls[1] + 1, temp_ls[2]],
            "排卵日": [temp_ls[3], temp_ls[3]],
            "排卵后期（排卵期，危险期）": [temp_ls[3] + 1, temp_ls[4]],
            "安全期（排卵后安全期）": [temp_ls[4], temp_ls[-1]]
        }
    }
    return name_dict


class Menses:

    def __init__(self):
        self.menses_period = [
            ("2022-5-30", "2022-6-5"),
            ("2022-6-27", "2022-7-8"),
            ("2022-7-30", "2022-8-5"),
            ("2022-9-2", "2022-9-8"),
        ]
        # 经期,安全期（排卵前安全期),排卵前期（排卵期，危险期）,排卵日,排卵后期（排卵期，危险期）,安全期（排卵后安全期）
        self.menstrual_classes_period = [4, 4, 5, 1, 4, 10]

        menstrual_cycle = []
        pre_value = 0
        for value in self.menses_period:
            if pre_value != 0:
                menstrual_cycle.append(diff_time(pre_value[1], value[0]))
            pre_value = value

        self.out_message = self.own_sheet()
        self.ovulation_period_start = min(menstrual_cycle) - 18
        self.ovulation_period_end = max(menstrual_cycle) - 11

    def own_sheet(self):
        sheet = menstrual_dict(self.menstrual_classes_period)
        time_now = f"{time.gmtime()[0]}-{time.gmtime()[1]}-{time.gmtime()[2]}"
        last_menstrual_time = self.menses_period[-1][1]
        key_point = diff_time(last_menstrual_time, time_now)
        message = []
        for name in sheet.keys():
            for key, value in sheet[name].items():
                if key_point in range(value[0], value[1]):
                    message.append(key)
        message = list(set(message))
        tips_message = []
        for key, v in Tips.items():
            for key, value in v.items():
                if key in message:
                    tips_message.append(value)
        out_message = "今天是悠然的"
        for key in message:
            if key == message[-1]:
                out_message += key
            else:
                out_message += key + ","
        out_message += "哦,以下是一些Tips："

        for key in tips_message:
            if key == message[-1]:
                out_message += str(key)
            else:
                out_message += str(key) + ","

        return out_message

    def __call__(self, *args, **kwargs):
        return self.out_message


# -*- coding: utf-8 -*-
def song_word(key):
    url = f"http://api.tianapi.com/zmsc/index?key={key}"
    ret = requests.get(url)
    ret = ret.content.decode('utf8').replace("'", '"')
    data_json = json.loads(ret)
    message = f"今日宋词：{data_json['newslist'][0]['content']}" + '\n' + f"出自：{data_json['newslist'][0]['source']}"
    print(message)
    return message


def star(key, star_name):
    url = f"http://api.tianapi.com/star/index?key={key}&astro={star_name}"
    ret = requests.get(url)
    ret = ret.content.decode('utf8').replace("'", '"')
    data_json = json.loads(ret)
    message = f"星座名称：{star_name}，"
    for i, news in enumerate(data_json['newslist'][:-1]):
        if i % 3 == 0:
            message += f"{news['type']}: {news['content']}, " + '\n'
        else:
            message += f"{news['type']}: {news['content']}, "
    last_message = f"{data_json['newslist'][-1]['type']}：{data_json['newslist'][-1]['content']}"
    return message, last_message


def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


class WeMessage:
    def __init__(self, temp_id, tianapi_key):
        self.tianapi_key = tianapi_key
        self.user0 = {
            'START_DATE': '2022-05-21',
            'CITY': '苏州',
            'BIRTHDAY': '11-8',
        }
        self.user1 = {
            'START_DATE': '2022-05-21',
            'CITY': '广州',
            'BIRTHDAY': '05-19',
        }

        self.client_info = {
            "APP_ID": 'wxaef11d8319d01eca',
            "APP_SECRET": 'ef79f1e3ea77907101deb7c60fa1502a',
            "USER_ID": ['omr1N5l9KdGm7LtNGPfrJET3qrGs', 'omr1N5sLmhG-9KNuZ0At5SgWK9aw'],
            "TEMPLATE_ID": temp_id
        }
        # , 'omr1N5sLmhG-9KNuZ0At5SgWK9aw'

        self._init_user_info()
        self.start()

    def _init_user_info(self):
        self.today = datetime.datetime.now()
        self.start_date = self.user0['START_DATE']

        self.city0 = self.user0['CITY']
        self.city1 = self.user1['CITY']
        self.birthday0 = self.user0['BIRTHDAY']
        self.birthday1 = self.user1['BIRTHDAY']

    def get_count(self):
        delta = self.today - datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
        return delta.days

    def get_birthday(self, birthday):
        next = datetime.datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
        if next < datetime.datetime.now():
            next = next.replace(year=next.year + 1)
        return (next - self.today).days

    def get_weather(self, city):
        url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
        res = requests.get(url).json()
        weather = res['data']['list'][0]
        weather_message = f"{weather['city']}, 天气：{weather['weather']}，" + f"温度：{math.floor(weather['temp'])}，" + f"湿度：{weather['humidity']}，" + f"风力等级：{weather['wind']}"
        return weather_message

    def start(self):
        client = WeChatClient(self.client_info['APP_ID'], self.client_info['APP_SECRET'])
        wm = WeChatMessage(client)
        weather_message0 = self.get_weather(self.user0['CITY'])
        weather_message1 = self.get_weather(self.user1['CITY'])
        star_message0, last_message0 = star(self.tianapi_key, "天蝎座")
        star_message1, last_message1 = star(self.tianapi_key, "金牛座")

        data0 = {
            "date_date": {"value": str(self.today), "color": get_random_color()},
            "weather_message0": {"value": weather_message0, "color": get_random_color()},
            "weather_message1": {"value": weather_message1},
            "love_days": {"value": self.get_count(), "color": "#%06x" % 0xFA8072},
            "birthday_left": {"value": self.get_birthday(self.user0['BIRTHDAY']), "color": "#%06x" % 0xFA8072},
            "words": {"value": get_words(), "color": get_random_color()},
            "song_words": {"value": song_word(self.tianapi_key), "color": get_random_color()},
        }
        star_0 = [{"star": {"value": star_message0, "color": "#%06x" % 0x8E236B}},
                  {"star": {"value": last_message0, "color": "#%06x" % 0x8E236B}}]
        star_1 = [{"star": {"value": star_message1, "color": "#%06x" % 0x8E236B}},
                  {"star": {"value": last_message1, "color": "#%06x" % 0x8E236B}}]

        for i in range(len(self.client_info['USER_ID'])):
            res = wm.send_template(self.client_info['USER_ID'][i], self.client_info['TEMPLATE_ID'], data0)
            if random.randint(0, 100) < 30:
                for value in [star_0, star_1]:
                    for key_message in value:
                        res = wm.send_template(self.client_info['USER_ID'][i],
                                               "vxbFxhPLsjnsZYqPgXHrsdZbAfJictedz-jEzE7yWLc",
                                               key_message)

        menses_message = Menses().out_message
        menses_message = {"menses": {"value": menses_message}}
        if random.randint(0, 100) < 30:
            for i in range(len(self.client_info['USER_ID'])):
                wm.send_template(self.client_info['USER_ID'][i], "2rTC0o4BDZHgH4DdUNIayGB8WF2NIs6OsdjM-ds9c9U",
                                 menses_message)

        print("process have down")


if __name__ == "__main__":
    tianapi_key = '54601312395bae03a51ec6d7fe2d8ee6'
    temp_id = "XmIP9fiQ1ML8mhcYXl-0Dkz_1tpfMvP7PMFNSlw8Vpo"
    WeMessage(temp_id, tianapi_key)

"""
目前时间是：{{date_date.DATA}}
今天是我们的第：{{love_days.DATA}}天 
距离她的生日：{{birthday_left.DATA}}天 
她所在的城市：{{weather_message0.DATA}}
他所在的城市：{{weather_message1.DATA}}
今日想对然然说的话：{{words.DATA}}
今日宋词推荐：{{song_words.DATA}}
"""

"""
{{star.DATA}} 
"""
"""
{{menses.DATA}}
"""
