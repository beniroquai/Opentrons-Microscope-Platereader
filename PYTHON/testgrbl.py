mport serial 
import time

ser = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=1)
ser.write("\r\n\r\n".encode())# Wake up grbl
time.sleep(2)   # Wait for grbl to initialize 
grbl_out = ser.readline() # Wait for grbl response with carriage return
return_message = (grbl_out.strip()).decode()
ser.flushInput()  # Flush startup text in serial input

ser.write(("?" + '\n').encode())
return_message = ''
#while not b'ok\r\n'==self.serial_xyz.readline():
grbl_out = ser.readline() # Wait for grbl response with carriage return
return_message = (grbl_out.strip()).decode()
print(return_message)
ser.flushInput()  # Flush startup text in serial input

ser.close()