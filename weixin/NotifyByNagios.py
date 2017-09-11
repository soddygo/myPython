#!/usr/bin/env python
# coding: utf-8



import sys
import urllib
import urllib2
import time
import datetime
import re  # 正则表达式


# 微信推送服务封装，测试用，检查查看消息内容
class Weixin:
    def __init__(self):
        self.httpService = HttpService()

    # 当前时间
    def getCurrentTime(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


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

        notifyType = content_data[0]
        # 主机故障告警，此时service宏命令都是空，会影响参数分解
        if notifyType == 'host':
            params['notificationType'] = content_data[1]
            params['hostName'] = content_data[2]
            params['hostState'] = content_data[3]
            params['hostStateId'] = content_data[4]
            params['hostOutPut'] = content_data[5]
            params['hostDisplayName'] = content_data[6]
            params['hostAlias'] = content_data[7]
            params['hostAddress'] = content_data[8]
            params['lastHostStateChange'] = content_data[9]  # $LASTHOSTSTATECHANGE$
            params['hostEventId'] = content_data[10]  # HOSTEVENTID
            params['contactAlias'] = content_data[11]

        # 服务告警
        elif notifyType == 'service':
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

    # Nagios 发送告警信息
    def sendNagiosNotifcation(self, params):
        url = 'http://10.6.10.178:9000/hardwareMgr/commoncollect'
        notifyType = params['notifyType']  # 类型判断

        # 主机故障告警，此时service宏命令都是空，会影响参数分解
        if notifyType == 'host':
            notifyDesc = params['hostAlias']
            id_original = params['hostOutPut']
            notifyInfo = params['hostEventId'] #时间id
            first_occurrence = params['lastHostStateChange']
            stateId = params['hostStateId']  # 0=UP, 1=DOWN, 2=UNREACHABLE.
            severity = '5'  # 级别,默认未知
            if stateId == '0':
                print('状态正常，为什么会告警？！')
            elif stateId == '1':
                severity = '2'
            elif stateId == '2':
                severity = '1'

        # 服务告警
        elif notifyType == 'service':
            notifyInfo = params['serviceOutPut']
            notifyDesc = params['serviceDesc']
            id_original = params['serviceNotificationId']
            first_occurrence = params['lastServiceStateChange']

            # 值处理转换
            stateId = params['serviceStateId']  # 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN.
            severity = '5'  # 级别,默认未知
            if stateId == '0':
                print('状态正常，为什么会告警？！')
            elif stateId == '1':
                severity = '4'
            elif stateId == '2':
                severity = '1'
            elif stateId == '3':
                severity = '5'

         # json文本内容
        notify_content = {
            'parameter': notifyDesc,
            'severity': severity,
            'hostname': params['hostName'],
            # "original State": params['serviceState'],
            'status': '1',
            'original_severity': stateId,
            'ip': params['hostAddress'],
            'id_original': id_original,
            'title': notifyInfo[:50],
            'summary': notifyInfo,
            'first_occurrence': self.formatDate(first_occurrence),
            'source': 'Nagios'
        }

        # 数据存放
        resutlJson = '''{'warnJson':"%s"}'''
        resutlJson = resutlJson % notify_content

        return self.httpService.url_request(url, resutlJson)

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

    # 返回json对象
    def url_request(self, url, result):

        print("result:" + result)
        try:
            param = eval(result)
            data = urllib.urlencode(param)
            res = urllib2.urlopen(url, data)
            res.encoding = 'utf-8'
            responseStr = res.read().decode('utf-8')
            print("res result:", repr(responseStr))
            return responseStr

        except Exception as e:
            print(self.getCurrentTime(), '请求错误,原因:%r' % repr(e))  # 请求错误信息


# nagios 告警封装
class Nagios:
    def __init__(self):
        self.httpService = HttpService()
        self.weiXin = Weixin()

    # 测试
    def sendMessage(self, message):
        token = self.weiXin.get_token()  # 获取token
        self.weiXin.send_text_message(token=token, content=message)  # 推送消息

    # 发送json字符串
    def sendNagiosMessage(self, message):
        # token = self.weiXin.get_token()  # 获取token
        params = self.weiXin.handleNagiosParams(message)
        # self.weiXin.sendTestNagiosNotifcation(token, params) # nagios测试接口，通过微信发送查看json
        self.weiXin.sendNagiosNotifcation(params)  # nagios接口
        print('send nagios message')


def main():
    try:
        # 修改打印信息输出
        # make a copy of original stdout route
        stdout_backup = sys.stdout
        # define the log file that receives your log info
        log_file = open("/usr/local/nagios/mypython/nagios/message.log", "w")
        # redirect print output to log file
        sys.stdout = log_file

        # 逻辑调用
        nagios = Nagios()

        # content = args.content
        content = sys.argv[1]
        print("输入参数:", content)
        # nagios.sendMessage(content)
        nagios.sendNagiosMessage(content)
        log_file.close()
    except Exception as e:
        print('main错误,原因:%r' % repr(e))  # 请求错误信息


if __name__ == "__main__":
    main()
