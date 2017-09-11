#!/usr/bin/env python
# coding:utf-8



from urllib import request, parse
from wxConfig import *
import pickle
import datetime, time
import argparse
import json
import ssl
# import argparse
import sys
import re  # 正则表达式


# 微信推送服务封装，测试用，检查查看消息内容
class Weixin:
    def __init__(self):
        self.httpService = HttpService()
        print("init")

    # 当前时间
    def getCurrentTime(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    # 获取token
    def get_token(self):
        data_pkl = './token_data.pkl'
        try:
            f = open(data_pkl, 'rb')
            data_dict = pickle.load(f)
            f.close()
        except:
            data_dict = {}
        try:
            print("data_dict:" + data_dict)
            expires_time = data_dict['expires_time']
        except:
            expires_time = 0
        now_time = int(time.mktime(datetime.datetime.now().timetuple()))
        if now_time >= expires_time:
            # url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
            url = WxGetToken
            values = {
                'corpid': CorpID,
                'corpsecret': Secret,
            }
            result = self.httpService.url_request(url, values, method='GET')
            if len(result) != 0:
                now_time = int(time.mktime(datetime.datetime.now().timetuple()))
                expires_time = now_time + 7200 - 10
                result['expires_time'] = expires_time
                f = open(data_pkl, 'wb')
                pickle.dump(result, f)
                f.close()
                access_token = result['access_token']
            else:
                print("Get token error,exit!")
                access_token = ''
        else:
            access_token = data_dict['access_token']
        return access_token

    # 初始化参数
    def handleNagiosParams(self, content):
        # 分隔符分割数据
        content_data = content.split('-@-')
        print("content_data len:" + str(len(content_data)))

        # python3
        # NotifyByNagios.py
        # "service-\$NOTIFICATIONTYPE\$-\$HOSTNAME\$-\$HOSTSTATE\$-\$HOSTSTATEID\$-\$HOSTOUTPUT\$-\$HOSTDISPLAYNAME\$-\$HOSTALIAS\$-\$HOSTADDRESS\$" \
        # "-\$SERVICEDESC\$-\$SERVICEDISPLAYNAME\$-\$SERVICESTATEID\$-\$SERVICEATTEMPT\$-\$SERVICESTATE\$-\$LASTSERVICESTATECHANGE\$-\$SERVICENOTIFICATIONID\$" \
        # "-\$SERVICEOUTPUT\$-\$CONTACTALIAS\$"
        params = {}
        params['notifyType'] = content_data[0]  # 手动输入的字符串类型
        params['notificationType'] = content_data[1]
        params['hostName'] = content_data[2]
        params['hostState'] = content_data[3]
        params['hostStateId'] = content_data[4]
        params['hostOutPut'] = content_data[5]
        params['hostDisplayName'] = content_data[6]
        params['hostAlias'] = content_data[7]
        params['hostAddress'] = content_data[8]
        params['serviceDesc'] = content_data[9]
        params['serviceDisplayName'] = content_data[10]
        params['serviceStateId'] = content_data[11]
        params['serviceAttempt'] = content_data[12]
        params['serviceState'] = content_data[13]
        params['lastServiceStateChange'] = content_data[14]
        params['serviceNotificationId'] = content_data[15]
        params['serviceOutPut'] = content_data[16]
        params['contactAlias'] = content_data[17]

        return params

    # 发送json数据，params类型是dict
    def sendJsonMessage(self, token, params):
        # url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + token + '&debug=' + str(DEBUG)
        url = WxSendMessage + '?access_token=' + token + '&debug=' + str(DEBUG)
        notifyType = params['notifyType']  # 类型判断
        if notifyType == 'host':
            notifyInfo = params['hostOutPut']
            notify_content = {
                "Notification Type": params['notificationType'],
                "hostname": params['hostName'],
                "original State": params['hostState'],
                "original_severity": params['hostStateId'],
                "ip": params['hostAddress'],
                "origin_id": params['serviceNotificationId'],
                "title": notifyInfo[:50],
                "summary": params['hostInfo'],
                "first_occurrence": self.formatDate(params['lastServiceStateChange']),
                "source": "Nagios"
            }
        elif notifyType == 'service':
            notifyInfo = params['serviceOutPut']
            notify_content = {
                "Notification Type": params['notificationType'],
                "Service": params['serviceDesc'],
                "hostname": params['hostName'],
                "original State": params['serviceState'],
                "original_severity": params['serviceStateId'],
                "ip": params['hostAddress'],
                "origin_id": params['serviceNotificationId'],
                "title": notifyInfo[:50],
                "summary": notifyInfo,
                "first_occurrence": self.formatDate(params['lastServiceStateChange']),
                "source": "Nagios"
            }
        else:
            # 获取信息错误
            notify_content = "Get nagios message notify info error.\n\nContent: %s" % json.dumps(params)
        values = {
            "touser": ToUser,
            "toparty": ToParty,
            "totag": ToTag,
            "msgtype": "text",
            "agentid": AgentId,
            "text": {
                "content": json.dumps(notify_content)
            }
        }
        return self.httpService.url_request(url, values, method='POST')

    # 测试接口 ，nagios
    def sendTestNagiosNotifcation(self, token, params):
        # url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + token + '&debug=' + str(DEBUG)
        url = WxSendMessage + '?access_token=' + token + '&debug=' + str(DEBUG)
        notifyInfo = params['serviceOutPut']
        # 值处理转换
        serviceStateId = params['serviceStateId']  # 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN.
        severity = '5'  # 级别,默认未知
        if serviceStateId == '0':
            print('状态正常，为什么会告警？！')
        elif serviceStateId == '1':
            severity = '4'
        elif serviceStateId == '2':
            severity = '1'
        elif serviceStateId == '3':
            severity = '5'

        # json文本内容
        notify_content = {
            "parameter": params['serviceDesc'],
            "severity": severity,
            "hostname": params['hostName'],
            # "original State": params['serviceState'],
            "status": '1',
            "original_severity": serviceStateId,
            "ip": params['hostAddress'],
            "origin_id": params['serviceNotificationId'],
            "title": notifyInfo[:50],
            "summary": notifyInfo,
            "first_occurrence": self.formatDate(params['lastServiceStateChange']),
            "source": "Nagios"
        }

        values = {
            "touser": ToUser,
            "toparty": ToParty,
            "totag": ToTag,
            "msgtype": "text",
            "agentid": AgentId,
            "text": {
                "content": json.dumps(notify_content)
            }
        }

        return self.httpService.url_request(url, values, method='POST')

    # Nagios 发送告警信息
    def sendNagiosNotifcation(self, params):
        url = NagiosUrl
        notifyType = params['notifyType']  # 类型判断

        notifyInfo = params['serviceOutPut']
        # 值处理转换
        serviceStateId = params['serviceStateId']  # 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN.
        severity = '5'  # 级别,默认未知
        if serviceStateId == '0':
            print('状态正常，为什么会告警？！')
        elif serviceStateId == '1':
            severity = '4'
        elif serviceStateId == '2':
            severity = '1'
        elif serviceStateId == '3':
            severity = '5'

        # json文本内容
        notify_content = {
            'parameter': params['serviceDesc'],
            'severity': severity,
            'hostname': params['hostName'],
            # "original State": params['serviceState'],
            'status': '1',
            'original_severity': serviceStateId,
            'ip': params['hostAddress'],
            'origin_id': params['serviceNotificationId'],
            'title': notifyInfo[:50],
            'summary': notifyInfo,
            'first_occurrence': self.formatDate(params['lastServiceStateChange']),
            'source': 'Nagios'
        }

        # dataJson = '''{'warnJson':"%s"}'''
        # dataJson = dataJson % (notify_content)
        # print("dataJson:"+dataJson)
        dataJson = {
            'warnJson': notify_content
        }
        # dataJson2 = eval(dataJson)
        # print("dataJson:" + json.dumps(dataJson2))


        return self.httpService.url_request(url, dataJson, method='POST')

    # 时间格式化，数字转换为时间文本格式：yyyy-mm-dd HH:mi:ss
    def formatDate(self, dateNumStr):
        # 校验是否数字
        regular = re.compile(r'^[-+]?[0-9]+$')
        result = regular.match(dateNumStr)
        if result:
            timeStr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(dateNumStr)))
            return timeStr
        else:
            return dateNumStr


