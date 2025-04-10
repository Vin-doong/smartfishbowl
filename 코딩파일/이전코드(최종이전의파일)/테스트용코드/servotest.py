### 【 라즈이노 IoT 】
### (실습 3-2) 서보모터 각도 조절해 보기 (0~>180도 까지만 1%씩 움직이기 x 3회)
### 학습 자료 제공 페이지 : Rasino.tistory.com/341
# 서보는 PWM을 20ms(50hz) 주기로 동작시키고 펄스 폭(duty)만 조절해 위치(각도)를 조절함.
# 여기서 duty는 1주기 동안 High를 유지하는 기간이며, 
# 20ms 주기에 100% 면 20ms가 되는 것이고 10% 면 2ms 5% 면 1ms가 됨.
# 펄스 폭은 1ms 일때 0도 2ms 일때 180도, 중간값 1.5ms 일때 90도로 이동함.
# 단, 저렴한 서보는 3%~12%(0도~180도)의 동작 특성을 가짐.
# 만약 모터가 떨린다면, 이 범위를 벗어났기 때문이며, 0도에서 떨린다면
# 3%값에서 조금 올려주고, 180도에서 떨린다면 12%에서 값을 조금 내려주면 됨.
import RPi.GPIO as GPIO
import time

servo_pin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin,GPIO.OUT)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(3.0)

for i in range (0,3) :    
    for high_time in range (30, 125):
        pwm.ChangeDutyCycle(high_time/10.0) # for 반복문에 실수가 올 수 없으므로 /10.0 로 처리함. 
        time.sleep(0.02)
    
    pwm.ChangeDutyCycle(3.0)    
    time.sleep(1.0)
    
pwm.ChangeDutyCycle(0.0)
pwm.stop()
GPIO.cleanup()
