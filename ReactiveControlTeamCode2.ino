//All inclusions of necessary Header files and libraries
#include "Arduino.h"
#include "Internal_DHT22_Sensor.h"
#include "Servo_Control.h"
#include "SD_Card.h"
#include "Fan_Control.h"
#include "External_SHT30_Sensor.h"
#include "Irradiance_Sensor.h"
#include "LCD.h"
//Test
//ALL COMBINED CODE FOR TH SOLAR CROP DRYER

/*PLUG IN SD CARD PINS OR CODE WILL NOT RUN BECAUSE OF THE SD CARD SETUP FUNCTION*/


/* PINS NOT USED IN MAIN FUCTION BUT FOR FUNCTIONALITY
 External_SHT30_PIN SDA - 0 / SCL - 1
 FAN_PIN 13
 SERVO_PIN 12
 DHT22_PIN 8
 irradiance_pin 28
***********************************
LCD SCREEN PINS:
 TFT_CS     5   // Chip Select (CS)
 TFT_DC     6   // Data Command (DC)
 TFT_MOSI   3   // SPI MOSI (DIN)
 TFT_CLK    2   // SPI Clock (CLK)
 TFT_RST    4   // Reset (RST)

//SD card attached to SPI bus as follows:
  MOSI - pin 19
  MISO - pin 16
  CLK - pin 18
  CS - pin 17

//USER INPUT PINS
  POTENTIOMETER_PIN_1  27
  POTENTIOMETER_PIN_2  26 
  BUTTON_PIN  21
 */


//USER INPUT PINS
//Setting the pins for the potentiometers and button
#define POTENTIOMETER_PIN_1  27
#define POTENTIOMETER_PIN_2  26 
#define BUTTON_PIN  21

//Variables to hold the temperature and humidity etc
float irradiance_value = 0, external_Temp=7, external_Humidity=8, internal_Temp=9, internal_Humidity=10;
int fan_Speed= 80, outlet_Opening=10;
int timer =0; // central "clock" in which we determine how often events happen
int state = -4; // determines which "state" or mode we are in, determines which "window" is displayed on the LCD



//variables to keep track of the timing of recent interrupts
unsigned long button_time = 0;  
unsigned long last_button_time = 0;
int buttonState = 0;  // Current button state
int lastButtonState = 0;
unsigned long lastDebounceTime = 0;  // The last time the button was toggled
unsigned long debounceDelay = 50;  // The debounce time; increase if the button is noisy

// Variables to count time passed for other operations
int time_1 = 0;
int time_2 = 0;
bool interval = false;
int potenValue = 0; // potentiometer value
int potentiometer_variable=0;
int year_value=2025;
int month_value=1;
int day_value=1;

//Count and Boolean Variables for automated testing
int fanCount=0;
int outletCount=0;
bool outletSweep=true;
bool fanSweep=false;

void isr(){ // this debounces and checks for button selection.
  button_time = millis();
  if (button_time - last_button_time > 250)
  {
      state = state+1;
      if(state == 3){
        state = 0;
      }
      last_button_time = button_time;
  }
}

void setup() {
  //Starting the serial monitor at a baud rate of 9600
  Serial.begin(9600);
  //*******************************************
  // setup for the SERVO
  servo_Setup();
  //*******************************************
  //Stating the read resolution for the irradiance sensor
  irradiance_Setup();
  //*******************************************
  // intializing the SHT30 and DHT22 sensor
  setup_External_SHT30();
  setup_Internal_DHT22();//Starting the DHT22
  //*******************************************
  //LCD SETUP FUNCTION
  LCDStart();
  //*******************************************
  //Setting up the fan speed function
  Fan_setup();
  //*******************************************
  pinMode(BUTTON_PIN, INPUT_PULLDOWN);
  attachInterrupt(BUTTON_PIN, isr, FALLING); // creates interrupt
}

void autonomusly_Set_Actuators(int fan, int outlet){ // this sets the actuators to whatever values we want.
  //Changing the fan speed and Outlet size based on values passed in
  autonomus_fan_control(fan);
  autonomus_servo_control(outlet);
}

void logData()
{
  //*********Updating the SD Card with the data*************
  data_Log(external_Humidity, external_Temp, internal_Humidity, internal_Temp, irradiance_value, fan_Speed, outlet_Opening);
}

