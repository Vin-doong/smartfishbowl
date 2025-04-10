import I2C_LCD_driver
import time
import os
import RPi.GPIO as GPIO
import smbus
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
import threading #시간,os,GPIO,smbus 등 라즈베리파이 연결을 위한 라이브러리
from flask import Flask, request, jsonify, render_template, Response #WAS서버 생성 라이브러리
from werkzeug.utils import redirect #FLASK에서 URL 파싱해서 이동시켜주는거
import Adafruit_DHT
from PIL import ImageFont, ImageDraw, Image
import datetime
from picamera2 import Picamera2
import numpy as np
import cv2
from time import sleep

app = Flask(__name__)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT) #물순환모터
GPIO.setup(6, GPIO.OUT) #물순환모터
GPIO.setup(13, GPIO.OUT) #물공급(수중)모터
GPIO.setup(19, GPIO.OUT) #물공급(수중)모터
GPIO.setup(26, GPIO.OUT) #LED
servo_pin = 21
GPIO.setup(servo_pin, GPIO.OUT)
GPIO.setwarnings(False)  #모터 구동을 위한GPIO 핀번호 배치 및 설치

servo_pwm = GPIO.PWM(servo_pin, 50)
servo_pwm.start(6.0)

motor_pwm_pin_2 = 5 # 물순환모터 회전속도 조절 
GPIO.setup(motor_pwm_pin_2, GPIO.OUT)
motor_pwm_2 = GPIO.PWM(motor_pwm_pin_2, 1000)
motor_pwm_pin_3 = 13 # 물공급모터 회전속도 조절 
GPIO.setup(motor_pwm_pin_3, GPIO.OUT)
motor_pwm_3 = GPIO.PWM(motor_pwm_pin_3, 1000)

def set_motor_speed_2(speed):
    motor_pwm_2.start(speed)
def set_motor_speed_3(speed):
    motor_pwm_3.start(speed)
#모터 속도제어

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 25  # DHT 센서가 연결된 GPIO 핀 번호입니다.

temp_sensor='/sys/bus/w1/devices/28-fdd4451f64ff/w1_slave' #수온 센서 구동 위치 지정, GPIO 4
address=0x48 #pcf8591
AIN2=0x42 #수위센서
AIN3=0x43 #탁도센서
AIN0 = 0x40 #조도센서
value = 0 #수위
value1 = 0 #수온
value2 = 0 #조도
value3 = 0 #탁도
value4 = 0 #온습도
jodo=0 #조도
takdo=0 #탁도
suwui=0 #수위

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
        time.sleep(10)  # 10초마다 온습도 값을 업데이트
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
        return temp_c      #수온 센서 읽어온 파일의 구문을 분석해 온도부분을 반환하는 함수
   

# Picamera2 객체 생성
piCam = Picamera2()

# 미리보기 설정: 크기 640x480
piCam.preview_configuration.main.size = (640, 480)
piCam.preview_configuration.main.format = "RGB888"
piCam.preview_configuration.align()

# 카메라 시작
piCam.start()

font = ImageFont.truetype('fonts/SCDream6.otf', 20)

def gen_frames():  
    while True:
        now = datetime.datetime.now()
        nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
        frame = piCam.capture_array()  # 현재 프레임을 캡처

        frame = Image.fromarray(frame)
        draw = ImageDraw.Draw(frame)
        draw.text(xy=(10, 15), text="스마트어항 " + nowDatetime, font=font, fill=(255, 255, 255))
        frame = np.array(frame)
        
        ref, buffer = cv2.imencode('.jpg', frame)            
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # 그림파일들을 쌓아두고 호출을 기다림

@app.route('/')
def index():
    global value, value1, value2, value3, temperature, humidity, jodo, takdo, suwui

    # 센서 데이터를 필요한 대로 읽고 수집합니다.
    messagetosend = ''.join([str(x) for x in ['{0}mA\n\n{1}lux\n\n{2:.1f}°C\n\n{3}\n\n{4}°C, {5}%'.format(value,value1,value2,value3,temperature,humidity)]])
    return messagetosend

@app.route('/jadong', methods=['GET'])
def jadong():
    global value, value1, value2, value3, temperature, humidity, jodo, takdo, suwui
    #어플에서 자동모드 실행시
    mylcd.clear()#LCD에 남는 잔상 정리
    bus.write_byte(address, AIN2)
    bus.read_byte(address)
    lvwater=bus.read_byte(address) 
    print("value:%d" %lvwater) #수위센서 값 받아와서 화면에 출력
    bus.write_byte(address,AIN0)
    bus.read_byte(address)
    llux=bus.read_byte(address)
    print(":{0}".format(llux)) #조도센서 값 받아와서 화면에 출력
    watertemp = read_temp() #수온센서 변수 지정
    bus.write_byte(address,AIN3)
    bus.read_byte(address)
    pol=bus.read_byte(address)
    print(":{0}".format(pol)) #탁도센서 값 받아와서 화면에 출력
    if humidity is not None and temperature is not None:
        print("온도={0:0.1f}°C 습도={1:0.1f}%".format(temperature, humidity)) #온습도 센서 값 출력
    #read_dht_sensor()
    mylcd.lcd_display_string("{0:.1f}C / {1:.1f}mA".format(watertemp, lvwater),1)
    mylcd.lcd_display_string("{0}Lux / NTU={1:.1f}".format(llux, pol),2) #LCD에 수온, 수위, 조도, 탁도 센서값 출력