# http 服务封装
class HttpService:
    def __init__(self):
        print('httpService inti')

    # 当前时间
    def getCurrentTime(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def test(self):
        ssl._create_default_https_context = ssl._create_unverified_context  # 导入ssl时关闭证书验证
        response = request.urlopen('https://www.baidu.com/')
        html = response.read()
        resHeard = response.info()
        print("reshead:", resHeard)
        print("html:", html)

    # 返回json对象
    def url_request(self, url, values={}, method='GET'):
        ssl._create_default_https_context = ssl._create_unverified_context  # 导入ssl时关闭证书验证
        if method == 'GET':
            # get 头部
            headers = {'Connection': 'keep-alive'}
            if len(values) != 0:
                # url_values = urllib..urlencode(values)
                params = ""  # url后缀参数
                for (k, v) in dict.items(values):
                    params += k + '=' + v + '&'
                params = params[0:len(params) - 1]
                furl = url + '?' + params
            else:
                furl = url
            print("furl:" + furl)
            try:
                req = request.Request(furl, headers=headers)
                res = request.urlopen(req)
                res.encoding = 'utf-8'
                statusCode = res.getcode()
                resHeard = res.info()
            except Exception as e:
                print(self.getCurrentTime(), '请求错误,原因:%r' % repr(e))  # 请求错误信息
        elif method == 'POST':
            # post 头部
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
                'Content-Type': 'application/json; charset=utf-8'}

            # param = eval(json.dumps(values), type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
            # data = parse.urlencode(param).encode('utf-8')

            #
            data = json.dumps(values).encode(encoding='UTF8')
            # # data = parse.urlencode(eval(json.dumps(values)))
            # data = urllib.urlencode(values)
            #


            try:
                req = request.Request(url, data=data, headers=headers)
                res = request.urlopen(req)  # 有data参数，自动默认为post
                res.encoding = 'utf-8'
                statusCode = res.getcode()
                resHeard = res.info()
            except Exception as e:
                print(self.getCurrentTime(), '请求错误,原因:%r' % repr(e))  # 请求错误信息
        else:
            print("不是Get，Post类型,[method]=", method)

        print("statusCode=", statusCode)
        print("resHeard=", resHeard)

        result = res.read().decode('utf-8')
        print("res result:", result)
        jsonObj = json.loads(result)
        return jsonObj


