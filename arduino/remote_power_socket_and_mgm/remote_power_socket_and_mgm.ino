#include <RCSwitch.h>

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_HMC5883_U.h>

/* Assign a unique ID to this sensor at the same time */
Adafruit_HMC5883_Unified mag = Adafruit_HMC5883_Unified(12345);
 
RCSwitch mySwitch = RCSwitch();

class RCSocket {
 public:
  enum Switch {
    SW1 = 0,
    SW2 = 1,
    SW3 = 2,
    SW4 = 3
  };

  RCSocket(uint8_t pin, Switch sw_no) {
    this->pin = pin;
    this->sw_no = sw_no;
  }

  void init() {
    this->sw.setPulseLength(197);
    this->sw.enableTransmit(this->pin);
  }

  void on() {
    this->sw.send(this->codesOn[this->sw_no], 24);
  }

  void off() {
    this->sw.send(this->codesOff[this->sw_no], 24);
  }

 private:
  RCSwitch sw;
  uint8_t pin;
  Switch sw_no;
  unsigned long codesOn[4] = {0b000100010101010100110011, 0b000100010101010111000011, 0b000100010101011100000011, 0b000100010101110100000011};
  unsigned long codesOff[4] = {0b000100010101010100111100, 0b000100010101010111001100, 0b000100010101011100001100, 0b000100010101110100001100}; 
};


RCSocket socket_1(10, RCSocket::SW1);
RCSocket socket_2(10, RCSocket::SW2);
RCSocket socket_3(10, RCSocket::SW3);
RCSocket socket_4(10, RCSocket::SW4);

enum class Commands : uint8_t {
  START = 7,
  SW1_ON = 10,
  SW1_OFF = 21,
  SW2_ON = 32,
  SW2_OFF = 43,
  SW3_ON = 54,
  SW3_OFF = 65,
  SW4_ON = 76,
  SW4_OFF = 87,
  STOP = 8
};

void setup() {
  Serial.begin(9600);
  socket_1.init();
  socket_2.init();
  socket_3.init();
  socket_4.init();
  mag.begin();
}

void read_and_execute_switch() {
  if (Serial.available()) {
    unsigned long start_time = millis();
    uint8_t first_byte = Serial.read();

    if (Commands::START == static_cast<Commands>(first_byte)) {
        while (Serial.available() < 2) {
          if (millis() - start_time > 10000) {
            break;
          }
        }
    }
      uint8_t second_byte = Serial.read();
      uint8_t third_byte = Serial.read();

      if (Commands::STOP == static_cast<Commands>(third_byte)) {
          switch (static_cast<Commands>(second_byte)) {
            case Commands::SW1_ON:
              socket_1.on();
            break;
          
            case Commands::SW1_OFF:
              socket_1.off();
            break;
            
            case Commands::SW2_ON:
              socket_2.on();
            break;
            
            case Commands::SW2_OFF:
              socket_2.off();
            break;
          
            case Commands::SW3_ON:
              socket_3.on();
            break;
            
            case Commands::SW3_OFF:
              socket_3.off();
            break;
          
            case Commands::SW4_ON:
              socket_4.on();
            break;
            
            case Commands::SW4_OFF:
              socket_4.off();
            break;
          }
      }
  }
}

void loop() {
  read_and_execute_switch();

  /* Get a new sensor event */ 
  sensors_event_t event; 
  mag.getEvent(&event);
 
  /* Display the results (magnetic vector values are in micro-Tesla (uT)) */
  Serial.print(event.magnetic.x); Serial.print(" ");
  Serial.print(event.magnetic.y); Serial.print(" ");
  Serial.println(event.magnetic.z);
}
