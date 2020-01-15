#include <Adafruit_ADS1015.h>
#include <Adafruit_NeoPixel.h>

#define ADC_Filter_K 5
#define Rs 4.0f

#define repeat(n) for(int i=0;i<n;i++)

#define LED_PIN 7
#define LEDs_Count 10
bool RGBW_LED = false;

// Parameter 1 = number of pixels in strip
// Parameter 2 = pin number (most are valid)
// Parameter 3 = pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
Adafruit_NeoPixel strip = Adafruit_NeoPixel(LEDs_Count, LED_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_ADS1115 ads;  

void PrintSensors(){
  float adc_I(0.0), adc_L(0.0);
  uint16_t adc_buf;
  //******* Measure LED Current(mA) *******
  ads.setGain(GAIN_SIXTEEN);  // 16x gain  +/- 0.256V  1 bit = 0.0078125mV
  repeat(ADC_Filter_K) {
    adc_buf = ads.readADC_SingleEnded(0);
    adc_buf = adc_buf < 32768 ? adc_buf : 0;
    adc_I += (adc_buf * 0.0078125f) / Rs ;
  }
  adc_I /= (float)ADC_Filter_K;
  //******* Measure LED Luminosity(mV) *******
  ads.setGain(GAIN_TWOTHIRDS); // 2/3x gain +/- 6.144V  1 bit = 0.1875mV
  repeat(ADC_Filter_K) {
    adc_buf = ads.readADC_SingleEnded(1);
    adc_buf = adc_buf < 32768 ? adc_buf : 0;
    adc_L += adc_buf * 0.1875f;
  }
  adc_L /= (float)ADC_Filter_K;

  Serial.print(adc_I);
  Serial.print(' ');
  Serial.print(adc_L);
  //Serial.print("I: ");Serial.print(adc_I);Serial.println(" mA");
  //Serial.print("L: ");Serial.print(adc_L);Serial.println(" mV");
  Serial.println();
}
void setup() {
  Serial.begin(115200);
  ads.setGain(GAIN_ONE);  
  ads.begin();
  strip.begin();
  Serial.setTimeout(10);
}
int R,G,B,W;
void loop() {
  while(true){
    if(Serial.available() > 0){
      String args = Serial.readString();
      byte args_count = sscanf(args.c_str(),"%u %u %u %u", &R,&G,&B,&W);
      
      if(args_count == 0){
        args.toLowerCase();
        if(args.indexOf("sk6812") != -1) {
          RGBW_LED = true;
          strip.updateType(NEO_RGBW);
          Serial.println("ok");
        }
        else if(args.indexOf("ws2812b") != -1){
          RGBW_LED = false;
          strip.updateType(NEO_GRB);
          Serial.println("ok");
        }
      }
      else {
        if(RGBW_LED) strip.fill(Adafruit_NeoPixel::Color(R,G,B,W),0,LEDs_Count);
        else {
          if(W > 0) R=G=B=W;
          strip.fill(Adafruit_NeoPixel::Color(R,G,B),0,LEDs_Count);
        }
        strip.show();
        delay(10);
        PrintSensors();
        R=G=B=W=0;
      }
    }
  }
}
