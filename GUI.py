import sys
from PyQt5.QtWidgets import  QWidget, QGridLayout, QDialog, QLabel, QMessageBox, QVBoxLayout,QHBoxLayout,QLineEdit, QPushButton, QApplication, QSplitter, QTextEdit
import threading
import chat_utils
from chat_client_class import *
 
class Interface(QWidget):

    def __init__(self):
        super().__init__()
        self.clientthread = clientthread()        
        self.system_display = threading.Thread(target=self.system_display)
        self.peer_display = threading.Thread(target = self.peer_display)
        
        self.initUI()
        self.multi_thread()
        
    def initUI(self):

        self.setWindowTitle('LUCKCHAT')

        self.msg_display = QTextEdit()
        self.msg_display.setReadOnly(True)
        self.msg_send = QLineEdit("You can type here!")
        self.send_button = QPushButton("Send")
        self.msg_send.returnPressed.connect(self.send)
        
        layout = QVBoxLayout()
        
        layout.addWidget(self.msg_display)
        layout.addWidget(self.msg_send)
        layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.send)
        
        self.setLayout(layout)
        
        self.setGeometry(400,200,600,500)
    
    def send(self):
        text = self.msg_send.text()
        self.clientthread.client.text_ = text
        self.msg_display.append(text)
        self.msg_send.setText('')

    def multi_thread(self):
        
        self.show()
        self.clientthread.start()
        self.system_display.start()
        self.peer_display.start()
    

    def system_display(self):  
        while 1:
              if self.clientthread.client.sm.system_display != '':
                   self.msg_display.append(self.clientthread.client.sm.system_display)
                   self.clientthread.client.sm.system_display = ''
        
    def peer_display(self):
        while 1:
            if self.clientthread.client.sm.peer_display != '':
                self.msg_display.append(self.clientthread.client.sm.peer_display)
                self.clientthread.client.sm.peer_display = '' 
            
    def username(self,name):
        self.clientthread.client.text_ = name

class clientthread(threading.Thread):
    def __init__(self):
        super().__init__()
        
        import argparse
        parser = argparse.ArgumentParser(description='chat client argument')
        parser.add_argument('-d', type=str, default=None, help='server IP addr')
        args = parser.parse_args()
        self.client = Client(args)
        
    def run(self):
        
        self.client.run_chat()
        
class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.name = QLineEdit()
        self.login_button = QPushButton('login')
        name = QLabel('Please enter your name:')
        layout = QVBoxLayout()
        layout.addWidget(name)
        layout.addWidget(self.name)
        layout.addWidget(self.login_button)
        self.setLayout(layout)
        self.setWindowTitle('LUCKCHAT')
        self.login_button.clicked.connect(self.check)
        
    def check(self):
        username = self.name.text()
        if username != '':
            self.name = username
            self.accept()
           
if __name__ == '__main__':
    app = QApplication(sys.argv)
    loginwindow = Login()
    if loginwindow.exec_() == QDialog.Accepted:
        name = loginwindow.name
        chatwindow = Interface()
        chatwindow.username(name)
        chatwindow.msg_display.append(name + ', welcome to LUCKCHAT!')
        for line in menu.split('\n'):
            chatwindow.msg_display.append(line)
        sys.exit(app.exec_())
    sys.exit(app.exec_())
    