void update_LCD_Variables(){ // gathers and logs and updates LCD with data
  //*********Reading the DHT22 and SHT30 sensors*****************
  temp_and_humidity_Internal_read_DHT22(internal_Humidity, internal_Temp);
  temp_and_humidity_External_read30(external_Humidity, external_Temp);
  //*********Reading the Irradiance sensor*************
  measure_Irradiance(irradiance_value);
  //********* Update the LCD and current file's globals with new data
  UpdateLCDValues(fan_Speed,outlet_Opening,external_Temp,internal_Temp,external_Humidity,internal_Humidity,irradiance_value);
}

//A function that reads the value of potentiometer 1 to use for setting year, month, and day
void read_Potentiometer_1(int &potentiometer_value)
{
  potentiometer_value = analogRead(POTENTIOMETER_PIN_1);
      if(potentiometer_value <20)
        potentiometer_value = 20;
      if(potentiometer_value>4050)
        potentiometer_value = 4050;
}


// Function to get target fan speed based on temperature and irradiance
int getTargetFanSpeed(float temperature, float irradiance) {
    if (irradiance >= 1800) irradiance = 1800;
    if (temperature >= 105) temperature = 105;
    if (temperature <= 60) temperature = 60;
    
    int tempIndex = (temperature - 60) / 5;  // Temperature index (60°F to 105°F)
    int irrIndex = irradiance / 200;         // Irradiance index (200W/m² to 1800W/m²)
    
    const int fanSpeedMap[9][10] = {
        {50, 52, 55, 57, 60, 62, 65, 67, 70, 75},
        {55, 57, 60, 62, 65, 67, 70, 72, 75, 80},
        {60, 62, 65, 67, 70, 72, 75, 77, 80, 85},
        {65, 67, 70, 72, 75, 77, 80, 82, 85, 90},
        {70, 72, 75, 77, 80, 82, 85, 87, 90, 95},
        {75, 77, 80, 82, 85, 87, 90, 92, 95, 100},
        {80, 82, 85, 87, 90, 92, 95, 97, 100, 100},
        {85, 87, 90, 92, 95, 97, 100, 100, 100, 100},
        {90, 92, 95, 97, 100, 100, 100, 100, 100, 100}
    };
    return fanSpeedMap[irrIndex][tempIndex];
}

// Function to get target orifice opening based on temperature and irradiance
int getTargetOrificeOpening(float temperature, float irradiance) {
    if (irradiance >= 1800) irradiance = 1800;
    if (temperature >= 105) temperature = 105;
    if (temperature <= 60) temperature = 60;
    
    int tempIndex = (temperature - 60) / 5;
    int irrIndex = irradiance / 200;
    
    const int orificeMap[9][10] = {
        {20, 25, 30, 35, 40, 45, 50, 55, 60, 65},
        {25, 30, 35, 40, 45, 50, 55, 60, 65, 70},
        {30, 35, 40, 45, 50, 55, 60, 65, 70, 75},
        {35, 40, 45, 50, 55, 60, 65, 70, 75, 80},
        {40, 45, 50, 55, 60, 65, 70, 75, 80, 85},
        {45, 50, 55, 60, 65, 70, 75, 80, 85, 90},
        {50, 55, 60, 65, 70, 75, 80, 85, 90, 95},
        {55, 60, 65, 70, 75, 80, 85, 90, 95, 100},
        {60, 65, 70, 75, 80, 85, 90, 95, 100, 100}
    };
    return orificeMap[irrIndex][tempIndex];
}



