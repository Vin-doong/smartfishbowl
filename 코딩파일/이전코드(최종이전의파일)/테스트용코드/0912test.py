import I2C_LCD_driver
from time import *
import time
import os
import RPi.GPIO as GPIO
import smbus
import threading #시간,os,GPIO,smbus 등 라즈베리파이 연결을 위한 라이브러리
from flask import Flask, request, jsonify #HTTP 서버 생성 라이브러리
import Adafruit_DHT
from time import sleep

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

app = Flask(__name__)

# GPIO 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

motor_pwm_pin_1 = 16
GPIO.setup(motor_pwm_pin_1, GPIO.OUT)
motor_pwm_1 = GPIO.PWM(motor_pwm_pin_1, 1000)

motor_pwm_pin_2 = 5
GPIO.setup(motor_pwm_pin_2, GPIO.OUT)
motor_pwm_2 = GPIO.PWM(motor_pwm_pin_2, 1000)

# 온습도 센서 설정
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 18

# 수온 센서 설정
temp_sensor = '/sys/bus/w1/devices/28-fdd4451f64ff/w1_slave'

# PCF8591 모듈 설정
address = 0x48
AIN2 = 0x42
AIN3 = 0x43
AIN0 = 0x40
value = 0
value1 = 0
value2 = 0
value3 = 0
value4 = 0
jodo = 0
takdo = 0

# LCD 설정
bus = smbus.SMBus(1)

def temp_raw():
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_dht_sensor():
    global humidity, temperature
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        sleep(10)

dht_thread = threading.Thread(target=read_dht_sensor)
dht_thread.daemon = True
dht_thread.start()

def read_temp():
    lines = temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        sleep(0.2)
        lines = temp_raw()

    temp_output = lines[1].find('t=')
 
    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def set_motor_speed_1(speed):
    motor_pwm_1.start(speed)

def set_motor_speed_2(speed):
    motor_pwm_2.start(speed)

@app.route('/', methods=['GET'])
def do_GET(self):
    global mode, Request, state, value, value1, value2, value3, temperature, humidity, jodo, takdo
    messagetosend = f"{value}mA\n\n{value1}lux\n\n{value2:.1f}°C\n\n{value3}\n\n{temperature:.1f}°C,{humidity}%"
    messagetosend = messagetosend.encode('utf-8')

    self.send_response(200)
    self.send_header('Content-Type', 'text/plain')
    self.end_headers()
    self.wfile.write(messagetosend)

    Request = self.requestline
    Request = Request[5 : int(len(Request)-9)]
    print(Request)

    if Request == 'jadong': #어플에서 자동모드 실행시
        mylcd.clear()#0819수정
        bus.write_byte(address, AIN2)
        bus.read_byte(address)
        lvwater=bus.read_byte(address)
        bus.write_byte(address,AIN0)
        bus.read_byte(address)
        llux=bus.read_byte(address)
        print(":{0}".format(llux)) #조도센서 값 받아와서 화면에 출력
        watertemp = read_temp() #수온센서 변수 지정
        bus.write_byte(address,AIN3)
        bus.read_byte(address)
        pol=bus.read_byte(address)
        mylcd.lcd_display_string("{0:.1f}C / {1:.1f}mA".format(watertemp, lvwater),1)
        mylcd.lcd_display_string("{0}Lux / NTU={1:.1f}".format(llux, pol),2) #LCD에 조도센서값과 수온센서값 탁도센서값 표시
        print(":{0}".format(pol)) #탁도센서 값 받아와서 화면에 출력
        if pol < 50:
            if takdo != 1:            
                GPIO.output(6,1)
                takdo = 1   
        elif pol > 80:
            if takdo == 1:
                GPIO.output(6,0)
                takdo = 0 #탁도센서 범위를 임의로 지정하여 물순환 모터 구동 함수
        if llux < 200:
            if jodo != 1:
                GPIO.output(26, 0)
                jodo = 1
        elif llux > 230:
            if jodo == 1:
                GPIO.output(26, 1)
                jodo = 0 #조도센서 범위를 임의로 지정하여 LED 구동 함수
        #if lvwater < 10:
        #      if value != 1:
        #            GPIO.output(13, 1)
        #            value = 1
        #elif lvwater > 50:
        #      if value == 1:
        #            GPIO.output(13, 0)
        #            value = 0 # 수위센서 범위를 임의로 지정하여 물순환 모터 구동 함수
        #물 공급 자동으로 하면 깔끔한 느낌이 안남
                    
        if humidity is not None and temperature is not None:
            print("온도={0:0.1f}°C 습도={1:0.1f}%".format(temperature, humidity))
        pass
    elif Request == 'stop':
        GPIO.output(5, 0)
        GPIO.output(6, 0)
        GPIO.output(26, 0)
        GPIO.output(16, 0)
        GPIO.output(20, 0)
        GPIO.output(13, 0)
        GPIO.output(19, 0) #전체 모터 동작 정지
        pass
    elif Request == 're':
        mylcd.clear()#0819수정
        bus.write_byte(address, AIN2)
        bus.read_byte(address)
        value=bus.read_byte(address)
        print("value:%d"%value) #수위센서 값 받아와서 화면에 출력
        bus.write_byte(address,AIN0)
        bus.read_byte(address)
        value1=bus.read_byte(address)
        print(":{0}".format(value1)) #조도센서 값 받아와서 화면에 출력
        value2 = read_temp()
        print(value2) ##수온센서 값 받아와서 화면에 출력
        mylcd.lcd_display_string("{0:.1f}C / {1:.1f}mA".format(value2, value),1)
        mylcd.lcd_display_string("{0}Lux / NTU={1:.1f}".format(value1, value3),2) #LCD에 조도센서값과 수온센서값 탁도센서값 표시
        bus.write_byte(address,AIN3)
        bus.read_byte(address)
        value3=abs((bus.read_byte(address)))
        print("value:{0}".format(value3)) #탁도센서 값 받아와서 화면에 출력
        if humidity is not None and temperature is not None:
           print("온도={0:0.1f}°C 습도={1:0.1f}%".format(temperature, humidity))
        pass
    elif Request == 'ledon': #어플에서 LED on
        GPIO.output(26, 1)
    elif Request == 'ledoff': #어플에서 LED off
        GPIO.output(26, 0) 
    elif Request == 'saryoon': #어플에서 사료 모터 on
        GPIO.output(16, 1)
        GPIO.output(20, 0) #모터 동작
        set_motor_speed_1(20)
    elif Request == 'saryooff': #어플에서 사료 모터 on
        GPIO.output(16, 0)
        GPIO.output(20, 0) #모터 정지
        motor_pwm_1.stop()
    elif Request == 'takon': #어플에서 물순환 모터 on
        GPIO.output(5, 1)
        GPIO.output(6, 0) #모터 동작
        set_motor_speed_2(50)
    elif Request == 'takoff': #어플에서 물순환 모터 on
        GPIO.output(5, 0)
        GPIO.output(6, 0) #모터 정지
        motor_pwm_2.stop()
    elif Request == 'wtron' : #어플에서 물공급 모터 on
        GPIO.output(13,1)
        GPIO.output(19, 0) #모터 동작
    elif Request == 'wtroff' : #어플에서 물공급 모터 off
        GPIO.output(13, 0)
        GPIO.output(19, 0) #모터 정지
        
    
    return messagetosend

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8000)
    except KeyboardInterrupt:
        GPIO.cleanup()
