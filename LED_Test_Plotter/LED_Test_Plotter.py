import matplotlib.pyplot as plt
import numpy as np
import serial
import sys
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter, QColor, QPen
import mainform
import time
import pyqtgraph
import pandas as pd
import threading
from SerialPorts import serial_ports



class LED_Test_App(QtWidgets.QMainWindow, mainform.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self) 
        self.comboBox_Port.addItems(serial_ports())
        self.pushButton_GO.clicked.connect(self.start_test) # start_test
        self.dependence_LI.toggled.connect(self.graph_dependence_changed)
        self.dependence_IC.toggled.connect(self.graph_dependence_changed)
        self.dependence_LC.toggled.connect(self.graph_dependence_changed)

        self.graphicsView_Red.plotItem.showGrid(True,True,1.0)
        self.graphicsView_Green.plotItem.showGrid(True,True,1.0)
        self.graphicsView_Blue.plotItem.showGrid(True,True,1.0)
        self.graphicsView_White.plotItem.showGrid(True,True,1.0)
        
        self.graphicsView_Red.setTitle("<span style=\"color:red;font-size:24px\">Red color</span>")
        self.graphicsView_Green.setTitle("<span style=\"color:green;font-size:24px\">Green color</span>")
        self.graphicsView_Blue.setTitle("<span style=\"color:blue;font-size:24px\">Blue color</span>")
        self.graphicsView_White.setTitle("<span style=\"color:black;font-size:24px\">White color</span>")

        self.graphicsView_Red.setBackground('w')
        self.graphicsView_Green.setBackground('w')       
        self.graphicsView_Blue.setBackground('w')       
        self.graphicsView_White.setBackground('w')

        
        self.red = np.zeros((1,2))
        self.green = np.zeros((1,2))
        self.blue = np.zeros((1,2))
        self.white = np.zeros((1,2))
        self.progressBar.setVisible(False)      
        self.graph_set_labels()
        
        
             
    def __del__(self): 
        try:
            if(self.port.isOpen()):
                self.port.close()
        except Exception as e:
            print(e)
    #def graph_resize(self):
      #  self.MainWindow.get

    def start_test(self):      
        try:                   
            self.port = serial.Serial(self.comboBox_Port.currentText(),115200,timeout = 0.1)
            time.sleep(3)    
            self.led_test_core = LED_Test_Core(self.port)
            if(self.led_test_core.set_led_model(self.comboBox_LED_Model.currentText()) == False): 
                print("[ERROR]: LED model setting")
                return
            self.test_thread()
        except Exception as e:
            print(e)
    def test_thread(self):
        self.progressBar.setVisible(True) 
        self.led_test_core.progress_handler = self.progressBar.setValue
        data = self.led_test_core.run_test()
        self.test_finished(data)
    def test_finished(self,data):
        I_const = data[(data.Red == 0) & (data.Green == 0) & (data.Blue == 0) & (data.White == 0)][['I']].to_numpy(dtype = float)
        zero_point = np.array([[I_const[0,0],0]])
        self.red = np.vstack((zero_point, data[data.Red > 0][['I','L']].to_numpy(dtype = float)  ))   
        self.green = np.vstack((zero_point, data[data.Green > 0][['I','L']].to_numpy(dtype = float) ))  
        self.blue = np.vstack((zero_point, data[data.Blue > 0][['I','L']].to_numpy(dtype = float) ))  
        self.white = np.vstack((zero_point, data[data.White > 0][['I','L']].to_numpy(dtype = float) ))            
        self.plot_all_graphs()
        self.progressBar.setVisible(False) 
        try: 
            self.port.close()
        except Exception as e:
            print(e)
    def graph_dependence_changed(self):       
        radioButton = self.sender()
        if radioButton.isChecked():
            self.graph_set_labels()
            self.plot_all_graphs()
    def resizeEvent(self, event):
        s = self.centralwidget.size()
        s.setHeight(s.height() - 100)
        s.setWidth(s.width() - 40)
        self.gridLayoutWidget.resize(s)
    def graph_set_labels(self):
        if self.dependence_LI.isChecked():
            x_text  = "Current"
            x_units = "mA"
            y_text  = "Luminosity"
            y_units = "mV"
        elif self.dependence_IC.isChecked():
            x_text  = "Code"
            x_units = "integer"
            y_text  = "Current"
            y_units = "mA"
        else: 
            x_text  = "Code"
            x_units = "integer"
            y_text  = "Luminosity"
            y_units = "mV"
        self.graphicsView_Red.setLabel('left',      "<span style=\"color:black;font-size:18px\">" +y_text +' ('+y_units+')' +"</span>")
        self.graphicsView_Red.setLabel('bottom',    "<span style=\"color:black;font-size:18px\">" +x_text +' ('+x_units+')' +"</span>")
        self.graphicsView_Green.setLabel('left',    "<span style=\"color:black;font-size:18px\">" +y_text +' ('+y_units+')' +"</span>")
        self.graphicsView_Green.setLabel('bottom',  "<span style=\"color:black;font-size:18px\">" +x_text +' ('+x_units+')' +"</span>")
        self.graphicsView_Blue.setLabel('left',     "<span style=\"color:black;font-size:18px\">" +y_text +' ('+y_units+')' +"</span>")
        self.graphicsView_Blue.setLabel('bottom',   "<span style=\"color:black;font-size:18px\">" +x_text +' ('+x_units+')' +"</span>")
        self.graphicsView_White.setLabel('left',    "<span style=\"color:black;font-size:18px\">" +y_text +' ('+y_units+')' +"</span>")
        self.graphicsView_White.setLabel('bottom',  "<span style=\"color:black;font-size:18px\">" +x_text +' ('+x_units+')' +"</span>")

    def plot_all_graphs(self):   
        self.plot_graph_R(self.red)
        #print("RED: Imax = ",self.red.max(axis=0)[0],"mA Lmax = ",self.red.max(axis=0)[1]," mV")
        self.plot_graph_G(self.green)
        #print("GREEN: Imax = ",self.green.max(axis=0)[0],"mA Lmax = ",self.green.max(axis=0)[1]," mV")
        self.plot_graph_B(self.blue)
        #print("BLUE: Imax = ",self.blue.max(axis=0)[0],"mA Lmax = ",self.blue.max(axis=0)[1]," mV")
        self.plot_graph_W(self.white)       
        #print("RGB: Imax = ",self.white.max(axis=0)[0],"mA Lmax = ",self.white.max(axis=0)[1]," mV")
    def convert_graph_data(self,data):

        if self.dependence_LI.isChecked():
            return data
        elif self.dependence_IC.isChecked(): 
            return np.column_stack((range(data.shape[0]),data[:,0]))
        else:
            return np.column_stack((range(data.shape[0]),data[:,1]))

    def get_graph_legend(self,data):
        return "<span>&nbsp;&nbsp;&nbsp;&nbsp;Imax = " + str(data.max(axis=0)[0]) + " mA Lmax = " + str(data.max(axis=0)[1]) + " mV<br>\
                      &nbsp;&nbsp;&nbsp;&nbsp;Imin = " + str(data.min(axis=0)[0]) + " mA</span>"

    def plot_graph_R(self,data):     
        pen=pyqtgraph.mkPen(color='r',width=2)
        data_c = self.convert_graph_data(data)   
        s = self.get_graph_legend(data)
        try:
            self.graphicsView_Red_legend.scene().removeItem(self.graphicsView_Red_legend)
        except Exception as e: pass
        self.graphicsView_Red_legend = self.graphicsView_Red.addLegend()
        self.graphicsView_Red.plot(data_c[:,0],data_c[:,1],pen=pen,name = s,clear=True)

    def plot_graph_G(self,data):     
        pen=pyqtgraph.mkPen(color='g',width=2)
        data_c = self.convert_graph_data(data)   
        s = self.get_graph_legend(data)      
        try:
            self.graphicsView_Green_legend.scene().removeItem(self.graphicsView_Green_legend)
        except Exception as e: pass          
        self.graphicsView_Green_legend = self.graphicsView_Green.addLegend()
        self.graphicsView_Green.plot(data_c[:,0],data_c[:,1],pen=pen,name = s,clear=True)

    def plot_graph_B(self,data):     
        pen=pyqtgraph.mkPen(color='b',width=2)
        data_c = self.convert_graph_data(data)   
        s = self.get_graph_legend(data)
        try:
            self.graphicsView_Blue_legend.scene().removeItem(self.graphicsView_Blue_legend)
        except Exception as e: pass
        self.graphicsView_Blue_legend = self.graphicsView_Blue.addLegend()
        self.graphicsView_Blue.plot(data_c[:,0],data_c[:,1],pen=pen,name = s,clear=True)

    def plot_graph_W(self,data):     
        pen=pyqtgraph.mkPen(color='k',width=2)
        data_c = self.convert_graph_data(data)   
        s = self.get_graph_legend(data)
        try:
            self.graphicsView_White_legend.scene().removeItem(self.graphicsView_White_legend)
        except Exception as e: pass
        self.graphicsView_White_legend = self.graphicsView_White.addLegend()
        self.graphicsView_White.plot(data_c[:,0],data_c[:,1],pen=pen,name = s,clear=True)    

