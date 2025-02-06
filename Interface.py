#!/usr/bin/env python3
from PyQt5 import QtCore, QtGui, QtWidgets
import rospy
import cv2
import roslib
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import tensorflow as tf
from keras.models import load_model
from PyQt5.QtWidgets import QTextBrowser, QSizePolicy
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTextBrowser, QVBoxLayout, QWidget, QScrollBar
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QTimer, QCoreApplication
import pdb
from email.message import EmailMessage
import smtplib
import imghdr
from PIL import Image as im

# Init Variables
bridge = CvBridge()
image_stack = []
width = 120
height = 120
dim = (width, height)
n = 0


class StartRecThread(QtCore.QThread):
    processedText = QtCore.pyqtSignal(str)

    def scrollDown(self):
        self.textBrowser.ensureCursorVisible()        
        self.textBrowser_3.ensureCursorVisible()
        
    def sendMail(self, Frame1, Frame2,name):
        email_sender = 'elfanimalika08@gmail.com'
        email_password = 'gyrszqnrcpomczqn'
        email_receiver = 'elfanielfani81@gmail.com'
        subject = "Suspicious activity has been detected!"
        body = """
    		The following suspicious activity has been detected: """+str(name)+"""
    		
    		See images for more information.
    		"""
    		
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['subject'] = subject
        em.set_content(body)
        
        with open('5.png', 'rb') as f:
        	image_data1 = f.read()
        	image_type1 = imghdr.what(f.name)
        	image_name1 = f.name
        em.add_attachment(image_data1, maintype='image', subtype=image_type1, filename=image_name1)

        with open('6.png', 'rb') as f:
        	image_data2 = f.read()
        	image_type2 = imghdr.what(f.name)
        	image_name2 = f.name
        em.add_attachment(image_data2, maintype='image', subtype=image_type2, filename=image_name2)
          
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        	smtp.login(email_sender, email_password)
        	smtp.send_message(em)


                   
        
    def __init__(self, textBrowser, spinBox, numTab, textBrowser_3, spinBox_2 ):
        super(StartRecThread, self).__init__()
        self.textBrowser = textBrowser
        self.spinBox = spinBox
        self.textBrowser_3 = textBrowser_3
        self.spinBox_2 = spinBox_2 
        self.numTab = numTab

    def run(self):
        rospy.init_node("HAR", anonymous=True)
        rospy.loginfo("Creating the model")

        #session = tf.compat.v1.keras.backend.get_session()
        session =tf.compat.v1.keras.backend.get_session()
        if (self.numTab == 1) :
        	with session.graph.as_default():
            		tf.compat.v1.keras.backend.set_session(session)
            		model = tf.keras.models.load_model('/home/malika/Downloads/acc92_loss28.h5')
        	rospy.Subscriber("camera/rgb/image_color", Image, self.img_acquired, (session, model), queue_size=1,
                         buff_size=2 ** 24)
        	while not rospy.is_shutdown():
        	        rospy.spin()
        	                   		
        else:
        	with session.graph.as_default():
            		tf.compat.v1.keras.backend.set_session(session)
            		model = tf.keras.models.load_model('/home/malika/Downloads/best_modelS6.h5')  # dyal rima R
        	#pdb.set_trace()	
        	rospy.Subscriber("camera/rgb/image_color", Image, self.img_acquired2, (session, model), queue_size=1,
                         buff_size=2 ** 24)
        	while not rospy.is_shutdown():
        	        rospy.spin()
     
    def stop(self):
        process.terminate()
        rospy.signal_shutdown("Stop requested")


    def show_message(self, message):
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText("Suspicious activity detected!")
        msg.setIcon(QMessageBox.Warning)
        msg.setInformativeText(message)
        msg.setStyleSheet("QLabel{font-size: 24px;}")
        QTimer.singleShot(2000, lambda: msg.done(0))
        msg.exec_()

                   
    def img_acquired(self, image_msg, args):
        session = args[0]
        model = args[1]
        global n
        n = n + 1
        global image_stack
        try:
            image = bridge.imgmsg_to_cv2(image_msg, desired_encoding="passthrough")
        except CvBridgeError as e:
            print(e)
            

        if n == 5 or n == 6:
            i = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            cv2.imwrite(str(n)+".png", image)
    
        image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image / 255
        image_stack.append(image)
        if n == 9:
            n = 0
            self.img_proc(image_stack, session, model)
            image_stack = []
        self.textBrowser.append("Processing frame | Delay:%6.3f" % (rospy.Time.now() - image_msg.header.stamp).to_sec()) 
        self.scrollDown()  # Scroll down after appending the text
        rate = rospy.Rate(9/2)
        rate.sleep()

    
    def img_acquired2(self, image_msg, args):
        session = args[0]
        model = args[1]
        global n
        n = n + 1
        global image_stack
        try:
            image = bridge.imgmsg_to_cv2(image_msg, desired_encoding="passthrough")
        except CvBridgeError as e:
            print(e)
            
        if n == 5 or n == 6:
            i = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            cv2.imwrite(str(n)+".png", image)
    
    
    
        image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image / 255
        image_stack.append(image)
        if n == 9:
            n = 0
            self.img_proc2(image_stack, session, model)
            image_stack = []
        self.textBrowser_3.append("Processing frame | Delay:%6.3f" % (rospy.Time.now() - image_msg.header.stamp).to_sec())
        self.scrollDown()  # Scroll down after appending the text
        rate = rospy.Rate(9/2)
        rate.sleep()

    def img_proc(self, image_stack, session_arg, model_arg):    
        image = np.expand_dims(image_stack, axis=0)
        session = session_arg
        model = model_arg
        with session.graph.as_default():
            tf.compat.v1.keras.backend.set_session(session)
            prediction = model.predict(image)
            result = "\nResult : "
            x = np.argmax(prediction[0])            
            if x == 0:
                result += "Action: Sit     --- Score: %.2f %%" % (prediction[0][0] * 100)
                self.textBrowser.append(result)
                self.textBrowser.ensureCursorVisible()
            elif x == 1:
                result += "Action: Kick     --- Score: %.2f %%" % (prediction[0][1] * 100)
                self.textBrowser.append(result)
                self.textBrowser.ensureCursorVisible()
                msg = QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setText("Suspicious activity detected!")
                msg.setIcon(QMessageBox.Warning)
                msg.setInformativeText("Kick")
                msg.setStyleSheet("QLabel{font-size: 24px;}")
                QTimer.singleShot(2000, lambda: msg.done(0))
                msg.exec_()
                try:
                   self.sendMail(image_stack[0][5], image_stack[0][6], "Kick")
                   self.textBrowser.append("\nAn alert email has been sent.")   
                except:
                   self.textBrowser.append("An exception occurred")
                self.textBrowser.ensureCursorVisible()                             
            elif x == 2:
                result += "Action: Push     --- Score: %.2f %%" % (prediction[0][2] * 100)
                self.textBrowser.append(result)
                self.textBrowser.ensureCursorVisible()
                msg = QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setText("Suspicious activity detected!")
                msg.setIcon(QMessageBox.Warning)
                msg.setInformativeText("Push")
                msg.setStyleSheet("QLabel{font-size: 24px;}")
                QTimer.singleShot(2000, lambda: msg.done(0))
                msg.exec_()
                try:
                   self.sendMail(image_stack[0][5], image_stack[0][6], "Push")
                   self.textBrowser.append("\nAn alert email has been sent.")   
                except:
                   self.textBrowser.append("An exception occurred")
                self.textBrowser.ensureCursorVisible()                             
            elif x == 3:
                result += "Action: Touch pocket     --- Score: %.2f %%" % (prediction[0][3] * 100)
                self.textBrowser.append(result)
                self.textBrowser.ensureCursorVisible()
                msg = QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setText("Suspicious activity detected!")
                msg.setIcon(QMessageBox.Warning)
                msg.setInformativeText("Touch pocket")
                msg.setStyleSheet("QLabel{font-size: 24px;}")
                QTimer.singleShot(2000, lambda: msg.done(0))
                msg.exec_()
                try:
                   self.sendMail(image_stack[0][5], image_stack[0][6], "Touch pocket")
                   self.textBrowser.append("\nAn alert email has been sent.")   
                except:
                   self.textBrowser.append("An exception occurred")
                self.textBrowser.ensureCursorVisible()                                
            elif (x == 4):
                result += "Action: Write     --- Score: %.2f %%" % (prediction[0][4] * 100)
                self.textBrowser.append(result)
                self.textBrowser.ensureCursorVisible()
            self.textBrowser.append("-----------------------------------------------------\n")
            self.scrollDown()  
        if (self.numTab == 1) :
        	rospy.sleep(self.spinBox.value())
        else :
        	rospy.sleep(self.spinBox_2.value())
        	
        	
    def img_proc2(self, image_stack, session_arg, model_arg):
        session = session_arg
        model = model_arg
        optical_flow1=[]
        
        for i in range(len(image_stack)-1):
            dtvl1 = cv2.optflow.DualTVL1OpticalFlow_create()
            flowDTVL1 = dtvl1.calc(cv2.cvtColor((image_stack[i]*255).astype(np.uint8), cv2.COLOR_RGB2GRAY), cv2.cvtColor((image_stack[i+1]*255).astype(np.uint8), cv2.COLOR_RGB2GRAY), None)
            x, y = flowDTVL1[..., 0], flowDTVL1[..., 1]
            mag, ang = cv2.cartToPolar(x, y)
            hsv = np.zeros((120, 120, 1), dtype = np.uint8)
            hsv[..., 0] = (cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)).astype(np.uint8)
            hsv = hsv/255
            optical_flow1.append(hsv)

        optical_flow1 = np.stack(optical_flow1, axis=0)
        image = np.expand_dims(image_stack, axis=0)
        OF = np.expand_dims(optical_flow1, axis=0)
        combined=[image, OF]
        
        with session.graph.as_default():
            tf.compat.v1.keras.backend.set_session(session)
            prediction = model.predict(combined)
           
            result = "\nResult : "
            x=np.argmax(prediction[0])    
            
            if x == 0:
                result += "Action: Sit     --- Score: %.2f %%" % (prediction[0][0] * 100)
                self.textBrowser_3.append(result)
                self.textBrowser_3.ensureCursorVisible()
            elif x == 1:
                result += "Action: Kick     --- Score: %.2f %%" % (prediction[0][1] * 100)
                self.textBrowser_3.append(result)
                self.textBrowser_3.ensureCursorVisible()
                msg = QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setText("Suspicious activity detected!")
                msg.setIcon(QMessageBox.Warning)
                msg.setInformativeText("Kick")
                msg.setStyleSheet("QLabel{font-size: 24px;}")
                QTimer.singleShot(2000, lambda: msg.done(0))
                msg.exec_()
                try:
                   self.sendMail(image_stack[0][5], image_stack[0][6], "Kick")
                   self.textBrowser_3.append("\nAn alert email has been sent.")   
                except:
                   self.textBrowser_3.append("An exception occurred")
            elif x == 2:
                result += "Action: Push     --- Score: %.2f %%" % (prediction[0][2] * 100)
                self.textBrowser_3.append(result)
                self.textBrowser_3.ensureCursorVisible()
                msg = QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setText("Suspicious activity detected!")
                msg.setIcon(QMessageBox.Warning)
                msg.setInformativeText("Push")
                msg.setStyleSheet("QLabel{font-size: 24px;}")
                QTimer.singleShot(2000, lambda: msg.done(0))
                msg.exec_()
                try:
                   self.sendMail(image_stack[0][5], image_stack[0][6], "Push")
                   self.textBrowser_3.append("\nAn alert email has been sent.")   
                except:
                   self.textBrowser_3.append("An exception occurred") 
                self.textBrowser_3.ensureCursorVisible()                             
            elif x == 3:
                result += "Action: Touch pocket     --- Score: %.2f %%" % (prediction[0][3] * 100)
                self.textBrowser_3.append(result)
                self.textBrowser_3.ensureCursorVisible()
                msg = QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setText("Suspicious activity detected!")
                msg.setIcon(QMessageBox.Warning)
                msg.setInformativeText("Touch pocket")
                msg.setStyleSheet("QLabel{font-size: 24px;}")
                QTimer.singleShot(2000, lambda: msg.done(0))
                msg.exec_()
                try:
                   self.sendMail(image_stack[0][5], image_stack[0][6], "Touch pocket")
                   self.textBrowser_3.append("\nAn alert email has been sent.")   
                except:
                   self.textBrowser_3.append("An exception occurred") 
                self.textBrowser_3.ensureCursorVisible()                                
            elif (x == 4):
                result += "Action: Write     --- Score: %.2f %%" % (prediction[0][4] * 100)
                self.textBrowser_3.append(result)
                self.textBrowser_3.ensureCursorVisible()
            self.textBrowser_3.append("-----------------------------------------------------\n")
            self.scrollDown()  
        if (self.numTab == 1) :
        	rospy.sleep(self.spinBox.value())
        else :
        	rospy.sleep(self.spinBox_2.value())
        	
        	

