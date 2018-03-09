# -*- coding: utf-8 -*-
#!/usr/bin/python

from time import sleep
from datetime import datetime
from tm1637 import TM1637
import RPi.GPIO as GPIO
import urllib2
import json
import csv

# GPIO口使用BCM编码
GPIO.setmode(GPIO.BCM)

# 定义按键引脚
pin_btn = 21

# 初始化按键的状态，内部上拉
GPIO.setup(pin_btn, GPIO.IN, pull_up_down = GPIO.PUD_UP)
 
# 初始化按键的次数
press_times = 1

# 定义数码管引脚亮度
Display = TM1637(CLK=23, DIO=24, brightness=1.0)
Display.Clear()

# 定义温湿度传感器引脚
pin_dht11 = 4

# 读取城市代码csv文件
def getcitycode(csvfile,city):
    csvcontent = csv.reader(file(csvfile, 'rb'))
    res=[]
    for line in csvcontent:
        if line[0].find(city)<>-1:
            res.append(line[1])
    i = res[0]
    return i

# 获取天气信息
def getweather(citypinyin):
    citypinyin = getcitycode('citycode.csv', citypinyin)
    # 和风天气API
    url = 'https://free-api.heweather.com/v5/weather?city=' + citypinyin +'&key=8a439a7e0e034cdcb4122c918f55e5f3'
    # 用urllib2创建一个请求并得到返回结果
    req = urllib2.Request(url)
    resp = urllib2.urlopen(req).read()
    # print resp
    # print type(resp)
    # 将json转化为Python的数据结构
    json_data = json.loads(resp)
    city_data=json_data['HeWeather5'][0]
    hourly_data= json_data['HeWeather5'][0]['hourly_forecast']
    daily_data = json_data['HeWeather5'][0]['daily_forecast']
    pm = city_data['aqi']['city']['pm25']
    minqw = '{1}'.format(str(daily_data[0]['date']),daily_data[0]['tmp']['min'],daily_data[0]['tmp']['max'])
    maxqw = '{2}'.format(str(daily_data[0]['date']),daily_data[0]['tmp']['min'],daily_data[0]['tmp']['max'])
    # print json_data
    # 打印天气信息
    print u'当前时间：' + daily_data[0]['date']
    print u'城市：' + city_data['basic']['city']
    print u'PM指数：' + city_data['aqi']['city']['pm25']
    print u'白天天气：' + daily_data[0]['cond']['txt_d']
    print u'夜间天气：' + daily_data[0]['cond']['txt_n']
    print u'今天是{0}  气温：{1}°C/{2}°C'.format(str(daily_data[0]['date']),daily_data[0]['tmp']['min'],daily_data[0]['tmp']['max'])
    print u'未来1小时天气：{0} {1}'.format(str(hourly_data[0]['date']).split()[1],hourly_data[0]['cond']['txt'])
    print u'未来4小时天气：{0} {1}'.format(str(hourly_data[1]['date']).split()[1],hourly_data[1]['cond']['txt'])
    print u'未来7小时天气：{0} {1}'.format(str(hourly_data[2]['date']).split()[1],hourly_data[2]['cond']['txt'])
    print u'{0} 天气：{1}°C/{2}°C'.format(daily_data[1]['date'],daily_data[1]['tmp']['min'],daily_data[1]['tmp']['max'])
    print u'{0} 天气：{1}°C/{2}°C'.format(daily_data[2]['date'],daily_data[1]['tmp']['min'],daily_data[2]['tmp']['max'])
    print u'穿衣建议：' + json_data['HeWeather5'][0]['suggestion']['drsg']['txt']
    return pm , minqw , maxqw

# 获取当前DHT11温湿度传感器信息
def gettemperature(pin_dht11):
    DHT11 = pin_dht11
    data = []
    j = 0
    GPIO.setmode(GPIO.BCM)
    sleep(1)
    GPIO.setup(DHT11, GPIO.OUT)
    GPIO.output(DHT11, GPIO.LOW)
    sleep(0.02)
    GPIO.output(DHT11, GPIO.HIGH)
    GPIO.setup(DHT11, GPIO.IN)
    while GPIO.input(DHT11) == GPIO.LOW:
        continue
    while GPIO.input(DHT11) == GPIO.HIGH:
        continue
    while j < 40:
        k = 0
        while GPIO.input(DHT11) == GPIO.LOW:
            continue
        while GPIO.input(DHT11) == GPIO.HIGH:
            k += 1
            if k > 100:
                break
        if k < 8:
            data.append(0)
        else:
            data.append(1)
        j += 1

    print "sensor starts working."
    humidity_bit = data[0:8]
    humidity_point_bit = data[8:16]
    temperature_bit = data[16:24]
    temperature_point_bit = data[24:32]
    check_bit = data[32:40]

    humidity = 0
    humidity_point = 0
    temperature = 0
    temperature_point = 0
    check = 0

    for i in range(8):
        humidity += humidity_bit[i] * 2 ** (7-i)
        humidity_point += humidity_point_bit[i] * 2 ** (7-i)
        temperature += temperature_bit[i] * 2 ** (7-i)
        temperature_point += temperature_point_bit[i] * 2 ** (7-i)
        check += check_bit[i] * 2 ** (7-i)

    tmp = humidity + humidity_point + temperature + temperature_point

    if check == tmp:
        print "temperature :", temperature, "*C, humidity :", humidity, "%"
        DHT11status = True
    else:
        print "error"
        print "temperature :", temperature, "*C, humidity :", humidity, "% check :", check, ", tmp :", tmp
        DHT11status = False
        temperature = 88
        humidity = 88
    return temperature , humidity , DHT11status
    
