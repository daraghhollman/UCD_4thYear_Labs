from machine import Pin, PWM

pwm = PWM(Pin(15))

# Set frequency in Hz
pwm.freq(10000)

# Set duty value between 0 and 1
dutyValue = 0.5
pwm.duty_u16(round(dutyValue * 65025))