#-*- coding: utf-8 -*-

import logging
import traceback
import datetime
import platform

from bs4 import CData
from bs4 import NavigableString


def log(msg, level = logging.DEBUG):
    logging.log(level, msg)
    print('%s [level:%s] msg:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), level, msg))

    if level == logging.WARNING or level == logging.ERROR:
        for line in traceback.format_stack():
            print(line.strip())

        for line in traceback.format_stack():
            logging.log(level, line.strip())


def get_first_text(soup, strip = False, types = (NavigableString, CData)):
    data = None
    for s in soup._all_strings(strip, types = types):
        data = s
        break
    return data


def get_texts(soup, strip = False, types = (NavigableString, CData)):
    texts = []
    for s in soup._all_strings(strip, types = types):
        texts.append(s)

    return texts


def get_platform():
    plat = platform.platform()
    if plat.find('Darwin') != -1:
        return 'mac'
    elif plat.find('Linux') != -1:
        return 'linux'
    else:
        return 'mac'


def get_aqi_level_info(aqi):
    try:
        aqi = int(aqi)
        if aqi >= 0 and aqi <= 50:
            return '优'
        elif aqi >= 51 and aqi <= 100:
            return '良'
        elif aqi >= 101 and aqi <= 150:
            return '轻度污染'
        elif aqi >= 151 and aqi <= 200:
            return '中度污染'
        elif aqi >= 201 and aqi <= 300:
            return '重度污染'
        elif aqi >= 300:
            return '严重污染'
    except Exception, e:
        return '无信息'


def get_week():
    week = datetime.datetime.today().strftime("%w")
    if week == '1':
        return '星期一'
    elif week == '2':
        return '星期二'
    elif week == '3':
        return '星期三'
    elif week == '4':
        return '星期四'
    elif week == '5':
        return '星期五'
    elif week == '6':
        return '星期六'
    elif week == '0' or week == '7':
        return '星期日'


def get_date():
    return datetime.datetime.today().strftime('%Y-%m-%d')


def get_aqi_level(aqi):
    try:
        aqi = int(aqi)
        if aqi >= 0 and aqi <= 50:
            return '优 绿色 空气质量令人满意，基本无空气污染 各类人群可正常活动'
        elif aqi >= 51 and aqi <= 100:
            return '良 黄色 空气质量可接受，但某些污染物可能对极少数异常敏感人群健康有较弱影响,极少数异常敏感人群应减少户外活动'
        elif aqi >= 101 and aqi <= 150:
            return '轻度污染 橙色 易感人群症状有轻度加剧，健康人群出现刺激症状儿童、老年人及心脏病、呼吸系统疾病患者应减少长时间、高强度的户外锻炼'
        elif aqi >= 151 and aqi <= 200:
            return '中度污染 红色 进一步加剧易感人群症状，可能对健康人群心脏、呼吸系统有影响儿童、老年人及心脏病、呼吸系统疾病患者避免长时间、高强度的户外锻炼,一般人群适量减少户外运动'
        elif aqi >= 201 and aqi <= 300:
            return '重度污染 紫色 心脏病和肺病患者症状显著加剧，运动耐受力降低，健康人群普遍出现症状儿童、老年人和心脏病、肺病患者应停留在室内，停止户外运动，一般人群减少户外运动'
        elif aqi >= 300:
            return '严重污染 褐红色 健康人运动耐受力降低，有明显强烈症状，提前出现某些疾病儿童、老年人和病人应当留在室内，避免体力消耗，一般人群应避免户外活动'
    except Exception, e:
        return '无信息'
