import time
import serial
import keyboard
               
ser = serial.Serial(            
    port='/dev/serial0',
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

while True:
    if keyboard.read_key() == "p":
        print("You pressed p")
        break
#ser.write('p'.encode())