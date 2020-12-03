import serial
import time

# Open grbl serial port
s = serial.Serial('/dev/ttyUSB0',115200)

# Open g-code file
f = open('test.gcode','r')

# Wake up grbl
s.write("\r\n\r\n".encode())
time.sleep(2)   # Wait for grbl to initialize 
s.flushInput()  # Flush startup text in serial input

# Stream g-code to grbl
for i in range(1):# line in f:
    line = "G20 G91 X-.2 Y0.109 F25"
    print(line)
    l = line.strip() # Strip all EOL characters for consistency
    print( 'Sending: ' + l)
    s.write((l + '\n').encode()) # Send g-code block to grbl
    grbl_out = s.readline() # Wait for grbl response with carriage return
    print( ' : ' + (grbl_out.strip()).decode())

# Wait here until grbl is finished to close serial port and file.
input("  Press <Enter> to exit and disable grbl.") 

# Close file and serial port
f.close()
s.close()