void loop() {
  time_1 = millis();
  // 4 seconds in which we do some operation, I think the switch statement will act more as a set parameters
  // that we will act upon every 4 seconds, so for example, setting the state tells the following function what GUI to show. Separate logic and timing
  if (time_1 - time_2 > 1000) 
  {             
    time_2 = time_1;
    interval = true;
    update_LCD_Variables();
    //Print stuff
    Serial.print("Case: ");
    Serial.println(state);
    Serial.print("ButtonPress: ");
    Serial.println(digitalRead(BUTTON_PIN));
    Serial.print("Poten 1: ");
    Serial.println(analogRead(POTENTIOMETER_PIN_1));
    Serial.print("Poten 2: ");
    Serial.println(analogRead(POTENTIOMETER_PIN_2));
  }
  else{
    interval = false;
  }
  switch(state)
  {
      /*
        Notice that the interrupt resets the case value to 0, not -3.
        So, the states -3 to -1 will only "run once", and are reset 
        only when the program is re run. 
        Example: User starts it, case =-3, user sets year, button press
        goes to -2, user sets month, etc... now case is equal to 2, 
        button press resets to 0, so that cases -3 to -1 never get 
        revisited. 
        */
    
    case -4:
    {
      // this is the set year 
      //Reading the potentiometer value from potentiometer 1
      read_Potentiometer_1(potentiometer_variable);
      potentiometer_variable = map(potentiometer_variable,20,4050,2025,2030);
      year_value=potentiometer_variable;
      if(interval)
      { 
        Intro_Set(1, year_value, month_value, day_value);// sets GUI page
        setYear(potentiometer_variable);
      }
      //setGUI(#some number corresponding to the year GUI);
      break;
    }
    case -3:
    {
      // this is the set month
      // the potentiometer value from potentiometer 1
      read_Potentiometer_1(potentiometer_variable);
      potentiometer_variable = map(potentiometer_variable,20,4050,1,12);
      month_value=potentiometer_variable;
      if(interval)
      {
        Intro_Set(2, year_value, month_value, day_value); // sets GUI page
        setMonth(potentiometer_variable);
      }
      break;
    }
    case -2: 
    {
      // this is the set day
      // the potentiometer value from potentiometer 1
      read_Potentiometer_1(potentiometer_variable);
      potentiometer_variable = map(potentiometer_variable,20,4050,1,31);
      day_value=potentiometer_variable;
      if(interval)
      {
        Intro_Set(3, year_value, month_value, day_value); // sets GUI page
        setDay(potentiometer_variable);
      }
      break;
    }
    case -1:
    {
      //*******************************************
      //Setup for the SD CARD in order to data log
      //Starting the SD card after date has been set by user
      SD_setup();
      //*******************************************
      state=0;
      break;
    }
    case 0:
    {
      // automatic - do all automatic stuff
      //Serial.println("Automatic");
      if(interval){ // 1 second interval
        //SETTING THE FAN SPEED TO A CERTAIN SPEED FOR 30 MINUTES WHILE HOLDING THE SERVO ANGLE CONSTANT
        fanCount++;
        if(fanCount==1800){
          fanCount=0;
          if(!fanSweep){
            if(fan_Speed<100){
              fan_Speed+=5;
            }
            else{
              fanSweep=true;
            }
          }
          else{
            if(fan_Speed>50){
              fan_Speed-=5;
            }
            else{
              fanSweep=false;
            }
          }
        }
        logData(); // logs datg 
        Serial.println("in auto");
        automaticGUI(); // runs the automaticGI window
        autonomusly_Set_Actuators(fan_Speed, outlet_Opening);
      }
    break;
    }
    case 1: // manuel mode - only in this state do analog reads work 4 poteniometer
    {
      // manuel viewing (you can see the values that you have set, but you can't set them)
      //Serial.println("Manual");
      int fan_value =analogRead(POTENTIOMETER_PIN_1); // from poteniometer pin 
      int servo_value =analogRead(POTENTIOMETER_PIN_2); // from poteniometer pin 
      if(fan_value <20)
        fan_value = 20;
      if(fan_value>4050)
        fan_value = 4050;
      if(servo_value<20)
        servo_value =20;
      if(servo_value>4050)
        servo_value =4050;
      fan_Speed = map(fan_value, 20, 4050, 0, 100);  // To percentage 
      outlet_Opening = map(servo_value, 20, 4050, 0, 40);  // To percentage              

      if(interval){ // 4 second interval
        logData(); // logs datg 
        manualGUI(); // runs the automaticGUI window
        autonomusly_Set_Actuators(fan_Speed, outlet_Opening);
      }
      break;
    }
    // predictive
    case 2:
    {
      
      float internalTemperature, internalHumidity;
      float irradiance;
      
      // Read sensors
      temp_and_humidity_Internal_read_DHT22(internalHumidity, internalTemperature);
      measure_Irradiance(irradiance);
      
      // Get target fan speed and orifice opening
      fan_Speed = getTargetFanSpeed(internalTemperature, irradiance);
      outlet_Opening = getTargetOrificeOpening(internalTemperature, irradiance);

      // Logging data
      logData();
      automaticGUI();
      
      // Apply values to actuators
      autonomusly_Set_Actuators(fan_Speed, outlet_Opening);
      
      
      Serial.print("Fan Speed: "); Serial.print(fan_Speed);
      Serial.print("% | Orifice Opening: "); Serial.print(outlet_Opening);
      Serial.println("%");


    break;
    }
  }
}
