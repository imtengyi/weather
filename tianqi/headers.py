#-*- coding: utf-8 -*-

headers = '''Accept
text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Encoding
gzip, deflate
Accept-Language
en-US,en;q=0.5
Connection
keep-alive
Host
bj.lianjia.com
Upgrade-Insecure-Requests
1
User-Agent
Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:50.0) Gecko/20100101 Firefox/50.0
'''


def deal_headers(headers):
    datas = headers.split('\n')
    temp = ''
    for i in range(0, len(datas)):
        if i % 2 == 0:
            temp = temp + '\'' + datas[i] + '\'' + ':'
        else:
            temp = temp + ' \'' + datas[i] + '\','
            print(temp)
            temp = ''


if __name__ == '__main__':
    deal_headers(headers)
