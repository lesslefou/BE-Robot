from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QRadioButton, QLabel
from PyQt5.QtGui import QColor
import sys
from Common import *

#position = S_GetCurrentPosition()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Robot')
        self.resize(1200, 800)

        # Création du widget central
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        left_widget = QWidget(central_widget)
        left_widget.setGeometry(0, 0, 900, 800)
        left_widget.setStyleSheet("background-color: green;")        
        
        right_widget = QWidget(central_widget)
        #right_widget.setTitle("configuration")
        right_widget.setGeometry(900, 0, 300, 200)
        #right_widget.setStyleSheet("background-color: red;")
        
        #création d'un layout vertical pour la partie gauche
        left_layout = QVBoxLayout(left_widget)
        btn_layout = QVBoxLayout(right_widget)
        
        btn_layout.addWidget(QLabel('coucou'))

        # Ajout des boutons au layout
        button1 = QPushButton('Ouvrir la communication du robot')
        button2 = QPushButton('Fermer la communication du robot')
        button3 = QPushButton('Bouton 3')
        btn_layout.addWidget(button1)
        btn_layout.addWidget(button2)
        btn_layout.addWidget(button3)
        
        '''btn1 = QPushButton('je suis à gauche')
        left_layout.addWidget(btn1)'''
        
        liste_speed = ['Very Slow', 'Slow', 'Medium', 'Fast']
        for speed in liste_speed:
            btn_layout.addWidget(QRadioButton(speed))
        
        # Connexion du signal clicked du bouton 1 à la fonction mon_slot
        button1.clicked.connect(S_Open_Communication)
        #button2.clicked.connect(S_GetCurrentPosition())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
    


'''
boutons à mettre:
        - EMVCo (sa figure)
        - NFC 
        - Maillage
'''
    
    
    
    
    
    
    
    
    
    
    
    
    