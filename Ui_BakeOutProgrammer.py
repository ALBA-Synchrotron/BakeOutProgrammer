from __future__ import division
from PyQt4 import QtCore, QtGui, Qwt5 as Qwt
from tau.widget import TauWidget, TauMainWindow, TauValueLabel, TauValueSpinBox
from tau.widget.qwt import TauTrend
from PyTangoArchiving.widget import ContextToolBar

TEMP_ROOM = 25.
TEMP_DEFAULT = 1200.
PROGRAM_DEFAULT = [TEMP_DEFAULT, 0., -1.]
PARAMS_DEFAULT = [TEMP_DEFAULT, 0., 0., 0.]

class UiMainWindow(TauMainWindow):
    def __init__(self, parent=None, flags=0):
        TauMainWindow.__init__(self, parent, flags)
        self.setObjectName("BakeoutProgrammer")
        self.setWindowTitle("Bakeout Programmer v1.0.0a")

        #--------------------------------------------------------- centralWidget
        self.centralWidget = QtGui.QWidget(self)
        self.centralWidget.setObjectName("centralWidget")       
        self.centralWidget.setLayout(QtGui.QGridLayout())
        self.centralWidget.layout().setColumnStretch(1, 1)
        
        # #------------------------------------------------------- controllerCombo
        self.controllerCombo = QtGui.QComboBox()
        self.controllerCombo.setObjectName("controllerCombo")
        
        self.controllerState = TauValueLabel()
        self.controllerStatus = QtGui.QPushButton("Show Status")
        self.controllerStatus.setObjectName("controllerStatus")
        
        # #------------------------------------------------ end of controllerCombo
        
        # #----------------------------------------------------------- tabWidget
        self.tabWidget = QtGui.QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName("tabWidget")
#        self.tabWidget.setDisabled(True)
        
        # # #--------------------------------------------------- tabCornerWidget
        self.newProgramButton = QtGui.QPushButton("New program")
        self.newProgramButton.setObjectName("newProgramButton")        
        
        if ( QtCore.PYQT_VERSION_STR >= "4.5" ):
            tabCornerWidget = self.newProgramButton 
        else:
            tabCornerWidget = QtGui.QWidget()
            tabCornerWidget.setLayout(QtGui.QHBoxLayout())
            
            self.closeProgramButton = QtGui.QPushButton("Close program")
            self.closeProgramButton.setObjectName("closeProgramButton")
            self.closeProgramButton.hide()
            
            tabCornerWidget.layout().addWidget(self.closeProgramButton)
            tabCornerWidget.layout().addWidget(self.newProgramButton)
               
        # # #-------------------------------------------- end of tabCornerWidget

        self.tabWidget.setCornerWidget(tabCornerWidget)
        # #---------------------------------------------------- end of tabWidget
        
        self.centralWidget.layout().addWidget(QtGui.QLabel("Bakeout controller"), 0, 0)
        self.centralWidget.layout().addWidget(self.controllerCombo, 0, 1)
        self.centralWidget.layout().addWidget(self.controllerStatus, 1, 0)
        self.centralWidget.layout().addWidget(self.controllerState, 1, 1)
        self.centralWidget.layout().addWidget(self.tabWidget, 2, 0, 1, 2)#4 #1,0,1,2)
        
        self.setCentralWidget(self.centralWidget)
        #-------------------------------------------------- end of centralWidget


        #--------------------------------------------------------------- menuBar
        # self.menuBar = QtGui.QMenuBar(self.mainWindow)
        # self.menuBar.setObjectName("menuBar")
        # self.setMenuBar(self.menuBar)
        #-------------------------------------------------------- end of menuBar

        #----------------------------------------------------------- mainToolBar
#        self.mainToolBar = QtGui.QToolBar(self)
#        self.mainToolBar.setObjectName("mainToolBar")
#        self.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        #---------------------------------------------------- end of mainToolBar

#        #-------------------------------------------------------- contextToolBar        
#        self.contextToolBar = ContextToolBar()
#        self.contextToolBar.setObjectName("contextToolBar")        
#        self.contextToolBar.setIconSize(QtCore.QSize(24, 24))
#        self.addToolBar(QtCore.Qt.TopToolBarArea, self.contextToolBar)
#        #------------------------------------------------- end of contextToolBar        

