#!/usr/bin/env python
# coding: utf-8

import sys
import urllib
import urllib2
import time
import datetime


def sendevent():
    # json = '''{'warnJson':"%s"}'''
    # values = {'title': subject, 'origin_id': id, 'summary': msg, 'status': '1', 'first_occurrence': first_occurrence,
    #           'original_severity': severity, 'ip': ip, 'hostname': hostname, 'source': 'zabbix'}
    #
    # jsonObj = {'warnJson': {'title': subject, 'origin_id': id, 'summary': msg, 'status': '1',
    #                         'first_occurrence': first_occurrence, 'original_severity': severity, 'ip': ip,
    #                         'hostname': hostname, 'source': 'zabbix'}
    #
    #            }

    json222 = '''{'warnJson':"%s"}'''
    values = {'title': 'PROBLEM', 'origin_id': '255', 'summary': 'Too many processes', 'status': '1',
              'first_occurrence': '2017-06-07 17:02:12', 'original_severity': '2', 'ip': '127.0.0.1',
              'hostname': 'localhost', 'source': 'nagios'}

    json222 = json222 % (values)
    param = eval(json222)

    #   jsonStr = jsonObj.dumps(jsonObj)
    #     jsonStrEn = jsonStr.encode("utf-8")

    print(json222)

    data = urllib.urlencode(param)  # str
    post_url = 'http://10.6.10.178:9000/hardwareMgr/commoncollect'
    try:
        conn = urllib2.urlopen(post_url, data)
        conn.encoding = 'utf-8'
        print
        res = conn.read().decode('utf-8')
        print("res:" + repr(res))
    except Exception as e:
        print(repr(e))


if __name__ == '__main__':

    sendevent()