class LED_Test_Core():
    def __init__(self,port):
        self.port = port
        self.progress_handler = None
        self.color_max_value = 255 # (0-255)
        self.color_max_value += 1
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
        for r in range(self.color_max_value):
            self.__add_measurement(r,0,0,0)
            self.__inc_progress()
        for g in range(self.color_max_value):
            self.__add_measurement(0,g,0,0)
            self.__inc_progress()
        for b in range(self.color_max_value):
            self.__add_measurement(0,0,b,0)
            self.__inc_progress()
        for w in range(self.color_max_value):
            self.__add_measurement(0,0,0,w)
            self.__inc_progress()
        self.set_color(0,0,0,0)
        return self.measurements
    def __add_measurement(self,R,G,B,W):
        response = self.set_color(R,G,B,W)
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
        self.port.write(model.encode())
        return self.port.readline().decode("utf-8").strip() == "ok"
    def set_color(self,R,G,B,W):
        arg_str = str(R) +' '+ str(G) +' '+ str(B) +' '+ str(W)
        self.port.write(arg_str.encode())
        return self.port.readline().decode("utf-8").strip()
    def __inc_progress(self):
        if self.progress_handler is not None:
            self.progress += 1
            self.progress_handler(self.progress / (self.color_max_value * 4) * 100)
    
def main():
    app = QtWidgets.QApplication(sys.argv)  
    window = LED_Test_App()  
    window.show() 
    app.exec_() 
    
if __name__ == '__main__':  
    main()  