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
from LED_Test_Core import *



class LED_Test_App(QtWidgets.QMainWindow, mainform.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self) 
        self.comboBox_Port.addItems(serial_ports())
        self.pushButton_GO.clicked.connect(self.start_test) # start_test
        self.pushButton_GO_FAST.clicked.connect(lambda : self.start_test('fast')) # start_test
        self.dependence_LI.toggled.connect(self.graph_dependence_changed)
        self.dependence_IC.toggled.connect(self.graph_dependence_changed)
        self.dependence_LC.toggled.connect(self.graph_dependence_changed)
        self.dependence_All.toggled.connect(self.graph_dependence_changed)

        self.graphicsView_Red.plotItem.showGrid(True,True,0.5)
        self.graphicsView_Green.plotItem.showGrid(True,True,0.5)
        self.graphicsView_Blue.plotItem.showGrid(True,True,0.5)
        self.graphicsView_White.plotItem.showGrid(True,True,0.5)
             
        self.graphicsView_Red.setBackground('w')
        self.graphicsView_Green.setBackground('w')       
        self.graphicsView_Blue.setBackground('w')       
        self.graphicsView_White.setBackground('w')
       
        self.red = np.zeros((1,2))
        self.green = np.zeros((1,2))
        self.blue = np.zeros((1,2))
        self.white_rgb = np.zeros((1,2))
        self.white = np.zeros((1,2))

        self.led_test_core = LED_Test_Core()

        self.progressBar.setVisible(False)      
        self.sign_graphs()
                          
    def __del__(self): 
        try:
            if(self.port.isOpen()):
                self.port.close()
        except Exception as e:
            print(e)

    def start_test(self, speed = 'slow'):      
        try:                   
            self.port = serial.Serial(self.comboBox_Port.currentText(),115200,timeout = 0.1)
            time.sleep(3)    
            
            self.led_test_core.port = self.port
            if(speed == 'fast'): self.led_test_core.speed = 5
            else: self.led_test_core.speed = 1
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
        self.red = np.vstack((zero_point, data[(data.Red > 0) & (data.Green == 0) & (data.Blue == 0)][['I','L']].to_numpy(dtype = float)  ))   
        self.green = np.vstack((zero_point, data[(data.Red == 0) & (data.Green > 0) & (data.Blue == 0)][['I','L']].to_numpy(dtype = float) ))  
        self.blue = np.vstack((zero_point, data[(data.Red == 0) & (data.Green == 0) & (data.Blue > 0)][['I','L']].to_numpy(dtype = float) ))  
        if self.led_test_core.IsLED_RGBW():
           self.white_rgb = np.vstack((zero_point, data[(data.Red > 0) & (data.Green > 0) & (data.Blue > 0)][['I','L']].to_numpy(dtype = float) ))
           self.white = np.vstack((zero_point, data[data.White > 0][['I','L']].to_numpy(dtype = float) ))
        else:
            self.white_rgb = np.vstack((zero_point, data[data.White > 0][['I','L']].to_numpy(dtype = float) ))
        self.plot_all_graphs()
        self.progressBar.setVisible(False) 
        try: 
            self.port.close()
        except Exception as e:
            print(e)

    def graph_dependence_changed(self):       
        radioButton = self.sender()
        if radioButton.isChecked():
            self.sign_graphs()
            self.plot_all_graphs()

    def resizeEvent(self, event):
        s = self.centralwidget.size()
        s.setHeight(s.height() - 100)
        s.setWidth(s.width() - 40)
        self.gridLayoutWidget.resize(s)

    def graph_set_labels(self, plotter, x_text, x_units, y_text, y_units):
        plotter.setLabel('left',      "<span style=\"color:black;font-size:18px\">" +y_text +' ('+y_units+')' +"</span>")
        plotter.setLabel('bottom',    "<span style=\"color:black;font-size:18px\">" +x_text +' ('+x_units+')' +"</span>")

    def graphs_set_labels(self, x_text, x_units, y_text, y_units):
        self.graph_set_labels(self.graphicsView_Red, x_text, x_units, y_text, y_units)
        self.graph_set_labels(self.graphicsView_Green, x_text, x_units, y_text, y_units)
        self.graph_set_labels(self.graphicsView_Blue, x_text, x_units, y_text, y_units)
        self.graph_set_labels(self.graphicsView_White, x_text, x_units, y_text, y_units)

    def graph_set_name(self, plotter, name = '', color = 'black'):
        plotter.setTitle("<span style=\"color:" + color + ";font-size:20px\">"+ name + "</span>")

    def sign_graphs(self):
        if self.dependence_LI.isChecked():
            self.graphs_set_labels("Current", "mA", "Luminosity", "mV")
            self.graph_set_name(self.graphicsView_Red,"L(I)-Red")
            self.graph_set_name(self.graphicsView_Green,"L(I)-Green")
            self.graph_set_name(self.graphicsView_Blue,"L(I)-Blue")
            self.graph_set_name(self.graphicsView_White,"L(I)-White")
        elif self.dependence_IC.isChecked():
            self.graphs_set_labels("Code", "integer", "Current", "mA")
            self.graph_set_name(self.graphicsView_Red,"I(Code)-Red")
            self.graph_set_name(self.graphicsView_Green,"I(Code)-Green")
            self.graph_set_name(self.graphicsView_Blue,"I(Code)-Blue")
            self.graph_set_name(self.graphicsView_White,"I(Code)-White")
        elif self.dependence_LC.isChecked(): 
            self.graphs_set_labels("Code", "integer", "Luminosity", "mV")
            self.graph_set_name(self.graphicsView_Red,"L(Code)-Red")
            self.graph_set_name(self.graphicsView_Green,"L(Code)-Green")
            self.graph_set_name(self.graphicsView_Blue,"L(Code)-Blue")
            self.graph_set_name(self.graphicsView_White,"L(Code)-White")
        else:
            self.graph_set_labels(self.graphicsView_Red,    "Current",  "mA",       "Luminosity",   "mV")
            self.graph_set_labels(self.graphicsView_Green,   "Code",     "integer",  "Luminosity",   "mV")
            self.graph_set_labels(self.graphicsView_Blue,   "Code",     "integer",  "Current",      "mA")
            self.graph_set_labels(self.graphicsView_White,  "Current",  "mA",       "Luminosity",   "mV")
            self.graph_set_name(self.graphicsView_Red,"L(I)-RGB")
            self.graph_set_name(self.graphicsView_Green,"L(Code)-RGB")
            self.graph_set_name(self.graphicsView_Blue,"I(Code)-RGB")
            self.graph_set_name(self.graphicsView_White,"L(I)-White")
        
    def plot_all_graphs(self):
        if(self.dependence_All.isChecked()):
            self.plot_graph(self.graphicsView_Red, self.red,'r', self.get_graph_legend_LI(self.red, False))
            self.plot_graph(self.graphicsView_Red, self.green,'g', self.get_graph_legend_LI(self.green, False), clear = False)
            self.plot_graph(self.graphicsView_Red, self.blue,'b', self.get_graph_legend_LI(self.blue, False), clear = False)

            self.plot_graph(self.graphicsView_Green, self.convert_graph_data_LC(self.red),'r', self.get_graph_legend_LC(self.red))
            self.plot_graph(self.graphicsView_Green, self.convert_graph_data_LC(self.green),'g', self.get_graph_legend_LC(self.green), clear = False)
            self.plot_graph(self.graphicsView_Green, self.convert_graph_data_LC(self.blue),'b', self.get_graph_legend_LC(self.blue), clear = False)

            self.plot_graph(self.graphicsView_Blue, self.convert_graph_data_IC(self.red),'r', self.get_graph_legend_IC(self.red))
            self.plot_graph(self.graphicsView_Blue, self.convert_graph_data_IC(self.green),'g', self.get_graph_legend_IC(self.green), clear = False)
            self.plot_graph(self.graphicsView_Blue, self.convert_graph_data_IC(self.blue),'b', self.get_graph_legend_IC(self.blue), clear = False)

            self.plot_graph(self.graphicsView_White, self.white_rgb,'k', self.get_graph_legend_LI(self.white_rgb, name = 'RGB White'))
            if(self.led_test_core.IsLED_RGBW()):
                self.plot_graph(self.graphicsView_White, self.white,'m', self.get_graph_legend_LI(self.white, name = 'Built-in White'), clear = False)

        else:
            self.plot_graph(self.graphicsView_Red, self.convert_graph_data(self.red),'r', self.get_graph_legend_LI(self.red))
            self.plot_graph(self.graphicsView_Green, self.convert_graph_data(self.green),'g', self.get_graph_legend_LI(self.green))
            self.plot_graph(self.graphicsView_Blue, self.convert_graph_data(self.blue),'b', self.get_graph_legend_LI(self.blue))
            self.plot_graph(self.graphicsView_White, self.convert_graph_data(self.white_rgb),'k', self.get_graph_legend_LI(self.white_rgb))   

    def convert_graph_data_IC(self, data):
        x = np.arange(0, self.led_test_core.color_max_value, self.led_test_core.speed)
        if data.shape[0] != x.shape[0]:
            return data
        return np.column_stack((x, data[:,0]))

    def convert_graph_data_LC(self, data):
        x = np.arange(0, self.led_test_core.color_max_value, self.led_test_core.speed)
        if data.shape[0] != x.shape[0]:
            return data
        return np.column_stack((x, data[:,1]))

    def convert_graph_data(self, data):
        if self.dependence_IC.isChecked(): 
            return self.convert_graph_data_IC(data)
        elif self.dependence_LC.isChecked(): 
            return self.convert_graph_data_LC(data)
        else: return data

    def get_graph_legend_LI(self,data,I_min = True, name = None):
        if name is not None:
            name = name + "<br>&nbsp;&nbsp;&nbsp;&nbsp;"
        else:
            name = ''
        if I_min: 
            return "<span>&nbsp;&nbsp;&nbsp;&nbsp;" + name + "Imax = " + str(data.max(axis=0)[0]) + " mA Lmax = " + str(data.max(axis=0)[1]) + " mV<br>\
                          &nbsp;&nbsp;&nbsp;&nbsp;Imin &nbsp;= " + str(data.min(axis=0)[0]) + " mA</span>"
        else: 
            return "<span>&nbsp;&nbsp;&nbsp;&nbsp;" + name + "Imax = " + str(data.max(axis=0)[0]) + " mA Lmax = " + str(data.max(axis=0)[1]) + " mV</span>"

    def get_graph_legend_LC(self,data):
        return "<span>&nbsp;&nbsp;&nbsp;&nbsp;Lmax = " + str(data.max(axis=0)[1]) + " mV</span>"

    def get_graph_legend_IC(self,data):
        return "<span>&nbsp;&nbsp;&nbsp;&nbsp;Imax = " + str(data.max(axis=0)[0]) + " mA</span>"

    def plot_graph(self, plotter, data, color, name, width = 2, clear = True):
        pen = pyqtgraph.mkPen(color = color, width = width)
        if clear:
            try:
                plotter._legend.scene().removeItem(plotter._legend)
            except Exception : pass
            finally:
                plotter._legend = plotter.addLegend()
        plotter.plot(data[:,0], data[:,1], pen = pen, name = name, clear = clear)
    
def main():
    app = QtWidgets.QApplication(sys.argv)  
    window = LED_Test_App()  
    window.show() 
    app.exec_() 
    
if __name__ == '__main__':  
    main()  