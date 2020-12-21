import time
import serial
import numpy as np

class xyzStepper:
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

    def __init__(self, serial_xyz = "/dev/ttyUSB0", serial_focus = "/dev/ttyUSB1",
                 mycurrentposition=0, backlash=0):

        self.mycurrentposition = mycurrentposition
        self.backlash = backlash
        
        print('Initializing XYZ-stepper')
        self.serial_xyz = serial.Serial('/dev/ttyUSB0',115200) # Open grbl serial port
        self.serial_xyz.write("\r\n\r\n".encode())# Wake up grbl
        time.sleep(1)   # Wait for grbl to initialize 
        self.serial_xyz.flushInput()  # Flush startup text in serial input
        
        print('Initializing Focus Sensor')
        self.serial_focus = serial.Serial("/dev/ttyUSB1", 115200, bytesize=8, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)
        self.serial_focus.flushInput()


    def go_to_z(self, pos_z):
        # Stream g-code to grbl
        line = "M3 S"+str(pos_z)
        l = line.strip() # Strip all EOL characters for consistency
        print( 'Sending: ' + l)
        self.serial_xyz.write((l + '\n').encode()) # Send g-code block to grbl
        grbl_out = self.serial_xyz.readline() # Wait for grbl response with carriage return
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
        self.serial_xyz.write((l + '\n').encode()) # Send g-code block to grbl
        grbl_out = self.serial_xyz.readline() # Wait for grbl response with carriage return
        print( ' : ' + (grbl_out.strip()).decode())

        self.mycurrentposition = (pos_x, pos_y)

#        time.sleep(abs(self.mystepstogo)*.01+.5)

    def reset_pos(self):
        '''
        

        Returns
        -------
        None.

        '''
        print('Reset the position of ' + self.mystepper + '-stepper with backlash; '+str(str(self.backlash)))
        self.mycurrentposition = 0

        print("Setting slow-speed")
        mycmd = 'L'
        self.serial_xyz.write(str.encode(mycmd))
        time.sleep(1)

        if (self.mystepper == 'x'):
            #for ix in range(8):
            print("Resetting X")
            mycmd = 'X' + str(80)
            self.serial_xyz.write(str.encode(mycmd))
            time.sleep(4)

            mycmd = 'x' + str(self.backlash) # backlash

        if (self.mystepper == 'y'):
            #for iy in range(8):
            print("Resetting Y")
            mycmd = 'Y' + str(80)
            self.serial_xyz.write(str.encode(mycmd))
            time.sleep(4)

        # set high speed
        mycmd = 'S'
        self.serial_xyz.write(str.encode(mycmd))
        time.sleep(1)

        mycmd = self.mystepper + str(self.backlash) # backlash
        self.serial_xyz.write(str.encode(mycmd))
        time.sleep(1)



    def find_focus(self, iz_min, iz_max=1024):
        '''
        find_focus will go through z-steps andasks you to find the perceptually 
        best matching focus plane; Hit CTRL+c to stop the focus search
        
        
        Parameters
        ----------
        iz_min : INT
            Minimum search value.
        iz_max : INT, optional
            Maximum serach value. The default is 1024.

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        
        # match focal planes
        iz = iz_min     # this should be outside the loop, I think
        while True:    # infinite loop
            try:
                focuspos,focusval = self.measure_focus()
                print("iz: "+str(iz)+", "+str(focusval))
                
                # move 
                iz +=10
                self.go_to_z(iz)
                time.sleep(.2)
                
                if iz>iz_max:
                    break
            except:
                print("Save the current slice as focus position")
                break
            
        # save them for later
        myfixfocus = focuspos
        myfixz = int(iz)
        
        return myfixfocus, myfixz


    def measure_focus(self):
        '''
        measure the focus which is just coming over the serial..

        Returns
        -------
        focuspos : TYPE
            Value of the focus
        focusval : TYPE
            Intensity of the focus position

        '''
        
        self.serial_focus.flushInput()  # make sure latest line is read
        ser_bytes = self.serial_focus.readline()
        decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
        focuspos = int(decoded_bytes.split("pos: ")[-1])
        focusval = int(decoded_bytes.split("Val: ")[-1].split(" at")[0])
        return focuspos, focusval
          

    def hold_focus(self, aimedfocus, currentz, zstep=3, N_meas=25):
        '''
        

        Parameters
        ----------
        aimedfocus : TYPE, optional
            DESCRIPTION. The default is myfixfocus.
        currentz : TYPE, optional
            DESCRIPTION. The default is iz.
        zstep : TYPE, optional
            DESCRIPTION. The default is 3.

        Returns
        -------
        iz : TYPE
            DESCRIPTION.

        '''
        i_meas = 0
        iz = currentz
        z_step_adapt = zstep
        
        # initially measure the focus value 
        focuspos, focusval = self.measure_focus()
            
        while np.abs(aimedfocus-focuspos)>0:
            # if the distance is positive, the curent sample is too high, hence we 
            # we must move the focus down, which corresponds to an increased iz value
            if (focuspos-aimedfocus)>0:
                iz += (abs((focuspos-aimedfocus))*2)**2
                
            else:
                iz -= (abs((focuspos-aimedfocus))*2)**2
            self.go_to_z(iz)
            time.sleep(.1)
            
            focuspos, focusval = self.measure_focus()
            print("Focus pos (should): "+str(aimedfocus)+", Focus pos (is):"+str(focuspos))
                
            if i_meas > N_meas:
                print("Max number of search iterations reached, taking old value")
                # revert back to old values
                iz = currentz
                self.go_to_z(iz)
                
                break
            i_meas += 1
            
        return iz
    