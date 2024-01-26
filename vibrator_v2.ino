#include <WiFi.h>
#include <WiFiUdp.h>
#include <SPI.h>
#include <Wire.h>
#include "Adafruit_DRV2605.h"
#include <stdlib.h>
#include <pthread.h>

const char* ssid     = "SSID";//"Galaxy de Claire"; // Change this to your WiFi SSID
const char* password = "password";//"azpw0641"; // Change this to your WiFi password
const int port = 8000; // Change this to UDP port number

WiFiUDP Udp;
unsigned int localPort = port;      // port to listen to
char packetBuffer[255]; //buffer to hold incoming packet

int message = 0;
bool flag=false;

Adafruit_DRV2605 drv;

void setup() {

  //Initialize serial and wait for port to open:
  Serial.begin(115200);

  // CONNECT TO WIFI
  // Give info on network
  Serial.println();
  Serial.println("******************************************************");
  Serial.print("Connecting to ");
  Serial.println(ssid);

  //connect
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }
  Serial.println("");
  
  //confirm and give IP adress
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  //CONNECT TO SERVER
  Serial.println("\nStarting connection to server at port");
  Serial.println(port);
  // if you get a connection, report back via serial:
  while (! Udp.begin(localPort)){
    Serial.println("\nCould not find server");
    delay(500);
  }
  Serial.println("\nConnected");

  //CONNECT TO DRIVER
  Serial.println("\nStarting connection to driver...");
  if (! drv.begin()) {
    Serial.println("\nCould not find DRV2605");
    while (1) delay(10);
  }
  drv.selectLibrary(1);
  // default, internal trigger when sending GO command
  drv.setMode(DRV2605_MODE_REALTIME); 
  Serial.println("\nConnected");

  // THREADS SETUP
  pthread_t thread;
  pthread_t thread_vib;
  pthread_create(&thread,NULL,task,NULL);
  pthread_create(&thread_vib,NULL,task2,NULL);
  pthread_join(thread,NULL);
  pthread_join(thread_vib,NULL);
}

void loop() {  
  //EMPTY (work gets done in threads)  
}

// TASK1 : listen to Udp and update message and flag
void* task(void*){
  while (true){
    //READ
    // if there's data available, read a packet
    int packetSize = Udp.parsePacket();
    
    // print info if needed
    if (packetSize) {
      flag = true;
      
//      Serial.print("Received packet of size ");
//      Serial.println(packetSize);
//      Serial.print("From ");
//      IPAddress remoteIp = Udp.remoteIP();
//      Serial.print(remoteIp);
//      Serial.print(", port ");
//      Serial.println(Udp.remotePort());
  
      // read the packet into packetBufffer
      int len = Udp.read(packetBuffer, 255);
      if (len > 0) {
        packetBuffer[len] = 0;
      }
      message = atoi(packetBuffer);
//      Serial.println("Contents:");
//      Serial.println(message);
    }
    else{
      flag = false;
    }
    delay(100);
  }
}

// TASK2 : control motor through driver
void* task2(void*){
  while (true){
    Serial.println("Contents:");
    Serial.println(message);
    while (flag){
      drv.setRealtimeValue(0x10);
      delay(40);
      drv.setRealtimeValue(0x00);
      delay(message);
    }
  }
}
