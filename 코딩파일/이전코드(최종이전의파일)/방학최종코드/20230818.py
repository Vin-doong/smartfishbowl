import I2C_LCD_driver
from time import *
import time
import os
import RPi.GPIO as GPIO
import smbus
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
import threading #시간,os,GPIO,smbus 등 라즈베리파이 연결을 위한 라이브러리
from http.server import BaseHTTPRequestHandler, HTTPServer #HTTP 서버 생성 라이브러리
import Adafruit_DHT

GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(26, GPIO.OUT) #LED
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT) #수중모터
GPIO.setwarnings(False)  #모터 구동을 위한GPIO 핀번호 배치 및 설치

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 18  # DHT 센서가 연결된 GPIO 핀 번호입니다.

temp_sensor='/sys/bus/w1/devices/28-fdd4451f64ff/w1_slave' #수온 센서 구동 위치 지정
address=0x48
AIN2=0x42
AIN3=0x43
AIN0 = 0x40
value = 0
value1 = 0
value2 = 0
value3 = 0
value4 = 0
jodo=0
takdo=0

humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

bus=smbus.SMBus(1) #PCF8591 모듈 사용을 위한 smbus의 주소 및 변수 지정
mylcd = I2C_LCD_driver.lcd() #LCD 클리어 함수

def temp_raw():
    f = open(temp_sensor,'r')
    lines = f.readlines()
    f.close()
    return lines       #수온 센서 파일의 내용을 읽어오는 함수
 
# 온습도 값을 읽어오는 함수
def read_dht_sensor():
    global humidity, temperature
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        time.sleep(5)  # 5초마다 온습도 값을 업데이트
# 온습도 값을 업데이트하는 스레드 생성 및 실행
dht_thread = threading.Thread(target=read_dht_sensor)
dht_thread.daemon = True  # 메인 스레드가 종료되면 함께 종료
dht_thread.start()

def read_temp():
    lines = temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = temp_raw()

    temp_output = lines[1].find('t=')
 
    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c      #수온 센서 읽어온 파일의 구문을 분석해 온도부분만 반환하는 함수


class RequestHandler_httpd(BaseHTTPRequestHandler):
 def do_GET(self):
  global mode, Request, state, value, value1, value2, value3, temperature,humidity, jodo, takdo
  messagetosend = bytes((''.join([str(x) for x in ['{0}mA\n\n{1}lux\n\n{2:.1f}°C\n\n{3}\n\n{4}°C,{5}%'.format(value,value1,value2,value3,temperature,humidity)]])), "utf")
  self.send_response(200)
  self.send_header('Content-Type', 'text/plain')
  self.end_headers()
  self.wfile.write(messagetosend)
  Request = self.requestline
  Request = Request[5 : int(len(Request)-9)]
  print(Request)     #HTTP 서버 구축 후 앱과의 연동을 위한 함수이며 각각의 지역 변수 지정
      
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

  if Request == 'stop': #자동 모드를 빠져나올시
             GPIO.output(5, 0)
             GPIO.output(6, 0)
             GPIO.output(26, 0)
             GPIO.output(16, 0)
             GPIO.output(20, 0) #전체 모터 동작 정지
            
  if Request == 're' : #어플에서 수동모드 실행시
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
             
  if Request == 'ledon': #어플에서 LED on
            GPIO.output(26, 1)
  if Request == 'ledoff': #어플에서 LED off
            GPIO.output(26, 0) 
  if Request == 'saryoon': #어플에서 사료 모터 on
            GPIO.output(16, 1)
            GPIO.output(20, 0) #모터 동작
            
  if Request == 'saryooff': #어플에서 사료 모터 on
            GPIO.output(16, 0)
            GPIO.output(20, 0) #모터 정지
  if Request == 'takon': #어플에서 물순환 모터 on
            GPIO.output(5, 1)
            GPIO.output(6, 0) #모터 동작
  if Request == 'takoff': #어플에서 물순환 모터 on
            GPIO.output(5, 0)
            GPIO.output(6, 0) #모터 정지
  if Request == 'wtron' : #어플에서 물공급 모터 on
            GPIO.output(13,1)
            GPIO.output(19, 0) #모터 동작
  if Request == 'wtroff' : #어플에서 물공급 모터 off
            GPIO.output(13, 0)
            GPIO.output(19, 0) #모터 정지
  return

server_address_httpd=('0.0.0.0',8000)
httpd = HTTPServer(server_address_httpd, RequestHandler_httpd)
print('starting server')
httpd.serve_forever() #HTTP 서버를 이용한 어플 구동 함수
