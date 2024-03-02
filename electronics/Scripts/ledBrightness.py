from machine import Pin, PWM

# Pin 25 for inbuilt LED
pwm = PWM(Pin(25))

# Set frequency in Hz
pwm.freq(100)

# Specify brightness value
brightness = 0.5

pwm.duty_u16(int(brightness * 65025))