enum PIN {
  LED = 13,
  RELAY_KILL = A2,
  RELAY_RBL = A3
};

enum COMMAND {
  EMPTY = 0,
  HEADER = 0x07,
  RELAY_KILL_ON = 0x15,
  RELAY_KILL_OFF = 0x25,
  RELAY_RBL_ON = 0x32,
  RELAY_RBL_OFF = 0x42,
  TERMINATOR = 0x08,
  WINDOW = 10000
};

uint16_t command_window_ms = COMMAND::WINDOW;
bool command_header_received = false;
COMMAND received_command = COMMAND::EMPTY;

void setup() {
  Serial.begin(9600);

  pinMode(PIN::LED, OUTPUT);
  pinMode(PIN::RELAY_KILL, OUTPUT);
  pinMode(PIN::RELAY_RBL, OUTPUT);
  digitalWrite(PIN::LED, LOW);
  digitalWrite(PIN::RELAY_KILL, LOW);
  digitalWrite(PIN::RELAY_RBL, LOW);
}

void execute_command(COMMAND command_to_execute){
  Serial.print("Executing command 0x");
  Serial.print(command_to_execute, HEX);
  Serial.println("...");

  if(command_to_execute == COMMAND::RELAY_KILL_ON){
    digitalWrite(PIN::RELAY_KILL, HIGH);
    Serial.println("Kill-Switch enabled!");
  }
  else if (command_to_execute == COMMAND::RELAY_KILL_OFF) {
    digitalWrite(PIN::RELAY_KILL, LOW);
    Serial.println("Kill-Switch disabled!");
  }
  else if (command_to_execute == COMMAND::RELAY_RBL_ON) {
    digitalWrite(PIN::RELAY_RBL, HIGH);
    Serial.println("RBL enabled!");
  }
  else if (command_to_execute == COMMAND::RELAY_RBL_OFF) {
    digitalWrite(PIN::RELAY_RBL, LOW);
    Serial.println("Kill-Switch disabled!");
  } else {
    Serial.println("Syntax error or unimplemented command!");
  }
}

void loop() {
  if (Serial.available()) {
    char received_byte = Serial.read();

    if (command_header_received and (received_command == 0)) {
      received_command = received_byte;
      Serial.println("Command received! Waiting for command terminator...");
      received_byte = COMMAND::EMPTY;
    }

    if (received_byte == COMMAND::HEADER) {
      Serial.print("Command header received! Command window time: ");
      Serial.print(COMMAND::WINDOW);
      Serial.println("ms");
      command_header_received = true;
      received_byte = COMMAND::EMPTY;
    }

    if(command_header_received and (received_command > 0) and (received_byte == COMMAND::TERMINATOR)){
      execute_command(received_command);
      command_window_ms = 1;
      received_byte = COMMAND::EMPTY;
    }
  }

  if(command_header_received){
    command_window_ms--;
    digitalWrite(PIN::LED, HIGH);
    if(command_window_ms == 0){
      command_header_received = false;
      command_window_ms = COMMAND::WINDOW;
      received_command = COMMAND::EMPTY;
      Serial.println("Command window expired!");
    }
  } else {
    digitalWrite(PIN::LED, LOW);
  }

  delay(1);
}
