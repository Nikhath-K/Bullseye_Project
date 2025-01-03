from gpiozero import LED
from time import sleep

# Define the GPIO pin where the LED is connected
led = LED(17)  # GPIO 17

try:
    while True:
        led.on()   # Turn LED on
        print("LED ON")
        sleep(1)   # Wait for 1 second
        led.off()  # Turn LED off
        print("LED OFF")
        sleep(1)   # Wait for 1 second
except KeyboardInterrupt:
    print("Exiting program...")
