import math

brightnessValues = []
logValues = []

for i in range(100):
    brightnessValues.append(i/100)
    logValues.append(math.pow(10, i/100) / 10)
    
#print(brightnessValues)
print(logValues)