import RPi.GPIO as GPIO
import time
import sys

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Get pin number from command-line argument
if len(sys.argv) < 2:
    print("Please provide a pin number as an argument.")
    sys.exit(1)

pin_number = int(sys.argv[1])

# Set up pin as output
GPIO.setup(pin_number, GPIO.OUT)

try:
    while True:
        # Toggle the pin state
        GPIO.output(pin_number, GPIO.HIGH)
        print(f"Pin {pin_number} set to HIGH")
        time.sleep(1)
        
        GPIO.output(pin_number, GPIO.LOW)
        print(f"Pin {pin_number} set to LOW")
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting program")
    GPIO.cleanup()
