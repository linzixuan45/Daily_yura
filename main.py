from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import random
import json

"""
微信公众号平台  
https://mp.weixin.qq.com/debug/cgi-bin/sandboxinfo?action=showinfo&t=sandbox/index
小接口：
https://www.tianapi.com

"""


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
        self.today = datetime.now()
        self.start_date = self.user0['START_DATE']

        self.city0 = self.user0['CITY']
        self.city1 = self.user1['CITY']
        self.birthday0 = self.user0['BIRTHDAY']
        self.birthday1 = self.user1['BIRTHDAY']

    def get_count(self):
        delta = self.today - datetime.strptime(self.start_date, "%Y-%m-%d")
        return delta.days

    def get_birthday(self, birthday):
        next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
        if next < datetime.now():
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
            "song_words":{"value": song_word(self.tianapi_key), "color": get_random_color()},
        }
        star_0 = [{"star": {"value": star_message0, "color": "#%06x" % 0x8E236B}},
                  {"star": {"value": last_message0, "color": "#%06x" % 0x8E236B}}]
        star_1 = [{"star": {"value": star_message1, "color": "#%06x" % 0x8E236B}},
                  {"star": {"value": last_message1, "color": "#%06x" % 0x8E236B}}]

        for i in range(len(self.client_info['USER_ID'])):
            res = wm.send_template(self.client_info['USER_ID'][i], self.client_info['TEMPLATE_ID'], data0)

            for value in[star_0, star_1]:
                for key_message in value:
                    res = wm.send_template(self.client_info['USER_ID'][i], "vxbFxhPLsjnsZYqPgXHrsdZbAfJictedz-jEzE7yWLc",
                                       key_message)


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
