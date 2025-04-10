import RPi.GPIO as GPIO
import time

# GPIO 핀 모드 설정
led_pin = 23  # 사용할 GPIO 핀 번호
GPIO.setmode(GPIO.BCM)  # BCM 핀 번호 사용
GPIO.setup(led_pin, GPIO.OUT)  # 출력 모드로 설정

def turn_on_led():
    GPIO.output(led_pin, GPIO.HIGH)  # LED 켜기
    print("LED 켜짐")

def turn_off_led():
    GPIO.output(led_pin, GPIO.LOW)  # LED 끄기
    print("LED 꺼짐")

try:
    while True:
        turn_on_led()  # LED 켜기
        time.sleep(1)  # 1초 대기
        turn_off_led()  # LED 끄기
        time.sleep(1)  # 1초 대기

except KeyboardInterrupt:
    GPIO.cleanup()  # 프로그램 종료 시 GPIO 초기화
