import time
import serial

class xyStepper:
    mycurrentposition = 0
    max_steps = 100
    mystepper = 'x'
    backlash = 0
    highspeed = 2500
    lowspeed = 2500
    '''
    X -> backwards
    x -> forwards
    '''

    def __init__(self, myserial, mycurrentposition=0, mystepper='x', backlash=0):
        self.mycurrentposition = mycurrentposition
        self.mystepper = mystepper
        self.myserial = serial.Serial('/dev/ttyUSB0',115200) # Open grbl serial port
        self.backlash = backlash
        print('Initializing XY-stepper: ' + self.mystepper)
        
        # Wake up grbl
        self.myserial.write("\r\n\r\n".encode())
        time.sleep(1)   # Wait for grbl to initialize 
        self.myserial.flushInput()  # Flush startup text in serial input


    def go_to_z(self, pos_z):
        # Stream g-code to grbl
        line = "M3 S"+str(pos_z)
        l = line.strip() # Strip all EOL characters for consistency
        print( 'Sending: ' + l)
        self.myserial.write((l + '\n').encode()) # Send g-code block to grbl
        grbl_out = self.myserial.readline() # Wait for grbl response with carriage return
        print( ' : ' + (grbl_out.strip()).decode())

    def go_to(self, pos_x, pos_y):
 #       self.mystepstogo = (pos_x, pos_y)-self.mycurrentposition        
        # Stream g-code to grbl
        g_dim = "G20"
        g_dist = "G90" # G91 is for incremental, G90 is for absolute distance
        g_x = "X"+str(pos_x)
        g_y = "Y"+str(pos_y)
        g_speed = "F25"
        line = g_dim + " " + g_dist + " "  + g_x + " " + g_y + " " + g_speed
        l = line.strip() # Strip all EOL characters for consistency
        print( 'Sending: ' + l)
        self.myserial.write((l + '\n').encode()) # Send g-code block to grbl
        grbl_out = self.myserial.readline() # Wait for grbl response with carriage return
        print( ' : ' + (grbl_out.strip()).decode())

        self.mycurrentposition = (pos_x, pos_y)

#        time.sleep(abs(self.mystepstogo)*.01+.5)

    def reset_pos(self):
        print('Reset the position of ' + self.mystepper + '-stepper with backlash; '+str(str(self.backlash)))
        self.mycurrentposition = 0

        print("Setting slow-speed")
        mycmd = 'L'
        self.myserial.write(str.encode(mycmd))
        time.sleep(1)

        if (self.mystepper == 'x'):
            #for ix in range(8):
            print("Resetting X")
            mycmd = 'X' + str(80)
            self.myserial.write(str.encode(mycmd))
            time.sleep(4)

            mycmd = 'x' + str(self.backlash) # backlash

        if (self.mystepper == 'y'):
            #for iy in range(8):
            print("Resetting Y")
            mycmd = 'Y' + str(80)
            self.myserial.write(str.encode(mycmd))
            time.sleep(4)

        # set high speed
        mycmd = 'S'
        self.myserial.write(str.encode(mycmd))
        time.sleep(1)

        mycmd = self.mystepper + str(self.backlash) # backlash
        self.myserial.write(str.encode(mycmd))
        time.sleep(1)


