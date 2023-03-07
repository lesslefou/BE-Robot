"""!
 * @file        MainWindows.py
 * @brief       Principal page to launch the QT application
 * @author      Clément Rouvier | Lisa Duterte
 * @version     0.1
 * @date        2023
"""


import os
from PyQt5.QtCore import *
import serial,serial.tools.list_ports  #pip install pyserial
from PyQt5.QtWidgets import *
from Common import *
import time



# ------------------- Definition of central point for acquisition ---
x_ptr = 0
y_ptr = 419
z_ptr = -165

speed = 2000
COM = "COM0"
initOscilloscope = False
initRobot = False
idOscilloscope = 'USB0::0x05FF::0x1023::3561N16324::INSTR'


"""
 * @brief Search the list of USB devices connected to the computer
"""
def find_USB_device():
        myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]   
        usb_port_list = [p[0:2] for p in myports]        
        return usb_port_list


"""
 * @brief Class managing the QT application 
"""
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #change the title of the window
        self.setWindowTitle("Robot bureau d'étude")
        #window size
        self.resize(1200, 800)
        self.setMinimumSize(1200,800)
        self.setMaximumSize(1200, 800)        
        self.portlist=find_USB_device()
        self.items=[p[1] for p in self.portlist]#["COM1","COM2"]
        self.items.append("Choice COM Port KEOLABS Robx")
        
        centralArea = QWidget()
        centralArea.setStyleSheet("background: '#ECECEC'")
        self.setCentralWidget(centralArea)
        
        global left_widget
        left_widget = QWidget(centralArea)
        left_widget.setGeometry(10, 10, 790, 750)
        left_widget.setStyleSheet("background-color: green;")
        
        
        right_widget = QWidget(centralArea)
        right_widget.setGeometry(800, 0, 400, 800)
        
        #------------------------COM Ports----------------------
        port_widget = QWidget(right_widget)
        port_widget.setGeometry(0, 0, 400, 80)       
        port_widget.selectlbl = QLabel("Select port:")
        #label
        port_widget.typeBox=QComboBox()
        port_widget.typeBox.addItems(self.items)
        port_widget.typeBox.setCurrentIndex(port_widget.typeBox.count()-1) 
        
        fields=QGridLayout()
        fields.addWidget(port_widget.selectlbl,0,0)
        fields.addWidget(port_widget.typeBox,1,0)
        port_widget.setLayout(fields)
        #signal connection 
        COM = port_widget.typeBox.currentIndexChanged.connect(self.valuePort)
                
        
        #------------------------Speed----------------------        
        speed_widget = QWidget(right_widget)
        speed_widget.setGeometry(0, 80, 400, 90)
                
        #Slider speed
        title_speed = QLabel("Select speed:")
        slider = QSlider(Qt.Horizontal, speed_widget)
        label1 = QLabel("Very Slow")
        label2 = QLabel("  Slow")
        label3 = QLabel("  Medium")
        label4 = QLabel("   Fast")
        label5 = QLabel("     Very Fast")
        grid = QGridLayout()
        grid.addWidget(title_speed, 0, 0, 1, 5)
        grid.addWidget(slider, 1, 0, 1, 5)        
        grid.addWidget(label1, 2, 0)
        grid.addWidget(label2, 2, 1)
        grid.addWidget(label3, 2, 2)
        grid.addWidget(label4, 2, 3)
        grid.addWidget(label5, 2, 4)
        slider.setMinimum(1000)
        slider.setMaximum(2000)
        slider.setValue(speed)
        speed_widget.setLayout(grid)
        #connection du signal
        slider.sliderReleased.connect(self.valueChanged)
        
        #------------------------Buttons----------------------
        btn_widget = QWidget(right_widget)
        btn_widget.setGeometry(0, 250, 400, 250)
        self.button1 = QPushButton(' Oscilloscope COM Initialization')
        self.button2 = QPushButton('Setup Oscilloscope Parameters')
        self.button3 = QPushButton('Robot Initialization')
        self.button4 = QPushButton('Home Position ')
        self.button5 = QPushButton('NFC Figure')
        self.button6 = QPushButton('EMVCO Figure')
        self.button7 = QPushButton('Close Robot communication')
        self.button1.setEnabled(False)
        self.button2.setEnabled(False)
        self.button3.setEnabled(False)
        self.button4.setEnabled(False)
        self.button5.setEnabled(False)
        self.button6.setEnabled(False)
        self.button7.setEnabled(False)
        self.button8 = QPushButton('Robot 5 axes')
        self.button9 = QPushButton('Robot 6 axes')
        
        btn_widgetAxes = QWidget(right_widget)
        btn_widgetAxes.setGeometry(0, 200, 400, 50)
        grid_btnAxes = QGridLayout()
        grid_btnAxes.addWidget(self.button8, 0, 0)
        grid_btnAxes.addWidget(self.button9, 0, 1)
        btn_widgetAxes.setLayout(grid_btnAxes)
        
        grid_btn = QGridLayout()
        grid_btn.addWidget(self.button1, 0, 0)
        grid_btn.addWidget(self.button2, 1, 0)
        grid_btn.addWidget(self.button3, 2, 0)
        grid_btn.addWidget(self.button4, 3, 0)
        grid_btn.addWidget(self.button5, 4, 0)
        grid_btn.addWidget(self.button6, 5, 0)
        grid_btn.addWidget(self.button7, 6, 0)
        btn_widget.setLayout(grid_btn)
        
        
        self.button1.clicked.connect(self.initOscilloscope)
        self.button2.clicked.connect(self.setupOscilloscope)
        self.button3.clicked.connect(self.initialization)
        self.button4.clicked.connect(S_GoToHome)
        self.button5.clicked.connect(self.nfc)
        self.button6.clicked.connect(self.emvco)
        self.button7.clicked.connect(self.disconnect)
        self.button8.clicked.connect(self.robotAxis5)
        self.button9.clicked.connect(self.robotAxis6)        
        
        
        
        #------------------------Reference point coordinates----------------------
        text_widget = QWidget(right_widget)
        text_widget.setGeometry(0, 500, 550, 80)
        title = QLabel("Possible Coordinates for the reference point:")
        indicator = QTextEdit("x=[ ; ] ; y=[ ; ] ;  z=[ ; ]")
        indicator.setEnabled(False)
        grid = QGridLayout()
        grid.addWidget(title, 0, 0)  
        grid.addWidget(indicator, 1, 0)      
        text_widget.setLayout(grid)
        
        ptr_widget = QWidget(right_widget)
        ptr_widget.setGeometry(0, 570, 400, 80)
        title = QLabel("Choice of coordinates for the reference point:")
        label_x = QLabel("x :")
        self.x = QLineEdit()
        label_y = QLabel("y :")
        self.y = QLineEdit()
        label_z = QLabel("z :")
        self.z = QLineEdit()
        validateCoordPtBtn = QPushButton('OK')
        grid = QGridLayout() 
        grid.addWidget(label_x, 1, 0)  
        grid.addWidget(self.x, 1, 1)
        grid.addWidget(label_y, 1, 2)
        grid.addWidget(self.y, 1, 3)
        grid.addWidget(label_z, 1, 4)
        grid.addWidget(self.z, 1, 5)
        grid.addWidget(validateCoordPtBtn, 1, 6)
        ptr_widget.setLayout(grid)
        
        validateCoordPtBtn.clicked.connect(self.validateCoordPt)
        
        
        #------------------------Validatation Text Box----------------------
        validTextBox_widget = QWidget(right_widget)
        validTextBox_widget.setGeometry(0, 650, 350, 100)
        validTextBox_widget.setStyleSheet("border: 1px solid black;")
    
        grid = QVBoxLayout()
        global validationText
        validationText = QTextEdit()
        validationText.setEnabled(False)
        grid.addWidget(validationText)
        validTextBox_widget.setLayout(grid)
        
        
    """
     * @brief activate the buttons
    """ 
    def robotAxis5(self):
        self.RobID = 5
        self.button1.setEnabled(True)
        self.button1.setEnabled(True)
        self.button2.setEnabled(False)
        self.button3.setEnabled(True)
        self.button4.setEnabled(True)
        self.button5.setEnabled(True) 
        self.button6.setEnabled(False)
        self.button7.setEnabled(True)
        self.button9.setEnabled(True)
        speed5axis()
    
        
    """
     * @brief activate the buttons
    """ 
    def robotAxis6(self):
        self.RobID = 6
        self.button1.setEnabled(True)
        self.button1.setEnabled(True)
        self.button2.setEnabled(False)
        self.button3.hide()
        self.button4.hide()
        self.button5.setEnabled(False)
        self.button6.setEnabled(False)
        self.button7.setEnabled(False)
        self.button8.setEnabled(False)
        speed6axis()
        
    """
     * @brief activate the acquisition buttons
    """ 
    def acquisitionButtonsActivation(self):
         if (initOscilloscope == True):
             self.button5.setEnabled(True)
             self.button6.setEnabled(True)

    """
     * @brief activate the setup oscilloscope button
    """ 
    def setupOscilloscopeButtonActivation(self):
         if (initOscilloscope == True):
             self.button2.setEnabled(True)

    """
     * @brief activate the robot buttons
    """ 
    def robotButtonsActivation(self):
        if (initRobot == True):
             self.button4.setEnabled(True)
             self.button7.setEnabled(True)
             
    
    """
     * @brief Initialise the connection to the oscilloscope
    """ 
    def initOscilloscope(self):
        rm = oscilloscopeConnection(idOscilloscope)
        #display the action on the specific Text Box
        validationText.setText("Oscilloscope Connection: " + str(rm.list_resources()))
        
        #variable set to true in order to enable the setupOscilloscope fonction
        global initOscilloscope
        initOscilloscope = True
        self.acquisitionButtonsActivation()
        self.setupOscilloscopeButtonActivation()
    
    """
     * @brief Launch the setup fonction of the oscilloscope
    """ 
    def setupOscilloscope(self):
        if (initOscilloscope == True):
            setOscilloscopeParameters()
            validationText.setText("Oscilloscope Setup Done")
        else : 
            validationText.setText("You must first connect to the oscilloscope")
        
   
    """
     * @brief Initialize the Robot position 
    """ 
    def initialization(self):
        err = S_Initialization(COM,self.RobID)
        global initRobot
        if err == 0 :
            validationText.setText("Robot Connection Done")
            initRobot = True
            self.acquisitionButtonsActivation()
            self.robotButtonsActivation()
        else :
            validationText.setText("Wrong COM port or cable connected")
            
    """
     * @brief Launch the NFC Acquisition 
    """  
    def nfc(self):
        #display the action on the specific Text Box
        left_widget.setStyleSheet("image: url(./nfc.jpg)")
        validationText.setText("Click on NFC Fonction")
        nfc(x_ptr, y_ptr, z_ptr,speed)
            
    """
     * @brief Launch the EMVCO Acquisition 
    """   
    def emvco(self):
        #display the action on the specific Text Box
        left_widget.setStyleSheet("image: url(./emvco.jpg)")
        validationText.setText("Click on EMVCO Fonction")
        emvco(x_ptr, y_ptr, z_ptr,speed)
            
    """
     * @brief Disconnect the Robot Communication 
    """ 
    def disconnect(self): 
        if (initRobot == True):
            S_Close_Communication()
            validationText.setText("Robot Disconnection Done")
        else: 
            validationText.setText("You must first connect to the oscilloscope")
        
    """
     * @brief Check if the text entered in the text field is a number or not.
    """ 
    def validateCoordPt(self):
        global x_ptr, y_ptr, z_ptr
        if not self.x.text() or not self.y.text() or not self.z.text() :
            validationText.setText("At least one of the coordinates is empty")
        else :
            if self.x.text().isnumeric() and self.y.text().isnumeric() and self.z.text().isnumeric() :
                x_ptr = int(self.x.text())
                y_ptr = int(self.y.text())
                z_ptr = int(self.z.text())
                validationText.setText("Coordinates Validate")
            else : validationText.setText("x, y or z is not a nomber")
    
    """
     * @brief Notify a change on the speed slider
    """ 
    def valueChanged(self):
        global speed
        slider = self.sender()
        speed = slider.value()
        validationText.setText("speed : " + str(speed))
        print("speed : ", speed) 
          
    """
     * @brief Notify a change on the COM list
    """   
    def valuePort(self):
        global COM
        port = self.sender()
        COM = self.portlist[port.currentIndex()][0]
                
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
    
    