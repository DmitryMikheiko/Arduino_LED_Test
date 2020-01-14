#include <Adafruit_ADS1015.h>
#include <Adafruit_NeoPixel.h>

#define LED_PIN 7
bool RGBW_LED = false;

// Parameter 1 = number of pixels in strip
// Parameter 2 = pin number (most are valid)
// Parameter 3 = pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
Adafruit_NeoPixel strip = Adafruit_NeoPixel(1, LED_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_ADS1115 ads;  
void PrintSensors(){
  float adc_I, adc_L;
  ads.setGain(GAIN_SIXTEEN);
  adc_I = (ads.readADC_SingleEnded(0) * 0.0078125f) / 4.0f ;
  ads.setGain(GAIN_TWOTHIRDS);
  adc_L = ads.readADC_SingleEnded(1);  
  adc_L = adc_L < 32768.0f ? (adc_L * 0.1875f) : 0.0f;

  
  Serial.print(adc_I);
  Serial.print(' ');
  Serial.print(adc_L);
  //Serial.print("I: ");Serial.print(adc_I);Serial.println(" mA");
  //Serial.print("L: ");Serial.print(adc_L);Serial.println(" mV");
  Serial.println();
}
void setup() {
  Serial.begin(115200);
  // ads.setGain(GAIN_TWOTHIRDS);  // 2/3x gain +/- 6.144V  1 bit =  0.1875mV (default)
   ads.setGain(GAIN_ONE);        // 1x gain   +/- 4.096V  1 bit =  0.125mV
  // ads.setGain(GAIN_TWO);           // 2x gain   +/- 2.048V  1 bit =  0.0625mV
  // ads.setGain(GAIN_FOUR);       // 4x gain   +/- 1.024V  1 bit =  0.03125mV
  // ads.setGain(GAIN_EIGHT);      // 8x gain   +/- 0.512V  1 bit =  0.015625mV
  // ads.setGain(GAIN_SIXTEEN);    // 16x gain  +/- 0.256V  1 bit =  0.0078125mV
  ads.begin();
  strip.begin();
  Serial.setTimeout(10);
}
int R,G,B,W;
void loop() {
  while(1){
    if(Serial.available() > 0){
      String args = Serial.readString();
      byte args_count = sscanf(args.c_str(),"%u %u %u %u", &R,&G,&B,&W);
      
      if(args_count == 0){
        args.toLowerCase();
        Serial.println(args);
        if(args.indexOf("sk6812")) {
          RGBW_LED = true;
          strip.updateType(NEO_RGBW);
          Serial.println("OK");
        }
        if(args.indexOf("ws2812b")){
          RGBW_LED = false;
          strip.updateType(NEO_GRB);
          Serial.println("OK");
        }
      }
      else {
        if(RGBW_LED) strip.setPixelColor(0,R,G,B,W);
        else {
          if(W > 0) R=G=B=W;
          strip.setPixelColor(0,R,G,B); 
        }
        strip.show();
        delay(10);
        PrintSensors();
        R=G=B=W=0;
      }
    }
  }
  // put your main code here, to run repeatedly:
  for(int r=0;r<256;r++){
     strip.setPixelColor(0,r,0,0);
     Serial.print("R:");
     Serial.println(r);
     strip.show();
     delay(10);
     PrintSensors();
  }
  for(int g=0;g<256;g++){
     strip.setPixelColor(0,0,g,0);
     Serial.print("G:");
     Serial.println(g);
     strip.show();
     delay(10);
     PrintSensors();
  }
  for(int b=0;b<256;b++){
     strip.setPixelColor(0,0,0,b);
     Serial.print("B:");
     Serial.println(b);
     strip.show();
     delay(10);
     PrintSensors();
  }
  while(1);
}
