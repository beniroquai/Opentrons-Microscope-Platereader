// Include the AccelStepper Library
#include <AccelStepper.h>

// Define pin connections
const int dirPin = 7;
const int stepPin = 4;


// Define pin connections
const int dirPinZ = 7;
const int stepPinZ = 4;
const int dirPinX = 5;
const int stepPinX = 2;


#define enablePin 8

// Define motor interface type
#define motorInterfaceType 1

// Creates an instance
AccelStepper stepperX(motorInterfaceType, stepPin, dirPin);

void setup() {
     pinMode(enablePin, OUTPUT);
   digitalWrite(enablePin, LOW);
   
  // set the maximum speed, acceleration factor,
  // initial speed and the target position
  stepperX.setMaxSpeed(8000);
  stepperX.setAcceleration(1000);
  stepperX.setSpeed(4000);
  stepperX.moveTo(0);
}

void loop() {
  // Change direction once the motor reaches target position
  if (stepperX.distanceToGo() == 0) 
    stepperX.moveTo(-stepperX.currentPosition());

  // Move the motor one step
  stepperX.run();
}
