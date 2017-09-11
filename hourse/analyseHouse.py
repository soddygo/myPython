# 楼盘分析
import xlrd
import xlwt
import pandas as pd  # 数据处理
import numpy as np

import pymysql
import os
import time
import sys


# 数据处理
class DataHanle:
    def __init__(self):
        self.excelPath = './hourse.xlsx'
        self.mysql = MySql()

    # 读取数据
    def readExcel(self):
        fname = self.excelPath;
        bk = xlrd.open_workbook(fname)
        shxrange = range(bk.nsheets)
        try:
            sh = bk.sheet_by_name("Sheet1")
        except:
            print("no sheet in %s named Sheet1" % fname)
        # 获取行数
        nrows = sh.nrows
        # 获取列数
        ncols = sh.ncols
        print
        "nrows %d, ncols %d" % (nrows, ncols)
        # 获取第一行第一列数据
        cell_value = sh.cell_value(1, 1)
        print(cell_value)

        row_list = []
        # 获取各行数据
        for i in range(1, nrows):
            row_data = sh.row_values(i)
            print("row_data:", row_data)
            row_list.append(row_data)
        # 返回所有数据
        return row_list

    # 写入excel,test
    def writeExcel(self):
        w = xlwt.Workbook()  # 创建工作簿 ()  # 创建一个工作簿
        ws = w.add_sheet('Hey, Hades')  # 创建一个工作表
        ws.write(0, 0, 'bit')  # 在1行1列写入bit
        ws.write(0, 1, 'huang')  # 在1行2列写入huang
        ws.write(1, 0, 'xuan')  # 在2行1列写入xuan
        w.save('./testDemo.xls')  # 保存

    # 数据进一步处理
    def convertData(self, rowList):
        print("转换数据格式")

    # 数据转换成矩阵
    def pivotTest(self):
        df = pd.DataFrame({'foo': ['one', 'one', 'one', 'two', 'two', 'two'],
                           'bar': ['A', 'B', 'C', 'A', 'B', 'C'],
                           'baz': [1, 2, 3, 4, 5, 6]})
        newDf = df.pivot(index='foo', columns='bar', values='baz')
        print(newDf)
        # df.pivot(index='foo', columns='bar')['baz']

    def handlePivot(self, data, index, columns, values):

        df = pd.DataFrame(data)
        resultData = df.pivot(index=index, columns=columns, values=values)
        result = resultData.fillna(0)
        # 打印
        print(result)

        test1 = result.index
        test2 = result.columns
        test3 = result.values
        print("index名称:"+repr(test1))
        print("columns名称:"+repr(test2))
        print("值内容:"+repr(test3))

        return result

    # 数据转换
    def handleData(self):
        querySelect = 'select * from  hourse.houseAnalyse'
        cursor = self.mysql.querySql(querySelect)
        rows = cursor.fetchall()

        currenthouseList = []
        currentbhList = []
        frombhList = []
        fromSumList = []
        for row in rows:
            currenthouse = row[0]
            currentbh = row[1]
            frombh = row[2]
            fromSum = row[3]
            # 放入列表
            currenthouseList.append(currenthouse)
            currentbhList.append(currentbh)
            frombhList.append(frombh)
            fromSumList.append(fromSum)

        result = {}
        result['currenthouseList'] = currenthouseList
        # result['currentbhList'] = currentbhList
        result['frombhList'] = frombhList
        result['fromSumList'] = fromSumList
        return result


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
        self.database = 'use hourse'
        self.table = 'house'

    # 当前时间
    def getCurrentTime(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    # 初始化字段信息
    def initColumns(self, bh, fromhouse, tohouse):
        # 字段信息
        columns = {}
        # 获取表字段名
        columns['bh'] = bh
        columns['fromhouse'] = fromhouse
        columns['tohouse'] = tohouse
        return columns

    # 插入数据
    def insert(self, table, columns):
        key = ','.join(list(columns.keys()))
        value = (columns['bh'], columns['fromhouse'], columns['tohouse'])
        print("value:", repr(value))
        self.sql = 'insert into %s(%s) ' % (table, key,) + 'VALUES (%s,%s,%s)'
        # self.sql = 'insert into %s(Tile)' % table + 'VALUES (%s)'
        print("self.sql:", self.sql)
        try:
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
            finally:
                cursor.close()
        except pymysql.Error as e:
            print(self.getCurrentTime(), '数据库错误,原因 %d: %s' % (e.args[0], e.args[1]))
        finally:
            self.connection.close()

    # excel插入数据
    def inserExcel(self, rowList):
        for i in range(1, len(rowList)):
            print("rowList type:", type(rowList))
            row_data = rowList[i]
            # 取出数据，插入数据库里
            bh = row_data[8]
            fromHouse = row_data[4]
            toHouse = row_data[17]
            column = self.initColumns(bh=bh, fromhouse=fromHouse, tohouse=toHouse)
            print("column:" + repr(column))
            self.insert(self.table, column)  # 插入一条进入数据库

    # 执行sql
    def exceSql(self, sql):
        # 执行分析完的sql放入建好的分析表里

        self.connection = pymysql.connect(**self.config)
        try:
            cursor = self.connection.cursor()
            cursor.execute(self.database)
            cursor.execute(sql)
            return 0
        except pymysql.Error as e:
            self.connection.rollback()
            print(self.getCurrentTime(), '执行失败,原因 %d: %s' % (e.args[0], e.args[1]))
        finally:
            cursor.close()
            self.connection.close()

    def querySql(self, sql):
        try:
            self.origconnecttion = pymysql.connect(**self.config)
            cursor = self.origconnecttion.cursor()
            cursor.execute(self.database)
            cursor.execute(sql)
            return cursor
        except pymysql.Error as e:
            print(self.getCurrentTime(), '查询失败，原因 %d:%s' % (e.args[0], e.args[1]))


# 主函数入口
def main():
    mysql = MySql()
    dataHandle = DataHanle()
    rowList = dataHandle.readExcel()
    # dataHandle.writeExcel()
    mysql.inserExcel(rowList)

    # 清空，重新插入
    deleSql = 'delete from hourse.houseAnalyse'
    mysql.exceSql(deleSql)

    # 执行sql，到另外一张表里
    sql = 'INSERT INTO hourse.houseAnalyse SELECT  a.tohouse,  b.bh,  a.fromhouse,  a.lookNum  FROM (  SELECT  t1.tohouse,  t1.fromhouse,  count(*) lookNum  FROM house t1  GROUP BY t1.tohouse, t1.fromhouse  ) a  LEFT JOIN (SELECT DISTINCT fromhouse,  bh  FROM house) b ON trim(a.tohouse) = trim(b.fromhouse)'
    mysql.exceSql(sql=sql)

    # handle data
    data = dataHandle.handleData()
    # result['currenthouseList'] = currenthouseList
    # result['currentbhList'] = currentbhList
    # result['frombhList'] = frombhList
    # result['fromSumList'] = fromSumList
    dataHandle.handlePivot(data, index='currenthouseList', columns='frombhList', values='fromSumList')

    # dataHandle.pivotTest()


if __name__ == '__main__':
    main()