# 获取当前时间
def getgetnowtime():
    hour = datetime.now().hour
    minute = datetime.now().minute
    second = datetime.now().second
    return hour , minute , second

# 获取当前日期
def getnowdate():
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    return year , month , day


# 定义按键函数
def onPress(channel):
    global press_times
    print('pressed')
    press_times += 1
    if press_times > 4:
        press_times = 1
    # 时钟模式
    if press_times == 1:
        print('time mode')
    # 日期模式
    elif press_times == 2:
        print('date mode')
    # 天气模式
    elif press_times == 3:
        print 'wether mode'
    # 温度模式
    elif press_times == 4:
        print 'temperature mode'

# 设置按键检测，检测到按下时调用 onPress 函数
GPIO.add_event_detect(pin_btn, GPIO.FALLING, callback = onPress, bouncetime = 500)

try:
    pm , minqw , maxqw = getweather('kaifeng')
    temperature , humidity , DHT11status = gettemperature(pin_dht11)
    getweathertimes = 0
    sensorinitial = True
    gettemperaturetimes = 0
    
    while(True):
# 按下一次显示时间
        if press_times == 1:
            hour , minute , second = getgetnowtime()
            currenttime = [ int(hour / 10), hour % 10, int(minute / 10), minute % 10 ]
            Display.ShowDoublepoint(second % 2)
            Display.Show(currenttime)
            sleep(1)

# 按下两次显示日期
        if press_times == 2:
            year , month , day = getnowdate()
            currentyear = [ int(year / 1000), int(year / 100) - int(year / 1000) * 10, int(year / 10) - int(year / 100) * 10, year - int(year / 10) * 10]
            currentdate = [ int(month / 10), month % 10, int(day / 10), day % 10]
            Display.ShowDoublepoint(False)
            Display.Show(currentyear)
            sleep(0.5)
            Display.ShowDoublepoint(True)
            Display.Show(currentdate)
            sleep(3)

# 按下三次显示天气
        if press_times == 3:
            if getweathertimes == 600:
                pm , minqw , maxqw = getweather('kaifeng')
                getweathertimes = 0
            currentpm = [ int(pm)/1000,int(pm)/100 - int(pm)/1000*10, int(pm)/10 - int(pm)/100*10, int(pm) % 10]
            currentqw=[ int(minqw)/10 - int(minqw)/100*10, int(minqw) % 10, int(maxqw)/10 - int(maxqw)/100*10, int(maxqw) % 10]
            Display.ShowDoublepoint(False)
            Display.Show(currentpm)
            sleep(3)
            Display.ShowDoublepoint(True)
            Display.Show(currentqw)
            sleep(3)
            getweathertimes += 1 

# 按下四次显示温度
        if press_times == 4:
            if gettemperaturetimes == 1:
                temperature , humidity , DHT11status = gettemperature(pin_dht11)
                if DHT11status:
                    wendu = temperature
                    shidu = humidity
                sensorinitial = False
                gettemperaturetimes = 0
            if DHT11status:
                wendu = temperature
                shidu = humidity
                currenttmp = [ int(wendu / 10), wendu % 10, int(shidu / 10), shidu % 10,]
                Display.ShowDoublepoint(True)
                Display.Show(currenttmp)
                sleep(1)
                gettemperaturetimes += 1
                
            else:
                if sensorinitial:
                    currenttmp = [ 8,8,8,8]
                    Display.ShowDoublepoint(True)
                    Display.Show(currenttmp)
                    sleep(1)
                    gettemperaturetimes += 1
                else:
                    Display.ShowDoublepoint(True)
                    Display.Show(currenttmp)
                    sleep(1)
                    gettemperaturetimes += 1

except KeyboardInterrupt:
    print('Ctrl+c, exit;')

finally:
    GPIO.cleanup()
