char server[] = "9657-2401-4900-52b4-7a3-b4e6-665d-6cb-2882.ngrok.io";               // Add Ngrok site here without http://
char ssid[] = "HitenLulla";       // your wifi SSID (name)
char pass[] = "8381006633";      // your wifi password
const unsigned long postingInterval = 1500L;      // delay between API Calls, in milliseconds with L

#include "WiFiEsp.h"            // Library to access ESP WiFi shield.
#ifndef HAVE_HWSERIAL1
#include "SoftwareSerial.h"
SoftwareSerial Serial1(2, 3);   // RX, TX connection
#endif

int status = WL_IDLE_STATUS;     // the Wifi radio's status
long int fsr1 = 0;
long int fsr2 = 0;
long int fsr3 = 0;
//long int fsr4 = 0;
long int fsr5 = 0;
//long int fsr6 = 0;

void get_sensor_readings(){
  fsr1 = analogRead(A0);
  fsr2 = analogRead(A1);
  fsr3 = analogRead(A2);
//  fsr4 = analogRead(A3);
  fsr5 = analogRead(A6);
//  fsr6 = analogRead(A7);
}

unsigned long lastConnectionTime = 0;         // last time you connected to the server, in milliseconds
WiFiEspClient client;                         // Initialize the Ethernet client object

void setup()
{
  // initialize serial for debugging
  Serial.begin(115200);
  // initialize serial for ESP module
  Serial1.begin(9600);
  // initialize ESP WiFi Shield
  WiFi.init(&Serial1);

  // check for the presence of the shield
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not found");
    // don't continue
    while (true);
  }

  // attempt to connect to WiFi network
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WiFi: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
  }
  Serial.println("Connected to the network");
}

void loop()
{
  /*
  // For Debugging
  while (client.available()) {
    char c = client.read();
    Serial.write(c);
  }
  */
  if (millis() - lastConnectionTime > postingInterval) {
    get_sensor_readings();
    call_api();
  }
}

// this method makes a HTTP connection to the server
void call_api()
{
  Serial.println();
    
  // close any connection before send a new request
  // this will free the socket on the WiFi shield
  client.stop();

  // if there's a successful connection
  if (client.connect(server, 80)) {
    Serial.println("Connecting...");
    
    // send the HTTP PUT request
    // String url = String("/sensors?") + String("FSR1=") + String(fsr1) + String("&FSR2=") + String(fsr2) + String("&FSR3=") + String(fsr3) + String("&FSR4=") + String(fsr4) + String("&FSR5=") + String(fsr5) + String("&FSR6=") + String(fsr6);
    String url = String("/sensors?") + String("FSR1=") + String(fsr1) + String("&FSR2=") + String(fsr2) + String("&FSR3=") + String(fsr3) + String("&FSR5=") + String(fsr5);
    Serial.println(String(server) + url);
    
    client.println("GET "+ url +" HTTP/1.1");
    client.println("Host: " + String(server));
    client.println("Connection: close");
    client.println();

    // note the time that the connection was made
    lastConnectionTime = millis();
  }
  else {
    // if you couldn't make a connection
    Serial.println("Connection failed");
  }
}
