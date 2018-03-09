# -*- coding: utf-8 -*-
#!/usr/bin/python

#tm1637数码管驱动
import math
import RPi.GPIO as GPIO
import threading
from time import sleep, localtime

# GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

HexDigits = [0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d,
             0x07, 0x7f, 0x6f, 0x77, 0x7c, 0x39, 0x5e, 0x79, 0x71]

ADDR_AUTO = 0x40
ADDR_FIXED = 0x44
STARTADDR = 0xC0
# DEBUG = False


class TM1637:
    __doublePoint = False
    __Clkpin = 0
    __Datapin = 0
    __brightness = 1.0  # 默认100%亮度
    __currentData = [0, 0, 0, 0]

    def __init__(self, CLK, DIO, brightness):
        self.__Clkpin = CLK
        self.__Datapin = DIO
        self.__brightness = brightness
        GPIO.setup(self.__Clkpin, GPIO.OUT)
        GPIO.setup(self.__Datapin, GPIO.OUT)

    def cleanup(self):
        """停止更新时钟，关闭显示，清理GPIO"""
        self.StopClock()
        self.Clear()
        GPIO.cleanup()

    def Clear(self):
        b = self.__brightness
        point = self.__doublePoint
        self.__brightness = 0
        self.__doublePoint = False
        data = [0x7F, 0x7F, 0x7F, 0x7F]
        self.Show(data)
        # Restore previous settings:
        self.__brightness = b
        self.__doublePoint = point

    def ShowInt(self, i):
        s = str(i)
        self.Clear()
        for i in range(0, len(s)):
            self.Show1(i, int(s[i]))

    def Show(self, data):
        for i in range(0, 4):
            self.__currentData[i] = data[i]

        self.start()
        self.writeByte(ADDR_AUTO)
        self.br()
        self.writeByte(STARTADDR)
        for i in range(0, 4):
            self.writeByte(self.coding(data[i]))
        self.br()
        self.writeByte(0x88 + int(self.__brightness))
        self.stop()

    def Show1(self, DigitNumber, data):
        """在指定位上显示一个数字"""
        # 位数在0-3之间
        if(DigitNumber < 0 or DigitNumber > 3):
            return

        self.__currentData[DigitNumber] = data

        self.start()
        self.writeByte(ADDR_FIXED)
        self.br()
        self.writeByte(STARTADDR | DigitNumber)
        self.writeByte(self.coding(data))
        self.br()
        self.writeByte(0x88 + int(self.__brightness))
        self.stop()

    def SetBrightness(self, percent):
        """调整亮度百分比"""
        max_brightness = 7.0
        brightness = math.ceil(max_brightness * percent)
        if (brightness < 0):
            brightness = 0
        if(self.__brightness != brightness):
            self.__brightness = brightness
            self.Show(self.__currentData)

    def ShowDoublepoint(self, on):
        """设置是否显示冒号"""
        if(self.__doublePoint != on):
            self.__doublePoint = on
            self.Show(self.__currentData)

    def writeByte(self, data):
        for i in range(0, 8):
            GPIO.output(self.__Clkpin, GPIO.LOW)
            if(data & 0x01):
                GPIO.output(self.__Datapin, GPIO.HIGH)
            else:
                GPIO.output(self.__Datapin, GPIO.LOW)
            data = data >> 1
            GPIO.output(self.__Clkpin, GPIO.HIGH)

        # 等待ACK
        GPIO.output(self.__Clkpin, GPIO.LOW)
        GPIO.output(self.__Datapin, GPIO.HIGH)
        GPIO.output(self.__Clkpin, GPIO.HIGH)
        GPIO.setup(self.__Datapin, GPIO.IN)

        while(GPIO.input(self.__Datapin)):
            sleep(0.001)
            if(GPIO.input(self.__Datapin)):
                GPIO.setup(self.__Datapin, GPIO.OUT)
                GPIO.output(self.__Datapin, GPIO.LOW)
                GPIO.setup(self.__Datapin, GPIO.IN)
        GPIO.setup(self.__Datapin, GPIO.OUT)

    def start(self):
        """向TM1637发送开始信号"""
        GPIO.output(self.__Clkpin, GPIO.HIGH)
        GPIO.output(self.__Datapin, GPIO.HIGH)
        GPIO.output(self.__Datapin, GPIO.LOW)
        GPIO.output(self.__Clkpin, GPIO.LOW)

    def stop(self):
        GPIO.output(self.__Clkpin, GPIO.LOW)
        GPIO.output(self.__Datapin, GPIO.LOW)
        GPIO.output(self.__Clkpin, GPIO.HIGH)
        GPIO.output(self.__Datapin, GPIO.HIGH)

    def br(self):
        """短时间中断"""
        self.stop()
        self.start()

    def coding(self, data):
        if(self.__doublePoint):
            pointData = 0x80
        else:
            pointData = 0

        if(data == 0x7F):
            data = 0
        else:
            data = HexDigits[data] + pointData
        return data
