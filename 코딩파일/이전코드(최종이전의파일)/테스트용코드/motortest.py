from gpiozero import Motor
from time import sleep

# 모터 핀 세팅.
motorR = Motor(forward=5,backward=6) # 오른쪽 모터 객체 생성. (그림에서 A 방향)
motorL = Motor(forward=16,backward=20) # 왼쪽 모터 객체 생성. (그림에서 B 방향)

# speed 변수에 0~1 사이의 값을 넣어서 속도를 조절할 수 있다. 수가 클수록 빠르다.
# 3초 동안 전진
motorR.forward(speed=0.1)
motorL.forward(speed=0.1)
sleep(3)

# 3초 동안 후진
motorR.backward(speed=0.1)
motorL.backward(speed=0.1)
sleep(3)

# 3초 동안 좌회전
motorR.forward(speed=0.7)
motorL.backward(speed=0.7)
sleep(3)

# 3초 동안 우회전
motorR.backward(speed=0.7)
motorL.forward(speed=0.7)
sleep(3)

# 양쪽 모터 정지.
motorR.stop()
motorL.stop()
