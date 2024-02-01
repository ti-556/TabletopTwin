import serial
import time
import random

ser = serial.Serial("COM4", 9600, timeout = None)
time.sleep(2.0)

value1 = 7500
value2 = 7500
value3 = 7500
value4 = 7500
value5 = 7500
value6 = 7500
value7 = 7500
value8 = 7500
ser.write(bytes(f"{value1},{value2},{value3},{value4},{value5},{value6},{value7},{value8}\n", "utf-8"))
time.sleep(0.5)
    
ser.close()