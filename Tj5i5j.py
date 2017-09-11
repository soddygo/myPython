#!/usr/bin/env python
#-*- coding:utf-8 -*-
import requests
import re
import pymysql
import time
import os

# 数据清洗
class Tool:
    #移除双引号
    removeQuo=re.compile('"')
    #移除</b>、<b>
    removeB1=re.compile('</b>|<b>')
    #移除<span...>
    removeSp=re.compile('<span.*?>|</span>')
    #移除冒号
    removeH=re.compile('：')
    #移除<br/>
    removeBr=re.compile('<br/>')

    def replace(self,x):
        x=re.sub(self.removeQuo,"",x)
        x=re.sub(self.removeB1,"",x)
        x=re.sub(self.removeSp,"",x)
        x=re.sub(self.removeH,"",x)
        x=re.sub(self.removeBr,"",x)
        #strip删除前后多余内容
        return x.strip()

# 写入Mysql数据库
class Mysql:

    def __int__(self):
        self.fields=['urlsite','price', 'bedrm', 'hall', 'bathrm', 'unit_price', 'area', 'house_age', 'orient', 'floor', 'tol_floor', 'block_name', 'block_volume', 'eval_volume', 'see_volume','maint_name', 'maint_tel', 'wok_time','maint_store','self_see', 'house_id']

    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]')

    def insert(self,table,dict):
        self.config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '123456',
            'charset': 'utf8'
        }
        try:
            key=','.join(list(dict.keys()))
            value='"'+'","'.join(list(dict.values()))+'"'
            self.sql='INSERT INTO %s(%s) values(%s)'%(table,key,value)
            self.connection = pymysql.connect(**self.config)
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute('USE internet_worm')
                    # print(self.getCurrentTime(),'执行Mysql语句%s'%self.sql)
                    cursor.execute(self.sql)
                    self.connection.commit()
                    return 0
            except pymysql.Error as e:
                self.connection.rollback()
                # print(e.args)
                if "key 'PRIMARY'" in e.args[1]:
                    print(self.getCurrentTime(),'数据已存在')
                else:
                    print(self.getCurrentTime(),'插入数据失败,原因 %d: %s'%(e.args[0],e.args[1]))
            except pymysql.Error as e:
                print(self.getCurrentTime(),'数据库错误,原因 %d: %s'%(e.args[0],e.args[1]))
        finally:
                self.connection.close()

