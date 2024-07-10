import RPi.GPIO as GPIO
import datetime
import time

init = False
GPIO.setmode(GPIO.BCM) # Change to BCM

def get_last_watered():
    try:
        with open("last_watered.txt", "r") as f:
            return f.readline()
    except FileNotFoundError:
        return "NEVER!"

def get_status(pin=21):  # Change to BCM 21
    GPIO.setup(pin, GPIO.IN) 
    return GPIO.input(pin)

def init_output(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    GPIO.output(pin, GPIO.HIGH)

def auto_water(delay=5, pump_pin=4, water_sensor_pin=21):  # Change to BCM 4
    consecutive_water_count = 0
    init_output(pump_pin)
    print("Here we go! Press CTRL+C to exit")
    try:
        while consecutive_water_count < 10:
            time.sleep(delay)
            wet = get_status(pin=water_sensor_pin) == 0
            if not wet:
                if consecutive_water_count < 5:
                    pump_on(pump_pin, 1)
                consecutive_water_count += 1
            else:
                consecutive_water_count = 0
    except KeyboardInterrupt:
        GPIO.cleanup()

def pump_on(pump_pin=4, delay=1):  # Change to BCM 4
    init_output(pump_pin)
    with open("last_watered.txt", "w") as f:
        f.write(f"Last watered {datetime.datetime.now()}")
    GPIO.output(pump_pin, GPIO.LOW)
    time.sleep(delay)
    GPIO.output(pump_pin, GPIO.HIGH)

if __name__ == "__main__":
    auto_water()
