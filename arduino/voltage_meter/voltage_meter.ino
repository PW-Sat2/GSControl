void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT);
}

void loop() {
  Serial.print(analogRead(0));
  Serial.print(" ");
  Serial.print(analogRead(1));
  Serial.print(" ");
  Serial.print(analogRead(2));
  Serial.print(" ");
  Serial.print(analogRead(3));
  Serial.print(" ");
  Serial.print(analogRead(4));
  Serial.print(" ");
  Serial.print(analogRead(5));
  Serial.print(" ");
  Serial.print(analogRead(6));
  Serial.print(" ");
  Serial.println(analogRead(7));

  delay(100);

  digitalWrite(13, !digitalRead(13));
}