#탁도, 조도, 수위센서값은 환경에 따라 조절해서 사용하세요.   
    if pol < 60:
        if takdo != 1:
            GPIO.output(5,1)            
            set_motor_speed_2(40)
            takdo = 1   
    elif pol > 80:
        if takdo == 1:
            GPIO.output(5,0)
            motor_pwm_2.stop()
            takdo = 0 #탁도센서 범위를 임의로 지정하여 물순환 모터 구동 함수
    if llux > 228: 
        if jodo != 1:
            GPIO.output(26, 1)
            jodo = 1
    elif llux < 224: 
        if jodo == 1:
            GPIO.output(26, 0)
            jodo = 0 #조도센서 범위를 임의로 지정하여 LED 구동 함수
    if lvwater < 10:
        if suwui != 1:
            GPIO.output(13, 1)
            set_motor_speed_3(50)
            suwui = 1
    elif lvwater > 50:
        if suwui == 1:
            GPIO.output(13, 0)
            motor_pwm_3.stop()
            suwui = 0 # 수위센서 범위를 임의로 지정하여 물순환 모터 구동 함수
    return redirect('/')                
@app.route('/stop', methods=['GET'])
def stop():

    GPIO.output(5, 0)
    GPIO.output(6, 0)
    GPIO.output(13, 0)
    GPIO.output(19, 0) 
    GPIO.output(26, 0)#모든 GPIO에 연결된 모터, LED 정지
    motor_pwm_2.stop()
    motor_pwm_3.stop()
    #자동 모드에서 나왔을 시 다시 자동모드가 작동 할 수 있게 초기화
    global value, value1, value2, value3, temperature, humidity, jodo, takdo, suwui
    value = 0
    value1 = 0
    value2 = 0
    value3 = 0
    temperature = 0
    humidity = 0
    jodo = 0
    takdo = 0
    suwui = 0
    return redirect('/')

@app.route('/re', methods=['GET'])
def re():
    global value, value1, value2, value3, temperature, humidity, jodo, takdo, suwui        
    mylcd.clear()#LCD에 남는 잔상 정리
    bus.write_byte(address, AIN2)
    bus.read_byte(address)
    value=bus.read_byte(address)
    print("value:%d"%value) #수위센서 값 받아와서 화면에 출력
    bus.write_byte(address,AIN0)
    bus.read_byte(address)
    value1=bus.read_byte(address)
    print(":{0}".format(value1)) #조도센서 값 받아와서 화면에 출력
    value2 = read_temp()
    print(value2) #수온센서 값 받아와서 화면에 출력
    bus.write_byte(address,AIN3)
    bus.read_byte(address)
    value3=abs((bus.read_byte(address)))
    print("value:{0}".format(value3)) #탁도센서 값 받아와서 화면에 출력
    if humidity is not None and temperature is not None:
       print("온도={0:0.1f}°C 습도={1:0.1f}%".format(temperature, humidity)) #온습도 센서 값 출력
    mylcd.lcd_display_string("{0:.1f}C / {1:.1f}mA".format(value2, value),1)
    mylcd.lcd_display_string("{0}Lux / NTU={1:.1f}".format(value1, value3),2) #LCD에 수온, 수위, 조도, 탁도 센서값 출력
    return redirect('/')

@app.route('/ledon', methods=['GET'])
def ledon():     #어플에서 LED on
    
    GPIO.output(26, 1)
    return redirect('/')
@app.route('/ledoff', methods=['GET'])
def ledoff():   #어플에서 LED off
    
    GPIO.output(26, 0)
    return redirect('/') 
@app.route('/saryoon', methods=['GET'])
def saryon():  #어플에서 사료 모터 on
    servo_pwm.ChangeDutyCycle(3.5)   
    time.sleep(1.0)            
    servo_pwm.ChangeDutyCycle(6.0)
    sleep(1)
    return redirect('/')

@app.route('/takon', methods=['GET'])
def takon(): #어플에서 물순환 모터 on
        
    GPIO.output(5, 1)
    GPIO.output(6, 0) #모터 동작
    set_motor_speed_2(40)
    return redirect('/')
@app.route('/takoff', methods=['GET'])
def takoff(): #어플에서 물순환 모터 off
    
    GPIO.output(5, 0)
    GPIO.output(6, 0) #모터 정지
    motor_pwm_2.stop()
    return redirect('/')
@app.route('/wtron', methods=['GET'])
def wtron(): #어플에서 물공급 모터 on
    
    GPIO.output(13, 1)
    GPIO.output(19, 0) #모터 동작
    set_motor_speed_3(70)
    return redirect('/')
@app.route('/wtroff', methods=['GET'])
def wtroff(): #어플에서 물공급 모터 off
        
    GPIO.output(13, 0)
    GPIO.output(19, 0) #모터 정지
    motor_pwm_3.stop()
    return redirect('/')
#cctv 코드
@app.route('/video')
def index2():
    return render_template('index4#2.html')  # index4#2.html 템플릿을 렌더링하여 웹 페이지 반환

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8000")