#        #------------------------------------------------------------- statusBar
#        self.statusBar = QtGui.QStatusBar(self)
#        self.statusBar.setObjectName("statusBar")
#        self.statusBar.showMessage("Bakeout Programmer ready...")
#        
#        self.setStatusBar(self.statusBar)        
#        #------------------------------------------------------ end of statusBar
        
        self.metaObject().connectSlotsByName(self)
        
    # setupUi()

class UiTab(TauWidget):
    def __init__(self, parent=None, flags=0):
        TauWidget.__init__(self, parent, flags)
        self._cGroupBoxes = []
        self._cCheckBoxes = []
        self._cLimits = []
        self._cOutputs = []
        self._cTemps = []      
        self._cTempsSp = []      
                
        self.setObjectName("tab")
        self.setLayout(QtGui.QGridLayout())
        self.layout().setRowStretch(1, 1)
        self.layout().setColumnStretch(1, 1)

        #------------------------------------------------------ pressureGroupBox
        pressureGroupBox = QtGui.QGroupBox("Pressure")
        pressureGroupBox.setLayout(QtGui.QFormLayout())

        # #----------------------------------------------------- pressureCombo
        self.pressureCombo = QtGui.QComboBox()
        self.pressureCombo.setObjectName("pressureCombo")
        # #---------------------------------------------- end of pressureCombo
        
        # #-------------------------------------------------------- gaugeCombo
        self.gaugeCombo = QtGui.QComboBox()
        self.gaugeCombo.setObjectName("gaugeCombo")
        self.gaugeCombo.setDisabled(True)
        # #------------------------------------------------- end of gaugeCombo
       
        # #------------------------------------------------------ gaugeValueLayout
        gaugeValueLayout = QtGui.QHBoxLayout()
       
        # # #-------------------------------------------------------- gagueValue
        self.gaugeValue = TauValueLabel()
        self.gaugeValue.setObjectName("gaugeValue")
        self.gaugeValue.setDisabled(True)        
        # # #------------------------------------------------- end of gaugeValue
        
        gaugeValueLayout.addWidget(self.gaugeValue)
        gaugeValueLayout.addWidget(QtGui.QLabel("mbar"))
        # #----------------------------------------------- end of gaugeValueLayout
        
        pressureGroupBox.layout().addRow("Controller", self.pressureCombo)
        pressureGroupBox.layout().addRow("Gauge", self.gaugeCombo)
        pressureGroupBox.layout().addRow("Pressure", gaugeValueLayout)  
        #----------------------------------------------- end of pressureGroupBox

        #--------------------------------------------------------------- table
        self.table = QtGui.QTableWidget(1, 4)
        self.table.setObjectName("table")
        self.table.setHorizontalHeaderLabels((
                                            "Temperature [" + u"\u00B0" + "C]",
                                            "Ramp [" + u"\u00B0" + "C/min]",
                                            "Dwell time [h]", ""))
        self.table.setFixedWidth(400)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        
        for column in range(4):
            if ( column == 0 ):
                self.addButton = QtGui.QPushButton("Add")
                self.addButton.setObjectName("addButton")
                self.table.setCellWidget(0, column, self.addButton)
            elif ( column == 3 ):
                self.removeAllButton = QtGui.QPushButton("Remove all")
                self.removeAllButton.setObjectName("removeAllButton")
                self.removeAllButton.setDisabled(True)
                self.table.setCellWidget(0, column, self.removeAllButton)                
            else:
                item = QtGui.QTableWidgetItem()
                item.setFlags(QtCore.Qt.NoItemFlags)
                self.table.setItem(0, column, item)
        #---------------------------------------------------------- end of table
        
        #--------------------------------------------------------- graphGroupBox
        graphGroupBox = QtGui.QGroupBox("Graph")
        graphGroupBox.setObjectName("graphGroupBox")
        graphGroupBox.setLayout(QtGui.QGridLayout())
        
        # #----------------------------------------------------------- graphPlot
        self.graphPlot = TauTrend()
        self.graphPlot.setObjectName("graphPlot")
        self.graphPlot.setCanvasBackground(QtCore.Qt.white)
        self.graphPlot.setAxisTitle(Qwt.QwtPlot.yLeft,
                                        "Temperature [" + u"\u00B0" + "C]")
        self.graphPlot.setAxisTitle(Qwt.QwtPlot.yRight, "Pressure [mbar]")
        self.graphPlot.setAxisTitle(Qwt.QwtPlot.xBottom, "Time [h:m]")
        self.graphPlot.disconnect(self.graphPlot,
                                    QtCore.SIGNAL("legendClicked(QwtPlotItem*)"),
                                    self.graphPlot.toggleCurveState)        
        # #---------------------------------------------------- end of graphPlot
        
        graphGroupBox.layout().addWidget(self.graphPlot, 0, 0)
        #-------------------------------------------------- end of graphGroupBox
        
        #------------------------------------------------------ progressGroupBox
        progressGroupBox = QtGui.QGroupBox("Progress")
        progressGroupBox.setLayout(QtGui.QFormLayout())
        
        # #-------------------------------------------------- currentProgressBar
        self.currentProgressBar = QtGui.QProgressBar()
        self.currentProgressBar.setObjectName("currentProgressBar")
        # #------------------------------------------- end of currentProgressBar
        
        # #-------------------------------------------------- overallProgressBar
        self.overallProgressBar = QtGui.QProgressBar()
        self.overallProgressBar.setObjectName("overallProgressBar")
        # #------------------------------------------- end of overallProgressBar
        
        progressGroupBox.layout().addRow("Current", self.currentProgressBar)
        progressGroupBox.layout().addRow("Overall", self.overallProgressBar)
        #----------------------------------------------- end of progressGroupBox
        
        #----------------------------------------------------------- channelsLayout
        channelsLayout = QtGui.QHBoxLayout()
        
        # #------------------------------------------------------ channelCheckBoxes
        self.channelCheckBox1 = QtGui.QCheckBox()
        self.channelCheckBox1.setObjectName("channelCheckBox1")
        self._cCheckBoxes.append(self.channelCheckBox1)
        
        self.channelCheckBox2 = QtGui.QCheckBox()
        self.channelCheckBox2.setObjectName("channelCheckBox2")
        self._cCheckBoxes.append(self.channelCheckBox2)
        
        self.channelCheckBox3 = QtGui.QCheckBox()
        self.channelCheckBox3.setObjectName("channelCheckBox3") 
        self._cCheckBoxes.append(self.channelCheckBox3) 
        
        self.channelCheckBox4 = QtGui.QCheckBox()
        self.channelCheckBox4.setObjectName("channelCheckBox4") 
        self._cCheckBoxes.append(self.channelCheckBox4) 
        
        self.channelCheckBox5 = QtGui.QCheckBox()
        self.channelCheckBox5.setObjectName("channelCheckBox5") 
        self._cCheckBoxes.append(self.channelCheckBox5) 
        
        self.channelCheckBox6 = QtGui.QCheckBox()
        self.channelCheckBox6.setObjectName("channelCheckBox6") 
        self._cCheckBoxes.append(self.channelCheckBox6)  
               
        self.channelCheckBox7 = QtGui.QCheckBox()
        self.channelCheckBox7.setObjectName("channelCheckBox7") 
        self._cCheckBoxes.append(self.channelCheckBox7) 
        
        self.channelCheckBox8 = QtGui.QCheckBox()
        self.channelCheckBox8.setObjectName("channelCheckBox8")
        self._cCheckBoxes.append(self.channelCheckBox8)                                                         
        # #----------------------------------------------- end of channelCheckBoxes
         
        # #---------------------------------------------------------- channelTemps
        self.channelTemp1 = TauValueLabel()
        self.channelTemp1.setObjectName("channelTemp1")
        self._cTemps.append(self.channelTemp1)
        
        self.channelTemp2 = TauValueLabel()
        self.channelTemp2.setObjectName("channelTemp2")
        self._cTemps.append(self.channelTemp2) 
        
        self.channelTemp3 = TauValueLabel()
        self.channelTemp3.setObjectName("channelTemp3")
        self._cTemps.append(self.channelTemp3) 
                
        self.channelTemp4 = TauValueLabel()
        self.channelTemp4.setObjectName("channelTemp4")
        self._cTemps.append(self.channelTemp4) 
        
        self.channelTemp5 = TauValueLabel()
        self.channelTemp5.setObjectName("channelTemp5")
        self._cTemps.append(self.channelTemp5) 
        
        self.channelTemp6 = TauValueLabel()
        self.channelTemp6.setObjectName("channelTemp6")
        self._cTemps.append(self.channelTemp6)  
               
        self.channelTemp7 = TauValueLabel()
        self.channelTemp7.setObjectName("channelTemp7")
        self._cTemps.append(self.channelTemp7)
        
        self.channelTemp8 = TauValueLabel()
        self.channelTemp8.setObjectName("channelTemp8")
        self._cTemps.append(self.channelTemp8)
        
        self.channelTempSp1 = TauValueLabel()
        self.channelTempSp1.setObjectName("channelTempSp1")
        self._cTempsSp.append(self.channelTempSp1)
        
        self.channelTempSp2 = TauValueLabel()
        self.channelTempSp2.setObjectName("channelTempSp2")
        self._cTempsSp.append(self.channelTempSp2) 
        
        self.channelTempSp3 = TauValueLabel()
        self.channelTempSp3.setObjectName("channelTempSp3")
        self._cTempsSp.append(self.channelTempSp3) 
                
        self.channelTempSp4 = TauValueLabel()
        self.channelTempSp4.setObjectName("channelTempSp4")
        self._cTempsSp.append(self.channelTempSp4) 
        
        self.channelTempSp5 = TauValueLabel()
        self.channelTempSp5.setObjectName("channelTempSp5")
        self._cTempsSp.append(self.channelTempSp5) 
        
        self.channelTempSp6 = TauValueLabel()
        self.channelTempSp6.setObjectName("channelTempSp6")
        self._cTempsSp.append(self.channelTempSp6)  
               
        self.channelTempSp7 = TauValueLabel()
        self.channelTempSp7.setObjectName("channelTempSp7")
        self._cTempsSp.append(self.channelTempSp7)
        
        self.channelTempSp8 = TauValueLabel()
        self.channelTempSp8.setObjectName("channelTempSp8")
        self._cTempsSp.append(self.channelTempSp8)        
        # #--------------------------------------------------- end of channelTemps
        
        # #---------------------------------------------------------- channelOutput
        self.channelOutput1 = TauValueLabel()
        self.channelOutput1.setObjectName("channelOutput1")
        self.channelOutput1.setDisabled(True)        
        self.channelOutput1.setUseParentModel(True)        
        self._cOutputs.append(self.channelOutput1)
        
        self.channelOutput2 = TauValueLabel()
        self.channelOutput2.setObjectName("channelOutput2")
        self.channelOutput2.setDisabled(True)        
        self.channelOutput2.setUseParentModel(True)        
        self._cOutputs.append(self.channelOutput2) 
        
        self.channelOutput3 = TauValueLabel()
        self.channelOutput3.setObjectName("channelOutput3")
        self.channelOutput3.setDisabled(True)        
        self.channelOutput3.setUseParentModel(True)
        self._cOutputs.append(self.channelOutput3) 
                
        self.channelOutput4 = TauValueLabel()
        self.channelOutput4.setObjectName("channelOutput4")
        self.channelOutput4.setDisabled(True)        
        self.channelOutput4.setUseParentModel(True)
        self._cOutputs.append(self.channelOutput4) 
        
        self.channelOutput5 = TauValueLabel()
        self.channelOutput5.setObjectName("channelOutput5")
        self.channelOutput5.setDisabled(True)        
        self.channelOutput5.setUseParentModel(True)
        self._cOutputs.append(self.channelOutput5) 
        
        self.channelOutput6 = TauValueLabel()
        self.channelOutput6.setObjectName("channelOutput6")
        self.channelOutput6.setDisabled(True)        
        self.channelOutput6.setUseParentModel(True)
        self._cOutputs.append(self.channelOutput6)  
               
        self.channelOutput7 = TauValueLabel()
        self.channelOutput7.setObjectName("channelOutput7")
        self.channelOutput7.setDisabled(True)        
        self.channelOutput7.setUseParentModel(True)
        self._cOutputs.append(self.channelOutput7)
        
        self.channelOutput8 = TauValueLabel()
        self.channelOutput8.setObjectName("channelOutput8")
        self.channelOutput8.setDisabled(True)
        self.channelOutput8.setUseParentModel(True)        
        self._cOutputs.append(self.channelOutput8)
        # #--------------------------------------------------- end of channelOutputs
        
