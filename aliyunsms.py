#-*- coding: utf-8 -*-

import sys, os
import urllib, urllib2
import base64
import hmac
import hashlib
from hashlib import sha1
import time
import uuid
import json
import requests
import utils


class AliyunSms(object):
    def __init__(self):
        self.access_key_id = 'LTAIjHdzLIPJXaIZ'
        self.access_key_secret = '6cVfaC47jGhxUAmW3nt14kktGeqvSu'
        self.server_address = 'https://sms.aliyuncs.com'

        self.parameters = {
            'Format': 'JSON',
            'Version': '2016-09-27',
            'AccessKeyId': self.access_key_id,
            'SignatureVersion': '1.0',
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureNonce': str(uuid.uuid1()),
            'Timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time()))
        }

        self.user_params = {
            'Action': 'SingleSendSms',
            'ParamString': '',
            'RecNum': '',
            'SignName': '刘光全送上',
            'TemplateCode': 'SMS_39185168',
        }

    def send_sms(self, template_code, info, phone):
        parsms = json.dumps(info)
        full_params = self.user_params
        full_params['ParamString'] = parsms
        full_params['RecNum'] = phone
        full_params['TemplateCode'] = template_code

        url = self.compose_url(full_params)
        try:
            r = requests.get(url = url, timeout = 10)
            utils.log('send_sms response:%s' % r.text)
            return r.text
        except Exception, e:
            utils.log('send_sms exception msg:%s' % str(e))
            return None

    def percent_encode(self, source):
        temp = str(source)
        res = urllib.quote(temp.decode('utf8').encode('utf8'), '')
        #res = urllib.quote(temp, '')
        #res = urllib.quote(temp.decode(sys.stdin.encoding).encode('utf8'))
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')
        return res

    def compute_signature(self, parameters, access_key_secret):
        sorted_parameters = sorted(parameters.items(), key = lambda parameters: parameters[0])
        canonicalized_query_string = ''
        for (k, v) in sorted_parameters:
            canonicalized_query_string += '&' + self.percent_encode(k) + '=' + self.percent_encode(v)

        stringToSign = 'GET&%2F&' + self.percent_encode(canonicalized_query_string[1:])
        utils.log("compute_signature stringToSign:  " + stringToSign)

        h = hmac.new(access_key_secret + "&", stringToSign, sha1)
        signature = base64.encodestring(h.digest()).strip()

        return signature

    def compose_url(self, params):
        for key in params.keys():
            self.parameters[key] = params[key]

            utils.log('compose_url parameters:%s' % str(self.parameters))

        signature = self.compute_signature(self.parameters, self.access_key_secret)
        self.parameters['Signature'] = signature

        url = self.server_address + "/?" + urllib.urlencode(self.parameters)
        utils.log('compose_url parameters:%s' % str(self.parameters))
        utils.log('compose_url url:%s' % url)

        return url
