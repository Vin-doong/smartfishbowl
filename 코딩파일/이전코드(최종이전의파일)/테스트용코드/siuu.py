import time

sensor_id = "28-fdd4451f64ff/w1_slave"

def read_temperature():
    try:
        sensor_path = f"/sys/bus/w1/devices/{sensor_id}/w1_slave"
        
        with open(sensor_path, "r") as sensor_file:
            lines = sensor_file.readlines()
            
        temperature_line = lines[1].strip()
        temperature_date = temperature_line.split(" ")[9]
        temperature = float(temperature_date[2:]) / 1000.0
        
        return temperature
    
    except Exception as e:
        print("Error reading temperature:", e)
        return None
        
while True:
    temperature = read_temperature()
    if temperature is not None:
        print("Temperature : {: .2f} C".format(temperature))
    time.sleep(1)
