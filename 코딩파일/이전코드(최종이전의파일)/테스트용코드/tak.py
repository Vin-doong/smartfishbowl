import smbus
import time
import math

address = 0x48
AIN3 = 0x43

bus = smbus.SMBus(1)

try:
    while True:
        bus.write_byte(address,AIN3)
        value=abs((((bus.read_byte(address))/50)))
        value2=math.pow(5,value)
        print("value:{0}".format(value))
        time.sleep(0.1)
        state = value2
        
except KeyboardInterrupt:
    pass
