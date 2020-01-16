import pandas as pd
import serial

class LED_Test_Core():
    def __init__(self,port = None):
        self.port = port
        self.progress_handler = None
        self.color_max_value = 255 # (0-255)
        self.color_max_value += 1
        self.speed = 1
        self.led_model = 'ws2812b'
        self.led_rgbw_models = ['sk6812rgbw']
        self.measurements = pd.DataFrame({
                            'Red'   :[0],
                            'Green' :[0],
                            'Blue'  :[0],
                            'White' :[0],
                            'I'     :[0],
                            'L'     :[0]
                            })
    def run_test(self):       
        self.measurements = self.measurements.iloc[0:0]      
        self.progress = 0
        for r in range(0, self.color_max_value, self.speed):
            self.__add_measurement(r,0,0,0)
            self.__inc_progress()
        for g in range(0, self.color_max_value, self.speed):
            self.__add_measurement(0,g,0,0)
            self.__inc_progress()
        for b in range(0, self.color_max_value, self.speed):
            self.__add_measurement(0,0,b,0)
            self.__inc_progress()
        for w in range(0, self.color_max_value, self.speed):
            self.__add_measurement(0,0,0,w)
            self.__inc_progress()
        if self.IsLED_RGBW():
            for w in range(0, self.color_max_value, self.speed):
                self.__add_measurement(w,w,w,0)
                self.__inc_progress()
        self.set_color(0,0,0,0)
        return self.measurements
    def IsLED_RGBW(self):
        return any(self.led_model.lower() in s.lower() for s in self.led_rgbw_models)
    def __add_measurement(self,R,G,B,W):
        response = self.set_color(R,G,B,W)
        if response is None: return
        response = response.split(' ')
        self.measurements = self.measurements.append({
                            'Red'   : R,
                            'Green' : G,
                            'Blue'  : B,
                            'White' : W,
                            'I'     : response[0],
                            'L'     : response[1]
                                  },ignore_index=True)           

    def set_led_model(self,model):
        if self.port is None: return False
        self.led_model = model
        self.port.write(model.encode())
        return self.port.readline().decode("utf-8").strip() == "ok"

    def set_color(self,R,G,B,W):
        if self.port is None: return None
        arg_str = str(R) +' '+ str(G) +' '+ str(B) +' '+ str(W)
        self.port.write(arg_str.encode())
        return self.port.readline().decode("utf-8").strip()

    def __inc_progress(self):
        if self.progress_handler is not None:
            self.progress += self.speed
            if self.IsLED_RGBW(): max_progress = self.color_max_value * 5
            else: max_progress = self.color_max_value * 4
            self.progress_handler(self.progress / max_progress * 100)
