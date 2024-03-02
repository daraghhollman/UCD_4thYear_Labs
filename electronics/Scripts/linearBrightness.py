from machine import Pin, PWM
from time import sleep_ms
import math

# Pin 25 for inbuilt LED
pwm = PWM(Pin(25))

# Set frequency in Hz
pwm.freq(100)

# Initialise brightness value
brightness = 0

# Evenly spaced brightnesses in linear or log space
isLog = True

# specify the cycle length
cycleLength = 4 # seconds

# 200 steps in one cycle, converted to ms. Needs to be an int for sleep_ms() function
delay = round((cycleLength / 200) * 1000)

def GetBrighter(t, b, log=False):
    # Loop 100 points for each cycle

    i = 0
    while i < 101:
        print(f"{b:0.2f}")
        
        pwm.duty_u16(round(b * 65025))
        
        sleep_ms(t)
        
        if log:
            b = math.pow(10, i/100) / 10
        else:
            b += 0.01
        i += 1
    
    return b
        
def GetDimmer(t, b, log=False):
    # Loop 100 points for each cycle
    i = 0
    while i < 101:
        print(f"{b:0.2f}")
        
        pwm.duty_u16(round(b * 65025))
        
        sleep_ms(t)
        
        if log:
            b = math.pow(10, - i/100 + 1) / 10
        else:
            b -= 0.01
        i += 1
    
    return b

while True:
    
    if brightness <= 0.5:
        print("getting brighter")        
        brightness = GetBrighter(delay, brightness, log=isLog)
    
    elif brightness >= 0.5:
        print("getting dimmer")
        brightness = GetDimmer(delay, brightness, log=isLog)
    
    else:
        break