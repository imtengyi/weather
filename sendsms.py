#-*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
import config
import utils

from sqlhelper import SqlHelper
from aliyunsms import AliyunSms


class SendSms(object):
    def __init__(self):
        self.sql = SqlHelper()

        self.weather_table_name = config.weather_table
        self.user_table_name = config.user_table

    def send_sms(self):
        command = ("SELECT * FROM {};".format(self.user_table_name))
        self.sql.execute(command)
        users = self.sql.cursor.fetchall()
        if users != None:
            for user in users:
                utils.log('send_sms get user info user:%s' % str(user))
                # 判断用户定义的时间，只有满足用户定义时间才发送短信
                user_time = user[5]
                time_info = user_time.split(':')

                u_hour = time_info[0]
                u_minute = time_info[1]

                # 获取系统时间
                s_hour = datetime.datetime.now().hour
                s_minute = datetime.datetime.now().minute

                if int(u_hour) == s_hour and int(u_minute) == s_minute:
                    utils.log('send sms to user:%s' % str(user))

                    command = ("select * from {0} where city_name='{1}' order by id desc limit 1;"
                               .format(self.weather_table_name, user[3]))
                    self.sql.execute(command)
                    weather = self.sql.cursor.fetchone()
                    if weather != None:
                        temp_code = 'SMS_41855112'
                        phone = user[2]
                        info = {
                            'name': user[1],
                            'city': user[3],
                            'weather': weather[15],
                            'temp': '%s ~ %s' % (weather[9], weather[8]),
                            'aqilevel': utils.get_aqi_level_info(weather[12]),
                        }

                        sms = AliyunSms()
                        sms.send_sms(temp_code, info, phone)


if __name__ == '__main__':
    os.chdir(sys.path[0])

    reload(sys)
    sys.setdefaultencoding('utf8')

    try:
        logging.basicConfig(
                filename = 'log/sms.log',
                format = '%(levelname)s %(asctime)s: %(message)s',
                level = logging.DEBUG
        )

        sms = SendSms()
        sms.send_sms()

    except Exception, e:
        utils.log('sms weather msg:%s' % str(e))