class Ui_MainWindow(object):


    def __init__(self):
        self.start_rec_thread = None
        self.start_rec_thread2 = None
        self.session = None
        self.model = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(869, 729)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_3 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_5.addWidget(self.label_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.spinBox = QtWidgets.QSpinBox(self.tab)
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout_4.addWidget(self.spinBox)
        self.Start = QtWidgets.QPushButton(self.tab)
        self.Start.setObjectName("Start")
        self.Start.clicked.connect(self.startRec)
                
                
        self.horizontalLayout_4.addWidget(self.Start)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.scrollArea_4 = QtWidgets.QScrollArea(self.tab)
        self.scrollArea_4.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollArea_4.setObjectName("scrollArea_4")
        self.scrollAreaWidgetContents_5 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_5.setGeometry(QtCore.QRect(0, 0, 794, 547))
        self.scrollAreaWidgetContents_5.setObjectName("scrollAreaWidgetContents_5")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_5)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.textBrowser = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents_5)
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setFont(QtGui.QFont("monospace",18))
        self.gridLayout_8.addWidget(self.textBrowser, 0, 0, 1, 1)
        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_5)
        self.verticalLayout_5.addWidget(self.scrollArea_4)
        self.gridLayout_2.addLayout(self.verticalLayout_5, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_2 = QtWidgets.QLabel(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.spinBox_2 = QtWidgets.QSpinBox(self.tab_2)
        self.spinBox_2.setObjectName("spinBox_2")
        self.horizontalLayout_3.addWidget(self.spinBox_2)
        self.Start_2 = QtWidgets.QPushButton(self.tab_2)
        self.Start_2.setObjectName("Start_2")
        self.Start_2.clicked.connect(self.startRec2)
        
        self.horizontalLayout_3.addWidget(self.Start_2)
        self.gridLayout_3.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.scrollArea_3 = QtWidgets.QScrollArea(self.tab_2)
        self.scrollArea_3.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollArea_3.setObjectName("scrollArea_3")
        self.scrollAreaWidgetContents_4 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_4.setGeometry(QtCore.QRect(0, 0, 794, 547))
        self.scrollAreaWidgetContents_4.setObjectName("scrollAreaWidgetContents_4")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_4)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.textBrowser_3 = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents_4)
        self.textBrowser_3.setObjectName("textBrowser_3")
        self.textBrowser_3.setFont(QtGui.QFont("monospace",18))
        self.gridLayout_6.addWidget(self.textBrowser_3, 0, 0, 1, 1)
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_4)
        self.gridLayout_3.addWidget(self.scrollArea_3, 2, 0, 1, 1)
        self.gridLayout_7.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_3.setText(_translate("MainWindow", "Suspecious Activity Recognition : Security environment"))
        self.Start.setText(_translate("MainWindow", "Start"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "RGB "))
        self.label_2.setText(_translate("MainWindow", "Suspicious activity recognition : Security environment"))
        self.Start_2.setText(_translate("MainWindow", "Start"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "RGB + OF"))
        
        
    def startRec(self):    
    	if (self.Start.text() != "Quit") :
    		self.Start.setObjectName("Quit")
    		self.Start.setText("Quit")
    		if (self.start_rec_thread is None or not self.start_rec_thread.isRunning()):
    		   self.start_rec_thread = StartRecThread(self.textBrowser, self.spinBox, 1, self.textBrowser_3, self.spinBox_2)
    		   self.start_rec_thread.start()
    		   self.start_rec_thread.scrollDown()  # Scroll down after starting the thread
    	else :
    		exit(1)


    def startRec2(self):
    	if (self.Start_2.text() != "Quit") :
    		self.Start_2.setObjectName("Quit")
    		self.Start_2.setText("Quit")
    		if (self.start_rec_thread is None or not self.start_rec_thread2.isRunning()):
    		   self.start_rec_thread = StartRecThread(self.textBrowser, self.spinBox, 2, self.textBrowser_3, self.spinBox_2)
    		   self.start_rec_thread.start()
    		   self.start_rec_thread.scrollDown()  # Scroll down after starting the thread
    	else :
    		exit(1)


if __name__ == "__main__":
    import sys
    
    import subprocess
    # Example command: echo "Hello, World!"
    
    command = ['rosrun', 'image_view', 'image_view', 'image:=/camera/rgb/image_color']
    process = subprocess.Popen(command)



    app = QtWidgets.QApplication(sys.argv)
    rospy.init_node("HAR", anonymous=True)  # Initialize ROS node here
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook

    def my_exception_hook(exctype, value, traceback):
        # Print the error and traceback
        print(exctype, value, traceback)
        # Call the normal Exception hook after
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")







