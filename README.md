# raspi
some interesting script for RaspberryPi
这是一个简单的用于树莓派的显示脚本，需要硬件有：树莓派主机、tm1637驱动的数码管、DHT11温湿度传感器
tm1637.py 为 tm1637的驱动程序，heweather.py 用于获取天气信息 ，display.py 为脚本主程序
默认数码管引脚 CLK=23、DIO=24 温湿度传感器引脚 DATA=4，按键引脚 21。（均为BCM编码）
python display.py 启动程序
按键一次显示时间，两次显示日期（年月日滚动显示），三次显示天气（PM指数、气温滚动显示），四次显示温湿度（温度：湿度）
