#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests
import responses
import pymysql
import os
import time
import sys
import re


# 插入mysql数据库
class MySql:
    def __init__(self):
        self.config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '631108',
            'charset': 'utf8',
            'autocommit': True
        }
        self.connection = {}
        self.sql = {}
        self.database = 'use mapcache'
        self.table = 'mapcache'
        self.origtable = 'gmapnetcache'  # 原始缓存的gis表
        self.origconnecttion = {}

    # 当前时间
    def getCurrentTime(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    # 字段信息
    def getField(self):
        self.field = ['Type', 'Zoom', 'X', 'Y', 'Tile']

    # 初始化字段信息
    def initColumns(self, type, zoom, x, y, filepath):
        # 字段信息
        columns = {}
        # 获取表字段名
        columns['Type'] = type
        columns['Zoom'] = zoom
        columns['X'] = x
        columns['Y'] = y
        # 图片特殊处理
        f = open(filepath, 'rb')
        tile = f.read()
        f.close()
        # columns['Tile'] = pymysql.Binary(tile)
        columns['Tile'] = tile
        return columns

    # 查询之前缓存的地图数据，然后根据坐标获取新题图数据
    def querymap(self):
        try:
            sql = "select type,zoom,x,y from %s" % self.origtable
            self.origconnecttion = pymysql.connect(**self.config)
            cursor = self.origconnecttion.cursor()
            cursor.execute(self.database)
            cursor.execute(sql)
            return cursor
        except pymysql.Error as e:
            print(self.getCurrentTime(), '查询失败，原因 %d:%s' % (e.args[0], e.args[1]))

    # 插入数据
    def insert(self, table, columns):
        try:
            key = ','.join(list(columns.keys()))
            value = (columns['Type'], columns['Zoom'], columns['X'], columns['Y'], columns['Tile'])
            self.sql = 'insert into %s(%s) ' % (table, key,) + 'VALUES (%s,%s,%s,%s,%s)'
            # self.sql = 'insert into %s(Tile)' % table + 'VALUES (%s)'
            self.connection = pymysql.connect(**self.config)
            try:
                cursor = self.connection.cursor()
                cursor.execute(self.database)
                cursor.execute(self.sql, value)
                return 0
            except pymysql.Error as e:
                self.connection.rollback()
                # print(e.args)
                if "key 'PRIMARY'" in e.args[1]:
                    print(self.getCurrentTime(), '数据已存在')
                else:
                    print(self.getCurrentTime(), '插入数据失败,原因 %d: %s' % (e.args[0], e.args[1]))
        except pymysql.Error as e:
            print(self.getCurrentTime(), '数据库错误,原因 %d: %s' % (e.args[0], e.args[1]))
        finally:
            cursor.close()
            self.connection.close()


# 地图数据爬虫
class Spider:
    def __init__(self):
        # self.urlsite = 'https://api.mapbox.com/styles/v1/mapbox/dark-v9/tiles/256/%s/%s/%s?access_token=pk.eyJ1Ijoic29kZHlnbyIsImEiOiJjajBxdDE3MjEwMXVhMzNtd3J0em11YjJsIn0.HQ3Mu5SpqaOmr8awN4163w'
        self.urlsite = 'https://api.mapbox.com/styles/v1/soddygo/cj0vs0lkq00pg2rqp5e78sbsj/tiles/256/%s/%s/%s?access_token=pk.eyJ1Ijoic29kZHlnbyIsImEiOiJjajBxdDE3MjEwMXVhMzNtd3J0em11YjJsIn0.HQ3Mu5SpqaOmr8awN4163w'
        self.mysql = MySql()

    # 当前时间
    def getCurrentTime(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def getMap(self, zoom, x, y):
        url = self.urlsite % (zoom, x, y)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', }
        print(self.getCurrentTime(), '开始爬取地图数据【zoom：%s ,x:%s, y:%s】' % (zoom, x, y))

        try:

            # 保存图片
            fileName = str(zoom) + '-' + str(x) + '-' + str(y)
            patch = sys.path[0]
            filepatch = patch + '/images/' + fileName + '.png'
            if os.path.exists(filepatch):
                print('图片已存在，不在保存【%s】' % fileName)
                return 200
            else:
                print(self.getCurrentTime(), '保存的图片为【%s】' % fileName)
                res = requests.get(url, headers=headers, stream=True)
                res.encoding = 'utf-8'
                statusCode = res.status_code
                self.cacheImage(res, filepatch)
                # 读取图片，插入数据库
                columns = self.mysql.initColumns(788865972, zoom, x, y, filepatch)
                # 插入数据库
                self.mysql.insert(self.mysql.table, columns)
                # 获取请求代码的返回码
                return statusCode

        except requests.RequestException as e:
            print(self.getCurrentTime(), '请求错误,原因:%r' % e)  # 缓存图片到临时目录

    def cacheImage(self, res, filepatch):
        with open(filepatch, 'wb', buffering=1) as f:
            for chunck in res.iter_content(chunk_size=1024):
                if chunck:
                    f.write(chunck)
            f.flush()
            f.close()


        # 缓存地图数据任务开始

    def taskStart(self):
        cursor = self.mysql.querymap()
        rows = cursor.fetchall()
        try:
            count = 0
            for row in rows:
                count += 1
                type = row[0]
                zoom = row[1]
                x = row[2]
                y = row[3]
                statusCode = self.getMap(zoom, x, y)
                if statusCode != 200:
                    print(self.getCurrentTime(), "为啥返回码不是200？")
                    # 重新尝试请求3次
                    trynum = 3
                    while (trynum > 0):
                        trynum -= 1
                        tryStatusCode = self.getMap(zoom, x, y)
                        if tryStatusCode == 200:
                            break
            print('遍历瓦片图当前数量:%d' % count)
        except pymysql.Error as e:
            print(self.getCurrentTime(), '数据库错误,原因 %d: %s' % (e.args[0], e.args[1]))
        finally:
            cursor.close()
            self.mysql.origconnecttion.close()


def main():
    print("start")
    spider = Spider()
    spider.taskStart()
    print("end")


if __name__ == '__main__':
    # 执行主函数
    main()
