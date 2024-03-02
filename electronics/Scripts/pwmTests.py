from machine import Pin, PWM

pwm = PWM(Pin(15))

# Set frequency in Hz
pwm.freq(1000)

pwm.duty_u16(int(0.5 * 65025))