# nagios 告警封装
class Nagios:
    def __init__(self):
        self.httpService = HttpService()
        self.weiXin = Weixin()

    # 测试
    def sendMessage(self, message):
        token = self.weiXin.get_token()  # 获取token
        params = self.weiXin.handleNagiosParams(message)
        self.weiXin.sendJsonMessage(token=token, params=params)  # 推送消息

    # 发送json字符串
    def sendNagiosMessage(self, message):
        # token = self.weiXin.get_token()  # 获取token
        params = self.weiXin.handleNagiosParams(message)
        # self.weiXin.sendTestNagiosNotifcation(token, params) # nagios测试接口，通过微信发送查看json
        self.weiXin.sendNagiosNotifcation(params)  # nagios接口
        print('send nagios message')


def main():
    # 修改打印信息输出
    # make a copy of original stdout route
    stdout_backup = sys.stdout
    # define the log file that receives your log info
    log_file = open("/opt/myPython-1.0/weixin/message.log", "w")
    # redirect print output to log file
    sys.stdout = log_file

    # 逻辑调用
    nagios = Nagios()

    # parser = argparse.ArgumentParser(description="Nagios notify by weixin")
    # parser.add_argument("params(str)", default=None, help="notify params,split with '-'")
    # args = parser.parse_args()

    # content = args.content
    content = sys.argv[1]
    print("content demo:", content)
    nagios.sendMessage(content)
    # nagios.sendNagiosMessage(content)
    log_file.close()


if __name__ == "__main__":
    # token = get_token()
    # content=u"host-@@-111-@@-222-@@-333-@@-444-@@-测试-@@-zhangnq"
    # send_text_message(token, content)
    main()
