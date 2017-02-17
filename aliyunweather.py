#-*- coding: utf-8 -*-

import json
import requests
import utils


class AliyunWeather(object):
    def __init__(self):
        self.init()

    def init(self):
        host = 'https://ali-weather.showapi.com'
        path = '/area-to-id'
        appcode = '4708657f90444c3dbe6775677ab7c37b'
        querys = 'area=北京'
        url = host + path + '?' + querys
        utils.log('请求的 url:%s' % url)

        headers = {
            'Authorization': 'APPCODE ' + appcode,
        }
        r = requests.get(url = url, headers = headers)

        utils.log('请求到的天气数据是:\n%s' % json.dumps(json.loads(r.text), indent = 4))
        return r.text


if __name__ == '__main__':
    weather = AliyunWeather()
