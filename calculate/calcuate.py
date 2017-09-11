from datetime import datetime;
import time;
from sys import stdin


# 预约场地的核心算法
class Calculate:
    def __init__(self):
        # 预约记录
        self.book = {};
        # 场地和时间记录下
        self.address = {};
        # 费用的初始化
        self.defalutMoney = {};
        for weekday in range(0, 6, 1):
            # 根据时间段不同，费用不同
            if (weekday < 5):
                # 周一到周五
                self.defalutMoney[weekday] = {};
                self.defalutMoney[weekday][9] = 30;
                self.defalutMoney[weekday][10] = 30;
                self.defalutMoney[weekday][11] = 30;
                self.defalutMoney[weekday][12] = 30;
                self.defalutMoney[weekday][13] = 50;
                self.defalutMoney[weekday][14] = 50;
                self.defalutMoney[weekday][15] = 50;
                self.defalutMoney[weekday][16] = 50;
                self.defalutMoney[weekday][17] = 50;
                self.defalutMoney[weekday][18] = 50;
                self.defalutMoney[weekday][19] = 80;
                self.defalutMoney[weekday][20] = 80;
                self.defalutMoney[weekday][21] = 60;
                self.defalutMoney[weekday][22] = 60;
                self.defalutMoney[weekday][18] = 60;


            else:
                # 周末价格
                self.defalutMoney[weekday] = {}
                self.defalutMoney[weekday][9] = 40;
                self.defalutMoney[weekday][10] = 40;
                self.defalutMoney[weekday][11] = 40;
                self.defalutMoney[weekday][12] = 40;
                self.defalutMoney[weekday][13] = 50;
                self.defalutMoney[weekday][14] = 50;
                self.defalutMoney[weekday][15] = 50;
                self.defalutMoney[weekday][16] = 50;
                self.defalutMoney[weekday][17] = 50;
                self.defalutMoney[weekday][18] = 50;
                self.defalutMoney[weekday][19] = 60;
                self.defalutMoney[weekday][20] = 60;
                self.defalutMoney[weekday][21] = 60;
                self.defalutMoney[weekday][22] = 60;
                self.defalutMoney[weekday][18] = 60;

        self.today = datetime.now().weekday();
        # datetime.strptime(self.today,"%Y%m%d");

    # 根据时间字符串，转换为时间
    def getTimeFromDay(self, strDay):
        return datetime.strptime(strDay, "%Y%m%d");

    # 根据日期，换算为星期几
    def getWeekFromDay(self, dayTime):
        return dayTime.weekday();

    # 获取当前时间，是星期几
    def getWeedDayFromNow(self):
        return datetime.now().weekday();

    # 取消预约,违约金
    def cancaleMoney(self, day, startTime, endTime):
        weekday = self.getWeekFromDay(day)
        money = 0;
        if weekday < 5:
            money = self.handleMoney(day, startTime, endTime) / 2;
        else:
            money = self.handleMoney(day, startTime, endTime) / 4;
        return money;

    # 根据时间，计算预约累计金额
    def handleMoney(self, day, startTime, endTime):
        sumMoney = 0;
        day = self.getWeekFromDay(day)
        str = datetime.strftime(startTime, "%H");
        end = datetime.strftime(endTime, "%H");
        for i in range(int(str) + 1, int(end) + 1):
            sumMoney += self.defalutMoney[day][i];
        return sumMoney;

    # 检查场地和时间是否被使用,1 代表可用，0 不可用，场地时间有冲突
    def checkAddress(self, daystr, startTime, endTime, address):
        star = datetime.strftime(startTime, "%H");
        end = datetime.strftime(endTime, "%H");
        if int(star) < 9 or int(end) > 22:
            print("预约时间，不在营业范围时间里，检查预约时间范围！");
        else:
            for i in range(int(star) + 1, int(end) + 1):
                keyAddress = daystr + "," + address + "," + str(i);
                print("keyAddress:" + keyAddress)
                if keyAddress in self.address.keys():
                    value = self.address[keyAddress];
                    if type(value) != "NoneType" or value != 0:
                        print("场地时间冲突！")
                        return 0;
        return 1;

    # 预约场地
    def bookAddress(self, user, daystr, time, address, cancle):

        # 预约时间，整点检查
        if time[3:5] != "00" or time[9:] != "00":
            print("预约时间不是整点，请检查预约时间是否整点时间");
            return;

        # 场地检查
        if address == "A" or address == "B" or address == "C" or address == "D":
            # 参数转换，和检查
            day = datetime.strptime(daystr, "%Y-%m-%d");
            startTime = datetime.strptime(daystr + " " + time[0:5], "%Y-%m-%d %H:%M");
            endTime = datetime.strptime(daystr + " " + time[6:], "%Y-%m-%d %H:%M");
            flag = self.checkAddress(daystr, startTime, endTime, address)  # 预约标记，1可以预约，0不能预约
            star = datetime.strftime(startTime, "%H");
            end = datetime.strftime(endTime, "%H");
            # 预约或取消预约逻辑处理
            if cancle == "C":
                # 取消预约操作
                for i in range(int(star) + 1, int(end) + 1):
                    keyAddress = daystr + "," + address + "," + str(i);
                    self.address[keyAddress] = 0;
                # 修改记录入账信息
                keyBook = address + "," + daystr + "," + time;
                if keyBook in self.book.keys():
                    self.book[keyBook] = self.cancaleMoney(day, startTime, endTime);
                    print("取消预约成功")
                else:
                    print("取消预约对象不存在")
            else:
                # 预约操作
                if flag == 1:
                    # 可预约
                    for i in range(int(star) + 1, int(end) + 1):
                        keyAddress = daystr + "," + address + "," + str(i);
                        self.address[keyAddress] = 1;
                    # 记录入账信息
                    keyBook = address + "," + daystr + "," + time;
                    self.book[keyBook] = self.handleMoney(day, startTime, endTime);
                    print("预约场地成功");
                else:
                    # 场地时间冲突
                    print("预约失败");
        else:
            print("没有此场地，场地必须是A,B,C,D中一个");

    # 将字典转化为列表
    def dict2list(self, dic: dict):
        keys = dic.keys()
        vals = dic.values()
        lst = [(key, val) for key, val in zip(keys, vals)]
        return lst

    # 解析函数，打印信息
    def main(self, read):

        if read is "":
            print("")
            print("收入汇总");
            print("--");
            # key排序
            sortList = sorted(self.dict2list(self.book), key=lambda x: x[0], reverse=False);
            print(self.book)
            print(sortList)
            group = "";  # 当前分类
            groupMoney = 0;  # 当前分类金额
            sumMoney = 0;  # 累计金额
            for i in sortList:
                tuple = i;
                if group == "":
                    # 第一次循环
                    group = tuple[0][0:1];
                    print("场地：" + group)
                if tuple[0][0:1] != group:
                    # 场地变了
                    group = tuple[0][0:1];
                    print("小计：" + str(groupMoney) + "元");
                    print("");
                    groupMoney = 0;  # 重新分类计算
                    print("场地：" + group)
                money = tuple[1];
                sumMoney += money;
                groupMoney += money;
                print(tuple[0][2:12] + " " + tuple[0][13:24] + " " + str(money) + "元");
            print("小计：" + str(groupMoney) + "元");
            print("--------");
            print("总计：" + str(sumMoney));
            print("")
        else:
            params = read.split(" ");
            if (len(params) >= 4):
                user = params[0];
                day = params[1];
                time = params[2];
                address = params[3];
                cancleFlag = "P";
                if len(params) == 5:
                    cancleFlag = params[4];

                if cancleFlag == "C":
                    self.bookAddress(user=user, daystr=day, time=time, address=address, cancle=cancleFlag);
                else:
                    self.bookAddress(user=user, daystr=day, time=time, address=address, cancle=cancleFlag);


# 入口函数
if __name__ == '__main__':
    # 执行主函数
    calculate = Calculate()
    while 1 == 1:
        print('请输入命令:')
        read = stdin.readline().strip('\n');
        calculate.main(read)
