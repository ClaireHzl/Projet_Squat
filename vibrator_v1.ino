#include <WiFi.h>
#include <WiFiUdp.h>
#include <SPI.h>

const char* ssid     = "SSID"; // Change this to your WiFi SSID
const char* password = "password"; // Change this to your WiFi password
unsigned int localPort = 8000;      // local port to listen on
char packetBuffer[255]; //buffer to hold incoming packet

WiFiUDP Udp;

const int Pin = 25;  // 25 corresponds to GPIO A1
const int freq = 5000;
const int channel = 0;
const int resolution = 8;

void setup() {

  //Initialize serial and wait for port to open:
  Serial.begin(115200);

  // connect to WiFi network
  Serial.println();
  Serial.println("******************************************************");
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  Serial.println("\nStarting connection to server...");

  // connect to server
  Udp.begin(localPort);

  // set PWM parameters up
  ledcSetup(channel, freq, resolution);
  ledcAttachPin(Pin, channel);
}

void loop() {
  // initialize message
  int message=0;

  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  
  if (packetSize) {  
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    Serial.print("From ");
    IPAddress remoteIp = Udp.remoteIP();
    Serial.print(remoteIp);
    Serial.print(", port ");
    Serial.println(Udp.remotePort());

    // read the packet into packetBufffer
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0;
    }

    Serial.println("Contents:");
    Serial.println(packetBuffer);  
    message=std::stof(packetBuffer);
    }

    // output the value of message as motor tension on set GPIO
    ledcWrite(channel, message);
    
    delay(50);

}