#        # #------------------------------------------------------- zoneSpinBoxes
#        self.zoneSpinBox1 = TauValueSpinBox()
#        self.zoneSpinBox1.setObjectName("zoneSpinBox1")
#        self.zoneSpinBox1.setUseParentModel(True)
##        self.zoneSpinBox1.setModel("/Output_1_Limit")        
#        self._cLimits.append(self.zoneSpinBox1)
#        
#        self.zoneSpinBox2 = TauValueSpinBox()
#        self.zoneSpinBox2.setObjectName("zoneSpinBox2")
#        self.zoneSpinBox2.setUseParentModel(True)        
##        self.zoneSpinBox2.setModel("/Output_2_Limit")
#        self._cLimits.append(self.zoneSpinBox2) 
#        
#        self.zoneSpinBox3 = TauValueSpinBox()
#        self.zoneSpinBox3.setObjectName("zoneSpinBox3")
#        self.zoneSpinBox3.setUseParentModel(True)        
##        self.zoneSpinBox3.setModel("/Output_3_Limit")
#        self._cLimits.append(self.zoneSpinBox3)
#        
#        self.zoneSpinBox4 = TauValueSpinBox()
#        self.zoneSpinBox4.setObjectName("zoneSpinBox4")
#        self.zoneSpinBox4.setUseParentModel(True)        
##        self.zoneSpinBox4.setModel("/Output_4_Limit")
#        self._cLimits.append(self.zoneSpinBox4)
#        
#        self.zoneSpinBox5 = TauValueSpinBox()
#        self.zoneSpinBox5.setObjectName("zoneSpinBox5")
#        self.zoneSpinBox5.setUseParentModel(True)        
##        self.zoneSpinBox5.setModel("/Output_5_Limit") 
#        self._cLimits.append(self.zoneSpinBox5)
#        
#        self.zoneSpinBox6 = TauValueSpinBox()
#        self.zoneSpinBox6.setObjectName("zoneSpinBox6")
#        self.zoneSpinBox6.setUseParentModel(True)        
##        self.zoneSpinBox6.setModel("/Output_6_Limit") 
#        self._cLimits.append(self.zoneSpinBox6)
#            
#        self.zoneSpinBox7 = TauValueSpinBox()
#        self.zoneSpinBox7.setObjectName("zoneSpinBox7")
#        self.zoneSpinBox7.setUseParentModel(True)        
##        self.zoneSpinBox7.setModel("/Output_7_Limit") 
#        self._cLimits.append(self.zoneSpinBox7)
#        
#        self.zoneSpinBox8 = TauValueSpinBox()
#        self.zoneSpinBox8.setObjectName("zoneSpinBox8")
#        self.zoneSpinBox8.setUseParentModel(True)        
##        self.zoneSpinBox8.setModel("/Output_8_Limit")
#        self._cLimits.append(self.zoneSpinBox8)
#        # #------------------------------------------------ end of zoneSpinBoxes

        # #-------------------------------------------------------- channelGroupBox1
        channelGroupBox1 = QtGui.QGroupBox("Channel 1")
        channelGroupBox1.setLayout(QtGui.QGridLayout())
        channelGroupBox1.layout().addWidget(QtGui.QLabel("Select"), 0, 0)
        channelGroupBox1.layout().addWidget(self.channelCheckBox1, 0, 1)
        channelGroupBox1.layout().addWidget(QtGui.QLabel("Temp."), 1, 0)        
        channelGroupBox1.layout().addWidget(self.channelTemp1, 1, 1)
        channelGroupBox1.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 1, 2)        
        channelGroupBox1.layout().addWidget(QtGui.QLabel("TSet"), 2, 0)        
        channelGroupBox1.layout().addWidget(self.channelTempSp1, 2, 1)
        channelGroupBox1.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 2, 2)        
        channelGroupBox1.layout().addWidget(QtGui.QLabel("Output"), 3, 0)         
        channelGroupBox1.layout().addWidget(self.channelOutput1, 3, 1)
        channelGroupBox1.layout().addWidget(QtGui.QLabel("%"), 3, 2)        
        self._cGroupBoxes.append(channelGroupBox1)
        # #------------------------------------------------ end of channelGroupBox1

        # #-------------------------------------------------------- channelGroupBox2
        channelGroupBox2 = QtGui.QGroupBox("Channel 2")
        channelGroupBox2.setLayout(QtGui.QGridLayout())
        channelGroupBox2.layout().addWidget(QtGui.QLabel("Select"), 0, 0)
        channelGroupBox2.layout().addWidget(self.channelCheckBox2, 0, 1)
        channelGroupBox2.layout().addWidget(QtGui.QLabel("Temp."), 1, 0)        
        channelGroupBox2.layout().addWidget(self.channelTemp2, 1, 1)
        channelGroupBox2.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 1, 2)        
        channelGroupBox2.layout().addWidget(QtGui.QLabel("TSet"), 2, 0)        
        channelGroupBox2.layout().addWidget(self.channelTempSp2, 2, 1)
        channelGroupBox2.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 2, 2)        
        channelGroupBox2.layout().addWidget(QtGui.QLabel("Output"), 3, 0)         
        channelGroupBox2.layout().addWidget(self.channelOutput2, 3, 1)
        channelGroupBox2.layout().addWidget(QtGui.QLabel("%"), 3, 2)        
        self._cGroupBoxes.append(channelGroupBox2)      
        # #------------------------------------------------ end of channelGroupBox2        

        # #-------------------------------------------------------- channelGroupBox3
        channelGroupBox3 = QtGui.QGroupBox("Channel 3")
        channelGroupBox3.setLayout(QtGui.QGridLayout())
        channelGroupBox3.layout().addWidget(QtGui.QLabel("Select"), 0, 0)
        channelGroupBox3.layout().addWidget(self.channelCheckBox3, 0, 1)
        channelGroupBox3.layout().addWidget(QtGui.QLabel("Temp."), 1, 0)        
        channelGroupBox3.layout().addWidget(self.channelTemp3, 1, 1)
        channelGroupBox3.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 1, 2)        
        channelGroupBox3.layout().addWidget(QtGui.QLabel("TSet"), 2, 0)        
        channelGroupBox3.layout().addWidget(self.channelTempSp3, 2, 1)
        channelGroupBox3.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 2, 2)        
        channelGroupBox3.layout().addWidget(QtGui.QLabel("Output"), 3, 0)         
        channelGroupBox3.layout().addWidget(self.channelOutput3, 3, 1)
        channelGroupBox3.layout().addWidget(QtGui.QLabel("%"), 3, 2)        
        self._cGroupBoxes.append(channelGroupBox3)       
        # #------------------------------------------------ end of channelGroupBox3
        
        # #-------------------------------------------------------- channelGroupBox4        
        channelGroupBox4 = QtGui.QGroupBox("Channel 4")
        channelGroupBox4.setLayout(QtGui.QGridLayout())
        channelGroupBox4.layout().addWidget(QtGui.QLabel("Select"), 0, 0)
        channelGroupBox4.layout().addWidget(self.channelCheckBox4, 0, 1)
        channelGroupBox4.layout().addWidget(QtGui.QLabel("Temp."), 1, 0)        
        channelGroupBox4.layout().addWidget(self.channelTemp4, 1, 1)
        channelGroupBox4.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 1, 2)        
        channelGroupBox4.layout().addWidget(QtGui.QLabel("TSet"), 2, 0)        
        channelGroupBox4.layout().addWidget(self.channelTempSp4, 2, 1)
        channelGroupBox4.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 2, 2)        
        channelGroupBox4.layout().addWidget(QtGui.QLabel("Output"), 3, 0)         
        channelGroupBox4.layout().addWidget(self.channelOutput4, 3, 1)
        channelGroupBox4.layout().addWidget(QtGui.QLabel("%"), 3, 2)        
        self._cGroupBoxes.append(channelGroupBox4)        
        # #------------------------------------------------ end of channelGroupBox4        
       
        # #-------------------------------------------------------- channelGroupBox5       
        channelGroupBox5 = QtGui.QGroupBox("Channel 5")
        channelGroupBox5.setLayout(QtGui.QGridLayout())
        channelGroupBox5.layout().addWidget(QtGui.QLabel("Select"), 0, 0)
        channelGroupBox5.layout().addWidget(self.channelCheckBox5, 0, 1)
        channelGroupBox5.layout().addWidget(QtGui.QLabel("Temp."), 1, 0)        
        channelGroupBox5.layout().addWidget(self.channelTemp5, 1, 1)
        channelGroupBox5.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 1, 2)        
        channelGroupBox5.layout().addWidget(QtGui.QLabel("TSet"), 2, 0)        
        channelGroupBox5.layout().addWidget(self.channelTempSp5, 2, 1)
        channelGroupBox5.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 2, 2)        
        channelGroupBox5.layout().addWidget(QtGui.QLabel("Output"), 3, 0)         
        channelGroupBox5.layout().addWidget(self.channelOutput5, 3, 1)
        channelGroupBox5.layout().addWidget(QtGui.QLabel("%"), 3, 2)        
        self._cGroupBoxes.append(channelGroupBox5)        
        # #------------------------------------------------ end of channelGroupBox5        
        
        # #-------------------------------------------------------- channelGroupBox6        
        channelGroupBox6 = QtGui.QGroupBox("Channel 6")
        channelGroupBox6.setLayout(QtGui.QGridLayout())
        channelGroupBox6.layout().addWidget(QtGui.QLabel("Select"), 0, 0)
        channelGroupBox6.layout().addWidget(self.channelCheckBox6, 0, 1)
        channelGroupBox6.layout().addWidget(QtGui.QLabel("Temp."), 1, 0)        
        channelGroupBox6.layout().addWidget(self.channelTemp6, 1, 1)
        channelGroupBox6.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 1, 2)        
        channelGroupBox6.layout().addWidget(QtGui.QLabel("TSet"), 2, 0)        
        channelGroupBox6.layout().addWidget(self.channelTempSp6, 2, 1)
        channelGroupBox6.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 2, 2)        
        channelGroupBox6.layout().addWidget(QtGui.QLabel("Output"), 3, 0)         
        channelGroupBox6.layout().addWidget(self.channelOutput6, 3, 1)
        channelGroupBox6.layout().addWidget(QtGui.QLabel("%"), 3, 2)        
        self._cGroupBoxes.append(channelGroupBox6)        
        # #------------------------------------------------ end of channelGroupBox6        
        
        # #-------------------------------------------------------- channelGroupBox7        
        channelGroupBox7 = QtGui.QGroupBox("Channel 7")
        channelGroupBox7.setLayout(QtGui.QGridLayout())
        channelGroupBox7.layout().addWidget(QtGui.QLabel("Select"), 0, 0)
        channelGroupBox7.layout().addWidget(self.channelCheckBox7, 0, 1)
        channelGroupBox7.layout().addWidget(QtGui.QLabel("Temp."), 1, 0)        
        channelGroupBox7.layout().addWidget(self.channelTemp7, 1, 1)
        channelGroupBox7.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 1, 2)        
        channelGroupBox7.layout().addWidget(QtGui.QLabel("TSet"), 2, 0)        
        channelGroupBox7.layout().addWidget(self.channelTempSp7, 2, 1)
        channelGroupBox7.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 2, 2)        
        channelGroupBox7.layout().addWidget(QtGui.QLabel("Output"), 3, 0)         
        channelGroupBox7.layout().addWidget(self.channelOutput7, 3, 1)
        channelGroupBox7.layout().addWidget(QtGui.QLabel("%"), 3, 2)        
        self._cGroupBoxes.append(channelGroupBox7)        
        # #------------------------------------------------ end of channelGroupBox7        

        # #-------------------------------------------------------- channelGroupBox8
        channelGroupBox8 = QtGui.QGroupBox("Channel 8")
        channelGroupBox8.setLayout(QtGui.QGridLayout())
        channelGroupBox8.layout().addWidget(QtGui.QLabel("Select"), 0, 0)
        channelGroupBox8.layout().addWidget(self.channelCheckBox8, 0, 1)
        channelGroupBox8.layout().addWidget(QtGui.QLabel("Temp."), 1, 0)        
        channelGroupBox8.layout().addWidget(self.channelTemp8, 1, 1)
        channelGroupBox8.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 1, 2)        
        channelGroupBox8.layout().addWidget(QtGui.QLabel("TSet"), 2, 0)        
        channelGroupBox8.layout().addWidget(self.channelTempSp8, 2, 1)
        channelGroupBox8.layout().addWidget(QtGui.QLabel(u"\u00B0" + "C"), 2, 2)        
        channelGroupBox8.layout().addWidget(QtGui.QLabel("Output"), 3, 0)         
        channelGroupBox8.layout().addWidget(self.channelOutput8, 3, 1)
        channelGroupBox8.layout().addWidget(QtGui.QLabel("%"), 3, 2)        
        self._cGroupBoxes.append(channelGroupBox8)
        # #------------------------------------------------ end of channelGroupBox8
         
        channelsLayout.addWidget(channelGroupBox1)
        channelsLayout.addWidget(channelGroupBox2)
        channelsLayout.addWidget(channelGroupBox3)
        channelsLayout.addWidget(channelGroupBox4)
        channelsLayout.addWidget(channelGroupBox5)
        channelsLayout.addWidget(channelGroupBox6)
        channelsLayout.addWidget(channelGroupBox7)
        channelsLayout.addWidget(channelGroupBox8)
        #---------------------------------------------------- end of channelsLayout
        
        #--------------------------------------------------------- buttonsLayout
        buttonsLayout = QtGui.QHBoxLayout()
        
        # #---------------------------------------------------------- saveButton
        self.saveButton = QtGui.QPushButton("Save")
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setSizePolicy(
                            self.saveButton.sizePolicy().horizontalPolicy(),
                            QtGui.QSizePolicy.MinimumExpanding)
        self.saveButton.setDisabled(True)        
        # #--------------------------------------------------- end of saveButton
        
        # #--------------------------------------------------------- startButton
        self.startButton = QtGui.QPushButton("Start")
        self.startButton.setObjectName("startButton")       
        self.startButton.setSizePolicy(
                            self.saveButton.sizePolicy().horizontalPolicy(),
                            self.saveButton.sizePolicy().verticalPolicy())
        self.startButton.setDisabled(True)
        # #-------------------------------------------------- end of startButton

        # #---------------------------------------------------------- stopButton
        self.stopButton = QtGui.QPushButton("Stop")
        self.stopButton.setObjectName("stopButton")
        self.stopButton.setSizePolicy(
                            self.saveButton.sizePolicy().horizontalPolicy(),
                            self.saveButton.sizePolicy().verticalPolicy())
        self.stopButton.setDisabled(True)
        # #--------------------------------------------------- end of stopButton
        
        buttonsLayout.addWidget(self.saveButton)
        buttonsLayout.addWidget(self.startButton)
        buttonsLayout.addWidget(self.stopButton)        
        #-------------------------------------------------- end of buttonsLayout
        
        self.layout().addWidget(pressureGroupBox, 0, 0)
        self.layout().addWidget(graphGroupBox, 0, 1, 4, 1)
        self.layout().addWidget(self.table, 1, 0)
        self.layout().addLayout(buttonsLayout, 2, 0)
        self.layout().addWidget(progressGroupBox, 3, 0)
        self.layout().addLayout(channelsLayout, 4, 0, 1, 2)
        
        self.metaObject().connectSlotsByName(self)
        
#    setupUi()
