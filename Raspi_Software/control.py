import time
import serial
import keyboard  # using module keyboard
               
ser = serial.Serial(            
    port='/dev/serial0',
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)


while True:  # making a loop
    if keyboard.is_pressed('p'):
        ser.write('p'.encode())