# 爬虫
class Spider:

    def __init__(self):
        self.urlsite='http://tj.5i5j.com/exchange/n'
        #调用 类:Tool&Mysql
        self.Tool=Tool()
        self.mysql=Mysql()

    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]')

    # 获取总页码数量
    # def getTotalPageNum(self):
    #     return 300

    #爬取pageIndex页面内容
    def getpage(self,pageIndex):
        url=self.urlsite+str(pageIndex)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',}
        print(self.getCurrentTime(),'开始爬取5i5j二手房源第%s页'%pageIndex)
        try:
            res=requests.get(url,headers=headers)
            res.encoding = 'utf-8'
            with open('d:\\data\\page.txt', 'r+', encoding='utf-8') as q:
                q.write(str(pageIndex+1))
            return res.text
        except requests.RequestException as e:
            print(self.getCurrentTime(),'一级链接请求错误,原因:%r'%e)
            # with open('page-first.txt','r') as p1:
            #     p1.write(pageIndex)

    #清洗出pageIndex页面内的二级链接
    def getSecondlink(self,pageIndex):
        content=self.getpage(pageIndex)
        pattern_temp = re.compile('<ul class="list-body">(.*)', re.S)
        items_temp = re.findall(pattern_temp, content)
        # print(items_temp)
        items_temp = items_temp[0]
        pattern = re.compile('<h2>.*?<a href=(.*?)target="_blank">.*?</h2>',re.S)
        items1 = re.findall(pattern, items_temp)
        if not items1 : return None
        print(self.getCurrentTime(),"第%d页共有%d个房源信息" % (pageIndex, len(items1)))
        secondurl=[]
        for item in items1:
            tempurl = 'http://tj.5i5j.com'+self.Tool.replace(item)
            secondurl.append(tempurl)
        return secondurl

    #爬取pageIndex页面二级链接下的内容
    def getSecondContent(self,pageIndex):
        secondurl=self.getSecondlink(pageIndex)
        if not secondurl: return None,None
        #测试
        # secondurl=['http://bj.5i5j.com/exchange/139720448']
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
        resp=[]
        m=1
        for url in secondurl:
            time.sleep(1)
            # if m>2:break
            try:
                res = requests.get(url, headers=headers)
                res.encoding = 'utf-8'
                resp.append(res.text)
                print(self.getCurrentTime(),'爬取第%d页第%d个链接'%(pageIndex,m),'还剩%d个'%(len(secondurl)-m))
                m+=1
            except requests.RequestException as e:
                print(self.getCurrentTime(),'爬取第%d页第%d个链接出现错误，原因：%r'%(pageIndex,m,e))
        return resp, secondurl

    #清洗pageIndex页面二级链接内容
    def getSecondContentClear(self,pageIndex):
        (secondcontent,secondurl)=self.getSecondContent(pageIndex)
        if not secondurl:return None
        # print(secondcontent,secondurl)
        # 北京我爱我家
        # pattern = re.compile('<ul class="house-info".*?售价(.*?)万元.*?<ul class="house-info-2">.*?户型(.*?)室(\d?)厅(\d?)卫&nbsp.*?单价(.*?)元.*?<a href.*?面积(.*?)平米.*?</li>.*?年代(.*?)年.*?</li>.*?朝向(.*?)</li>.*?楼层.*?</b>(.*?)\/(.*?)层/*?</li>.*?小区(.*?)<span>.*?小区成交记录(.*?)</a>.*?经纪人房评(.*?)</a>.*?客户看房数(.*?)</b>.*?<dl class="house-broker-info">.*?<p class="mr-t">(.*?)</p>.*?<p class="house-broker-tel">(.*?)<a class="broker-wx-icon".*?年限(.*?)年.*?所属门店.*?<a title="(.*?)".*?本房源带看次数(.*?)次.*?<p class="house-code">.*?<span>.*?房源编号(.*?)</span>',re.S)
        # 天津我爱我家
        pattern = re.compile(
            '<ul class="house-info">.*?售价(.*?)万元.*?<ul class="house-info-2">.*?户型(.*?)室(\d?)厅(\d?)卫&nbsp.*?单价(.*?)元.*?<a href.*?面积(.*?)平米.*?</li>.*?年代(.*?)年.*?</li>.*?朝向(.*?)</li>.*?楼层.*?</b>(.*?)\/(.*?)层/*?</li>.*?小区(.*?)<span>.*?小区成交记录(.*?)</a>.*?经纪人房评(.*?)</a>.*?客户看房数(.*?)</b>.*?<dl class="house-broker-info">.*?<p class="mr-t ers-xing">(.*?)</span>.*?</p>.*?<p class="house-broker-tel">(.*?)<a class="broker-wx-icon".*?年限(.*?)年.*?所属门店.*?<a title="(.*?)".*?本房源带看次数(.*?)次.*?<p class="house-code">.*?<span>.*?房源编号(.*?)</span>',
            re.S
        )
        #intialization 初始化
        dict = {}
        #注释：
        # '网页链接'=urlsite，'售价'=price, '室'=bedrm, '厅'=hall, '卫'=bathrm, '单价'=unit_price, '面积'=area, '房屋年代'=house_age, '朝向'=orient, '楼层'=floor, '总楼层'=tol_floor, '小区'=block_name, '小区成交记录'=block_volume, '经纪人房评量'=eval_volume, '房屋带看量'=see_volume,'维护经纪人姓名'=maint_name, '维护人电话'=maint_tel,'维护人从业年限'=wok_time, '维护人门店'=maint_store, '维护人带看本房源次次数'=self_see,'房源编号'=house_id
        fields = ['price', 'bedrm', 'hall', 'bathrm', 'unit_price', 'area', 'house_age', 'orient', 'floor', 'tol_floor', 'block_name', 'block_volume', 'eval_volume', 'see_volume', 'maint_name', 'maint_tel', 'wok_time','maint_store','self_see', 'house_id']
        #第j+1个二级链接
        j=0
        for content in secondcontent:
            try:
                items=re.findall(pattern,content)
                if items:
                    dict['pt']=time.strftime('%Y%m%d')
                    dict['urlsite']=secondurl[j]
                    i=0
                    while i < len(items[0]):
                        temp = self.Tool.replace(items[0][i])
                        dict[fields[i]] = temp
                        i+=1
                    j+=1
                    self.mysql.insert('5i5jhousedel',dict)
                else:break
            except re.error as e:
                print(self.getCurrentTime(),'匹配发生错误,原因：%d %s'%(e.args[0],e.args[1]))
        return 1

    # # 主函数
    # def main(self,):
    #
    #     print(self.getCurrentTime(),'Web-Crawler Starts')
    #     #打开/创建临时文件
    #     log_file=open('crawler.log','w')
    #     #重新定向
    #     sys.stdout=log_file


#主函数
def main():
    a=Spider()
    x=1
    while x<1000:
        try:
            with open('d:\\data\\page.txt','r+',encoding='utf-8') as p:
                temp=int(p.readline().strip())
                if temp!=x:
                    x=temp
            result=a.getSecondContentClear(x)
            # print(result)
            x+=1
            if not result:
                with open('d:\\data\\page.txt', 'w', encoding='utf-8') as p:
                    p.write(str(1))
                break
        except:pass

#判断page文件是否存在
if not os.path.exists('d:\\data\\page.txt'):
    with open('d:\\data\\page.txt', 'w', encoding='utf-8') as z:
        z.write(str(1))

count = 0
#重复爬取3次，查漏补缺
while count<3:
    main()
    count+=1
