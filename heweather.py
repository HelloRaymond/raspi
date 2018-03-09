# -*- coding: utf-8 -*-
#!/usr/bin/python

import urllib2
import json
import csv

class heweather:
# 初始化获取天气json信息
    def __init__(self,city):
        # 从csv文件获取城市代码
        csvcontent = csv.reader(file('citycode.csv', 'rb'))
        res=[]
        for line in csvcontent:
            if line[0].find(city)<>-1:
                res.append(line[1])
        citycode = res[0]
        # 和风天气API
        url = 'https://free-api.heweather.com/v5/weather?city=' + citycode +'&key=8a439a7e0e034cdcb4122c918f55e5f3'
        # 用urllib2创建一个请求并得到返回结果
        req = urllib2.Request(url)
        resp = urllib2.urlopen(req).read()
        # print resp
        # print type(resp)
        # 将json转化为Python的数据结构
        self.json_data = json.loads(resp)
        self.city_data=self.json_data['HeWeather5'][0]
        self.hourly_data= self.json_data['HeWeather5'][0]['hourly_forecast']
        self.daily_data = self.json_data['HeWeather5'][0]['daily_forecast']
    # 打印原始json数据
    def printjson(self):
        json_data = self.json_data
        print json_data
        return json_data
    # 打印并返回城市名称，同时打印当前时间
    def cityinformation(self):
        cityinformation = self.city_data['basic']['city']
        print u'当前时间：' + self.daily_data[0]['date']
        print u'城市：' + self.city_data['basic']['city']
        return cityinformation
    # 打印并返回白天天气信息
    def daytime(self):
        daytime = self.daily_data[0]['cond']['txt_d']
        print u'白天天气：' + daytime
        return daytime
    # 打印并返回夜间天气信息
    def night(self):
        night = self.daily_data[0]['cond']['txt_n']
        print u'夜间天气：' + night
        return night
    # 打印并返回PM指数
    def PM(self):
        PM = self.city_data['aqi']['city']['pm25']
        print u'PM指数：' + PM
        return PM
    # 打印并返回当日最高气温和最高气温
    def daily(self):
        minqw = '{1}'.format(str(self.daily_data[0]['date']),self.daily_data[0]['tmp']['min'],self.daily_data[0]['tmp']['max'])
        maxqw = '{2}'.format(str(self.daily_data[0]['date']),self.daily_data[0]['tmp']['min'],self.daily_data[0]['tmp']['max'])
        date = '{0}'.format(str(self.daily_data[0]['date']),self.daily_data[0]['tmp']['min'],self.daily_data[0]['tmp']['max'])
        print u'今天是' + date + '气温：' + minqw + '°C/' + maxqw + '°C'
        return minqw , maxqw
    # 打印未来几小时的天气信息
    def hourly(self):
        print u'未来1小时天气：{0} {1}'.format(str(self.hourly_data[0]['date']).split()[1],self.hourly_data[0]['cond']['txt'])
        print u'未来4小时天气：{0} {1}'.format(str(self.hourly_data[1]['date']).split()[1],self.hourly_data[1]['cond']['txt'])
        print u'未来7小时天气：{0} {1}'.format(str(self.hourly_data[2]['date']).split()[1],self.hourly_data[2]['cond']['txt'])
    # 打印并返回明天最高气温和最高气温
    def tomorrow(self):
        minqw = '{1}'.format(self.daily_data[1]['date'],self.daily_data[1]['tmp']['min'],self.daily_data[1]['tmp']['max'])
        maxqw = '{2}'.format(self.daily_data[1]['date'],self.daily_data[1]['tmp']['min'],self.daily_data[1]['tmp']['max'])
        date = '{0}'.format(self.daily_data[1]['date'],self.daily_data[1]['tmp']['min'],self.daily_data[1]['tmp']['max'])
        print u'明天是' + date + '气温：' + minqw + '°C/' + maxqw + '°C'
        return minqw , maxqw
    # 打印并返回后天最高气温和最高气温
    def aftertomorrow(self):
        minqw = '{1}'.format(self.daily_data[2]['date'],self.daily_data[1]['tmp']['min'],self.daily_data[2]['tmp']['max'])
        maxqw = '{2}'.format(self.daily_data[2]['date'],self.daily_data[1]['tmp']['min'],self.daily_data[2]['tmp']['max'])
        date = '{0}'.format(self.daily_data[2]['date'],self.daily_data[1]['tmp']['min'],self.daily_data[2]['tmp']['max'])
        print u'后天是' + date + '气温：' + minqw + '°C/' + maxqw + '°C'
        return minqw , maxqw
    # 打印并返回穿衣建议
    def wearing(self):
        wearing = self.json_data['HeWeather5'][0]['suggestion']['drsg']['txt']
        print u'穿衣建议：' + wearing
        return wearing
