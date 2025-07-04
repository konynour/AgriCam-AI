void setup() {
  Serial.begin(115200);  // Must match Python baudrate
}

void loop() {
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    Serial.print("Received: ");
    Serial.println(msg);

    // Act based on message content
    if (msg == "Start irrigation in Row 1") {
      digitalWrite(5, HIGH);  // Example: turn ON pump on pin 5
    } else if (msg == "Stop irrigation in Row 1") {
      digitalWrite(5, LOW);   // Turn OFF pump
    }
  }
}
