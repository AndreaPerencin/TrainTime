import sys
from PyQt6.QtWidgets import QLabel,QRadioButton, QDoubleSpinBox, QPushButton,QApplication,QComboBox, QGridLayout, QMainWindow, QMessageBox, QWidget, QVBoxLayout
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtCore import pyqtSignal
import xml.etree.ElementTree as ET
import requests
import xmltodict


URL_API = "http://api.irishrail.ie/realtime/realtime.asmx/getStationDataByCodeXML_WithNumMins?StationCode="


#read  list station from xml file and create a dictionary with station name and station code
tree = ET.parse('list_stations.xml')
root = tree.getroot()
stations = {}


for child in root:
    stations[child[0].text.upper()] = [child[4].text]
    
nameStations = list(stations.keys())
    
with open("./defaultStation.txt", "r") as myfile:
    try:
        theNumber = myfile.read().strip()
        defaultStation = int(theNumber)
    except:
        defaultStation = 12
    
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setGeometry(100, 100, 400, 300)    #set window size
        self.setWindowTitle('TrainTime')       
        
        #create central widget for main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create a QFormLayout to arrange the widgets
        my_grid_layout = QGridLayout()
        
        my_grid_layout.addWidget(QLabel('Select station:'), 0, 0)       #add label "select station" and place in first column first row
        
        
        self.combobox = QComboBox()                                     #combo box with list stations
        self.combobox.addItems(nameStations)                            #populate combo box with station names
        self.combobox.setCurrentIndex(defaultStation)                   #set default station 
        
        my_grid_layout.addWidget(self.combobox, 0, 1)                   #place combo box next to "select station label"
        
        my_grid_layout.addWidget(QLabel('Direction:'), 2, 0)            #add label "Direction" and place in first column third row
        
        
        #add radio buttons to select direction
        self.my_radio1 = QRadioButton("Northbound")
        self.my_radio2 = QRadioButton("Southbound")
        self.my_radio3 = QRadioButton("All")
        self.my_radio3.setChecked(True)    # set default selection

        #place radio button in second column and row 2,3,4 (remember that they start with 0)          
        my_grid_layout.addWidget(self.my_radio1,1, 1)
        my_grid_layout.addWidget(self.my_radio2,2, 1)
        my_grid_layout.addWidget(self.my_radio3,3, 1)
        
        my_grid_layout.addWidget(QLabel('Departing in...'), 4, 0)         #add label "Direction" and place in first column third row
        
        self.dspin = QDoubleSpinBox()                                     #create a double spin box
        self.dspin.setMaximum(70)                                         #set max value
        self.dspin.setDecimals(0)                                         #because we don't need decimals
        self.dspin.setValue(20)                                           #set default value
        self.dspin.setSuffix(" min")                                      #add suffix to the user selection
        my_grid_layout.addWidget(self.dspin, 4, 1)                        #place the double spin box on the 5th row, right side  
        
        self.go_button = QPushButton(text="Let's go!!!")                  #add button to send request
        #in the next line we launch the send_request function with the arguments selected by the user
        self.go_button.clicked.connect(lambda: self.send_request(self.combobox.currentText(),self.my_radio1.isChecked(), self.my_radio2.isChecked(), self.dspin.value()))

        
        my_grid_layout.addWidget(self.go_button, 5,0,1,2)                 # place the button at the bottom center of the canvas 

        self.label_img = QLabel(self)                                     # create a lablel where we'll add an image
        self.pixmap1 = QPixmap('dartpic1.jpeg')                           # select file to open
        self.pixmap1 = self.pixmap1.scaled(390,140)                       # scale image to fit in the label
        self.label_img.setPixmap(self.pixmap1)                            #add  pic to label
        my_grid_layout.addWidget(self.label_img, 6,0,1,2)                 #place the label in the canvas
        
        central_widget.setLayout(my_grid_layout)
        

        menu_bar = self.menuBar()                                         #add menu

        file_menu = menu_bar.addMenu('&File')                             #add File to the menu
        
        # new menu item
        new_action = QAction('&Set default station', self)
        new_action.setStatusTip('Change default station')
        new_action.setShortcut('Ctrl+S')
        new_action.triggered.connect(self.change_default)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        # exit menu item
        exit_action = QAction('&Exit', self)
        exit_action.setStatusTip('Exit')
        exit_action.setShortcut('Alt+F4')
        exit_action.triggered.connect(self.quit)
        file_menu.addAction(exit_action)
        
        self.show()
        
        
    def change_default(self):
        self.mySelection = SelectDefault(self)
        self.mySelection.station_changed.connect(self.update_default)  # Connect the signal to update_default()
        self.mySelection.show()
        
    def quit(self):
        self.destroy()
        
    def update_default(self,indexStation):
        self.combobox.setCurrentIndex(indexStation) 

    def send_request(self, station,mr1,mr2,time):
        if mr1 == True:
            self.radiovar = "N"
        elif mr2 == True:
            self.radiovar = "S"
        else:
            self.radiovar = "A"
        codice = stations[station]
        codice_lower = codice[0].lower()
        
        fine_stringa = "&NumMins="+str(int(time))
        stringa_api = URL_API + codice_lower + fine_stringa
        webpage_result = requests.get(stringa_api)
        dict_res = xmltodict.parse(webpage_result.content)

        try:
            my_data = dict_res['ArrayOfObjStationData']['objStationData']
            results = ""
            for diz in my_data:
                if self.radiovar == "N" and diz['Direction']=="Northbound":
                    result_iter= f"{diz['Traintype']}  in {diz['Duein']} min with destination {diz['Destination']}"
                    results = results+"\n"+result_iter
                elif self.radiovar == "S" and diz['Direction']=="Southbound":
                    result_iter=f"{diz['Traintype']}  in {diz['Duein']} min with destination {diz['Destination']}"
                    results = results+"\n"+result_iter
                elif self.radiovar =="A":
                    result_iter=f"{diz['Traintype']}  in {diz['Duein']} min with destination {diz['Destination']}"
                    results = results+"\n"+result_iter
            QMessageBox.information(None, "Train Tiiiime!", results)
        except:
            QMessageBox.warning(None, "Warning!", "There are no trains...")
        
        




#window to change default station
class SelectDefault(QWidget):
    station_changed = pyqtSignal(int)
    def __init__(self, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = main_window
        self.setWindowTitle("Set Default Station")
        self.setGeometry(100, 100, 500, 100) 
        
        layout = QVBoxLayout()
        self.label = QLabel("Please select:")
        layout.addWidget(self.label)

        self.dropdown = QComboBox()
        self.dropdown.addItems(nameStations) 
        layout.addWidget(self.dropdown)

        self.confirmB = QPushButton("Confirm")
        self.discardB = QPushButton("Discard")

        self.confirmB.clicked.connect(self.changeStation)   # call function below
        self.discardB.clicked.connect(self.close)

        layout.addWidget(self.confirmB)
        layout.addWidget(self.discardB)        
        
        self.setLayout(layout)


    # if the user confirmed the new station, then we need to save it to the defaultStation.txt file 
    def changeStation(self):
        selected_station = self.dropdown.currentText()
        indexStation = nameStations.index(selected_station) 

        with open("./defaultStation.txt", "w") as myfile:
            myfile.write(str(indexStation))

        self.main_window.update_default(indexStation)   # we also need to update the station in the main window. For this purpose we have the function update_default()
        self.station_changed.emit(indexStation)
        self.close()
        





if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


