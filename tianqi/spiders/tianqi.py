#-*- coding: utf-8 -*-

import json
import time
import datetime
import sys
import config
import utils

from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.spiders import Spider
from scrapy.http import Request
from sqlhelper import SqlHelper
from cityids import cityids

reload(sys)
sys.setdefaultencoding('utf-8')

class TianqiSpider(Spider):
    name = 'tianqi'

    def __init__(self, *a, **kw):
        super(TianqiSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

        self.sql = SqlHelper()
        self.weather_table_name = config.weather_table
        self.citys = []

        self.init()

    def init(self):
        command = ("CREATE TABLE IF NOT EXISTS {} ("
                   "`id` INT(8) NOT NULL AUTO_INCREMENT,"
                   "`unique_id` CHAR(25) NOT NULL UNIQUE,"
                   "`city_id` INT(9) NOT NULL,"
                   "`city_name` TEXT NOT NULL,"
                   "`date` DATE NOT NULL,"
                   "`time` TEXT NOT NULL,"
                   "`week` TEXT NOT NULL,"
                   "`cur_temperature` TEXT NOT NULL,"
                   "`max_temperature` TEXT NOT NULL,"
                   "`min_temperature` TEXT NOT NULL,"
                   "`overall` TEXT NOT NULL,"
                   "`humidity` TEXT NOT NULL,"
                   "`aqi` INT(3) DEFAULT NULL,"
                   "`aqi_pm25` INT(3) DEFAULT NULL,"
                   "`aqi_level` TEXT NOT NULL,"
                   "`weather` TEXT NOT NULL,"
                   "`wind_direction` TEXT DEFAULT NULL,"
                   "`wind_force` TEXT DEFAULT NULL,"
                   "`wind_speed` TEXT DEFAULT NULL,"
                   "`warning_level` TEXT DEFAULT NULL,"
                   "`warning_date` TEXT DEFAULT NULL,"
                   "`warning_info` TEXT DEFAULT NULL,"
                   "`remarks` TEXT DEFAULT NULL,"
                   "`other` TEXT DEFAULT NULL,"
                   "`save_data_time` TIMESTAMP NOT NULL,"
                   "`mini_weather` TEXT DEFAULT NULL,"
                   "`sk_2d_weather` TEXT DEFAULT NULL,"
                   "`dingzhi_weather` TEXT DEFAULT NULL,"
                   "PRIMARY KEY(id)"
                   ") ENGINE=InnoDB".format(self.weather_table_name))

        self.sql.create_table(command)

    def start_requests(self):
        for cityid, cityname in cityids.items():
            url = 'http://wthrcdn.etouch.cn/weather_mini?citykey=%s' % cityid

            yield Request(
                    url = url,
                    method = 'GET',
                    headers = {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Connection': 'keep-alive',
                        'Host': 'wthrcdn.etouch.cn',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:50.0) Gecko/20100101 '
                                      'Firefox/50.0',
                    },
                    meta = {
                        'cityid': cityid,
                        'cityname': cityname,
                    },
                    callback = self.get_sk_2d_weather,
            )

    def get_sk_2d_weather(self, response):
        cityid = response.meta.get('cityid')
        cityname = response.meta.get('cityname')
        mini_weather = response.body

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Host': 'd1.weather.com.cn',
            'Referer': 'http://www.weather.com.cn/weather1d/%s.shtml' % cityid,
        }

        url = 'http://d1.weather.com.cn/sk_2d/%s.html?_=%s' % (cityid, time.time() * 1000)
        yield Request(
                url = url,
                method = 'GET',
                headers = headers,
                meta = {
                    'cityid': cityid,
                    'cityname': cityname,
                    'mini_weather': mini_weather,
                },
                callback = self.get_dingzhi_weather,
        )

    def get_dingzhi_weather(self, response):
        cityid = response.meta.get('cityid')
        cityname = response.meta.get('cityname')
        mini_weather = response.meta.get('mini_weather')
        sk_2d_weather = response.body

        url = 'http://d1.weather.com.cn/dingzhi/%s.html?_=%s' % (cityid, time.time() * 1000)
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Host': 'd1.weather.com.cn',
            'Referer': 'http://www.weather.com.cn/alarm/newalarmcontent.shtml?file=10101-20170105084500-1303.html',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:50.0) Gecko/20100101Firefox/50.0',
        }
        yield Request(
                url = url,
                headers = headers,
                meta = {
                    'cityid': cityid,
                    'cityname': cityname,
                    'mini_weather': mini_weather,
                    'sk_2d_weather': sk_2d_weather,
                },
                callback = self.get_weather
        )

    def get_weather(self, response):
        mini_weather = response.meta.get('mini_weather')
        sk_2d_weather = response.meta.get('sk_2d_weather')
        dingzhi_weather = response.body

        cityid = response.meta.get('cityid')
        cityname = response.meta.get('cityname')

        response.meta['dingzhi_weather'] = dingzhi_weather

        self.log('get_weather \ncityid:%s\n cityname:%s\n\n mini_weather:\n%s\n sk_2d_weather:\n%s\n '
                 'dingzhi_weather:\n%s\n'
                 % (cityid, cityname, mini_weather, sk_2d_weather, dingzhi_weather))

        return self.insert_to_sql(response)

    def insert_to_sql(self, response):
        mini_weather = response.meta.get('mini_weather')
        sk_2d_weather = response.meta.get('sk_2d_weather')
        dingzhi_weather = response.meta.get('dingzhi_weather')

        city_id = response.meta.get('cityid')
        city_name = response.meta.get('cityname')

        date = utils.get_date()
        week = utils.get_week()

        mini = json.loads(mini_weather)
        data = mini.get('data')

        overall = data.get('ganmao')
        forecast = data.get('forecast')
        forecast_first = forecast[0]
        max_temperature = forecast_first.get('high').split(' ')[1]
        min_temperature = forecast_first.get('low').split(' ')[1]

        sk_2d = sk_2d_weather.split('=')
        sk_2d_info = json.loads(sk_2d[1])
        humidity = sk_2d_info.get('SD')
        cur_temperature = sk_2d_info.get('temp')
        cur_temperature = cur_temperature + '℃'
        aqi = sk_2d_info.get('aqi')
        aqi_pm25 = sk_2d_info.get('aqi_pm25')
        aqi_level = utils.get_aqi_level(aqi)
        weather = sk_2d_info.get('weather', '')
        wind_direction = sk_2d_info.get('WD', '')
        wind_force = sk_2d_info.get('WS', '')
        wind_speed = sk_2d_info.get('wse', '')
        wind_speed = wind_speed.replace('&lt;', '')
        data_time = sk_2d_info.get('time')

        dingzhi = dingzhi_weather.split(';')
        warning_level = ''
        warning_date = ''
        warning_info = ''

        alarm = json.loads(dingzhi[1].split('=')[1])
        alarm_w = alarm.get('w', '')
        if len(alarm_w) > 0:
            alarm_m_info = alarm_w[0]
            warning_level = alarm_m_info.get('w7', '')
            warning_date = alarm_m_info.get('w8', '')
            warning_info = alarm_m_info.get('w9', '')

        remarks = ''
        other = ''

        unique_id = city_id + date + data_time

        command = ("INSERT IGNORE INTO {} "
                   "(id, unique_id, city_id, city_name, date, time, week, cur_temperature, max_temperature, "
                   "min_temperature, "
                   "overall, humidity, aqi, aqi_pm25, aqi_level, weather, wind_direction, wind_force, wind_speed, "
                   "warning_level, warning_date, warning_info, remarks, other, save_data_time, mini_weather, "
                   "sk_2d_weather, dingzhi_weather)"
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                   "%s, "
                   "%s, %s, %s, %s, %s)".format(self.weather_table_name))

        msg = (
            None, unique_id, city_id, city_name, date, data_time, week, cur_temperature, max_temperature,
            min_temperature, overall,
            humidity,
            aqi, aqi_pm25, aqi_level, weather, wind_direction, wind_force, wind_speed, warning_level, warning_date,
            warning_info, remarks, other, None, mini_weather, sk_2d_weather, dingzhi_weather)

        self.sql.insert_data(command, msg)

    def close(spider, reason):
        print('close name:%s reason:%s' % (spider.name, reason))

    def spider_closed(self, spider):
        self.log('spider_closed 抓取信息完成，发送天气预报短信')
