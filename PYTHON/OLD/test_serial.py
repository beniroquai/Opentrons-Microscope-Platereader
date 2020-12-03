import serial
port = '/dev/ttyUSB0'

with serial.Serial(port, 115200, timeout=1) as ser:
	ser.write("\r\n\r\n".encode())
	line = "G20 G91 Y0.109 F25"
	l = line.strip()
	ser.write((l + '\n').encode())
#	ser.write("$G20G91Y0.109F25".encode())
	x = ser.read()          # read one byte
	s = ser.read(10)        # read up to ten bytes (timeout)
	line = ser.readline()   # read a '\n' terminated line
	print(line)
