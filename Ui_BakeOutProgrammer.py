from __future__ import division
from PyQt4 import QtCore, QtGui, Qwt5 as Qwt
from tau.widget import TauValueLabel, TauValueSpinBox
from tau.widget.qwt import TauTrend
from PyTangoArchiving.widget import ContextToolBar

TEMP_ROOM = 25.
TEMP_DEFAULT = 1200.
PROGRAM_DEFAULT = [TEMP_DEFAULT, 0., -1.]
PARAMS_DEFAULT = [TEMP_DEFAULT, 0., 0., 0.]

class UiMainWindow():
    def setupUi(self, parent):        
        parent.setObjectName("BakeoutProgrammer")
        parent.setWindowTitle("Bakeout Programmer v1.0.0a")

        #--------------------------------------------------------- centralWidget
        parent.centralWidget = QtGui.QWidget(parent)
        parent.centralWidget.setObjectName("centralWidget")       
        parent.centralWidget.setLayout(QtGui.QGridLayout())
        parent.centralWidget.layout().setColumnStretch(1, 1)
        
        # #------------------------------------------------------- controllerCombo
        parent.controllerCombo = QtGui.QComboBox()
        parent.controllerCombo.setObjectName("controllerCombo")
        # #------------------------------------------------ end of controllerCombo
        
        # #----------------------------------------------------------- tabWidget
        parent.tabWidget = QtGui.QTabWidget(parent.centralWidget)
        parent.tabWidget.setObjectName("tabWidget")
#        parent.tabWidget.setDisabled(True)
        
        # # #--------------------------------------------------- tabCornerWidget
        parent.newProgramButton = QtGui.QPushButton("New program")
        parent.newProgramButton.setObjectName("newProgramButton")        
        
        if ( QtCore.PYQT_VERSION_STR >= "4.5" ):
            tabCornerWidget = parent.newProgramButton 
        else:
            tabCornerWidget = QtGui.QWidget()
            tabCornerWidget.setLayout(QtGui.QHBoxLayout())
            
            parent.closeProgramButton = QtGui.QPushButton("Close program")
            parent.closeProgramButton.setObjectName("closeProgramButton")
            parent.closeProgramButton.hide()
            
            tabCornerWidget.layout().addWidget(parent.closeProgramButton)
            tabCornerWidget.layout().addWidget(parent.newProgramButton)
               
        # # #-------------------------------------------- end of tabCornerWidget

        parent.tabWidget.setCornerWidget(tabCornerWidget)
        # #---------------------------------------------------- end of tabWidget
        
        parent.centralWidget.layout().addWidget(QtGui.QLabel("Bakeout controller"), 0, 0)
        parent.centralWidget.layout().addWidget(parent.controllerCombo, 0, 1)
        parent.centralWidget.layout().addWidget(parent.tabWidget, 1, 0, 1, 2)        
        
        parent.setCentralWidget(parent.centralWidget)
        #-------------------------------------------------- end of centralWidget


        #--------------------------------------------------------------- menuBar
        # parent.menuBar = QtGui.QMenuBar(parent.mainWindow)
        # parent.menuBar.setObjectName("menuBar")
        # parent.setMenuBar(parent.menuBar)
        #-------------------------------------------------------- end of menuBar

        #----------------------------------------------------------- mainToolBar
#        parent.mainToolBar = QtGui.QToolBar(parent)
#        parent.mainToolBar.setObjectName("mainToolBar")
#        parent.addToolBar(QtCore.Qt.TopToolBarArea, parent.mainToolBar)
        #---------------------------------------------------- end of mainToolBar

        #-------------------------------------------------------- contextToolBar        
        parent.contextToolBar = ContextToolBar()
        parent.contextToolBar.setObjectName("contextToolBar")        
        parent.contextToolBar.setIconSize(QtCore.QSize(24, 24))
        parent.addToolBar(QtCore.Qt.TopToolBarArea, parent.contextToolBar)
        #------------------------------------------------- end of contextToolBar        

        #------------------------------------------------------------- statusBar
        parent.statusBar = QtGui.QStatusBar(parent)
        parent.statusBar.setObjectName("statusBar")
        parent.statusBar.showMessage("Bakeout Programmer ready...")
        
        parent.setStatusBar(parent.statusBar)        
        #------------------------------------------------------ end of statusBar
        
        parent.metaObject().connectSlotsByName(parent)
        
    # setupUi()

class UiTab():
    def setupUi(self, parent):
        parent._zGBoxes = []
        parent._zCBoxes = []
        parent._zSBoxes = []
        parent._zValues = []        
                
        parent.setObjectName("tab")
        parent.setLayout(QtGui.QGridLayout())
        parent.layout().setRowStretch(1, 1)
        parent.layout().setColumnStretch(1, 1)

        #-------------------------------------------------------- pressureLayout
        pressureLayout = QtGui.QFormLayout()

        # #------------------------------------------------------- pressureCombo
        parent.pressureCombo = QtGui.QComboBox()
        parent.pressureCombo.setObjectName("pressureCombo")
        # #------------------------------------------------ end of pressureCombo

        # #---------------------------------------------------------- gaugeCombo
        parent.gaugeCombo = QtGui.QComboBox()
        parent.gaugeCombo.setObjectName("gaugeCombo")
        parent.gaugeCombo.setDisabled(True)
        # #--------------------------------------------------- end of gaugeCombo
        
        pressureLayout.addRow("Pressure controller", parent.pressureCombo)
        pressureLayout.addRow("Pressure gauge", parent.gaugeCombo)     
        #----------------------------------------------- end of pressureLayout

        #--------------------------------------------------------------- table
        parent.table = QtGui.QTableWidget(1, 4)
        parent.table.setObjectName("table")
        parent.table.setHorizontalHeaderLabels((
                                            "Temperature [" + u"\u00B0" + "C]",
                                            "Ramp [" + u"\u00B0" + "C/min]",
                                            "Dwell time [h]", ""))
        parent.table.setFixedWidth(400)
        parent.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        
        for column in range(4):
            if ( column == 0 ):
                parent.addButton = QtGui.QPushButton("Add")
                parent.addButton.setObjectName("addButton")
                parent.table.setCellWidget(0, column, parent.addButton)
            elif ( column == 3 ):
                parent.removeAllButton = QtGui.QPushButton("Remove all")
                parent.removeAllButton.setObjectName("removeAllButton")
                parent.removeAllButton.setDisabled(True)
                parent.table.setCellWidget(0, column, parent.removeAllButton)                
            else:
                item = QtGui.QTableWidgetItem()
                item.setFlags(QtCore.Qt.NoItemFlags)
                parent.table.setItem(0, column, item)
        #---------------------------------------------------------- end of table
        
        #--------------------------------------------------------- graphGroupBox
        graphGroupBox = QtGui.QGroupBox("Graph")
        graphGroupBox.setObjectName("graphGroupBox")
        graphGroupBox.setLayout(QtGui.QGridLayout())
        
        # #----------------------------------------------------------- graphPlot
        parent.graphPlot = TauTrend()
        parent.graphPlot.setObjectName("graphPlot")
        parent.graphPlot.setCanvasBackground(QtCore.Qt.white)
        parent.graphPlot.setAxisTitle(Qwt.QwtPlot.yLeft,
                                        "Temperature [" + u"\u00B0" + "C]")
        parent.graphPlot.setAxisTitle(Qwt.QwtPlot.yRight, "Pressure [mbar]")
        parent.graphPlot.setAxisTitle(Qwt.QwtPlot.xBottom, "Time [h:m]")
        parent.graphPlot.disconnect(parent.graphPlot,
                                    QtCore.SIGNAL("legendClicked(QwtPlotItem*)"),
                                    parent.graphPlot.toggleCurveState)        
        # #---------------------------------------------------- end of graphPlot
        
        graphGroupBox.layout().addWidget(parent.graphPlot, 0, 0)
        #-------------------------------------------------- end of graphGroupBox
        
        #------------------------------------------------------ progressGroupBox
        progressGroupBox = QtGui.QGroupBox("Progress")
        progressGroupBox.setLayout(QtGui.QFormLayout())
        
        # #-------------------------------------------------- currentProgressBar
        parent.currentProgressBar = QtGui.QProgressBar()
        parent.currentProgressBar.setObjectName("currentProgressBar")
        # #------------------------------------------- end of currentProgressBar
        
        # #-------------------------------------------------- overallProgressBar
        parent.overallProgressBar = QtGui.QProgressBar()
        parent.overallProgressBar.setObjectName("overallProgressBar")
        # #------------------------------------------- end of overallProgressBar
        
        progressGroupBox.layout().addRow("Current", parent.currentProgressBar)
        progressGroupBox.layout().addRow("Overall", parent.overallProgressBar)
        #----------------------------------------------- end of progressGroupBox
        
        #----------------------------------------------------------- zonesLayout
        zonesLayout = QtGui.QGridLayout()
        
        # #------------------------------------------------------ zoneCheckBoxes
        parent.zoneCheckBox1 = QtGui.QCheckBox()
        parent.zoneCheckBox1.setObjectName("zoneCheckBox1")
        parent._zCBoxes.append(parent.zoneCheckBox1)
        
        parent.zoneCheckBox2 = QtGui.QCheckBox()
        parent.zoneCheckBox2.setObjectName("zoneCheckBox2")
        parent._zCBoxes.append(parent.zoneCheckBox2)
        
        parent.zoneCheckBox3 = QtGui.QCheckBox()
        parent.zoneCheckBox3.setObjectName("zoneCheckBox3") 
        parent._zCBoxes.append(parent.zoneCheckBox3) 
        
        parent.zoneCheckBox4 = QtGui.QCheckBox()
        parent.zoneCheckBox4.setObjectName("zoneCheckBox4") 
        parent._zCBoxes.append(parent.zoneCheckBox4) 
        
        parent.zoneCheckBox5 = QtGui.QCheckBox()
        parent.zoneCheckBox5.setObjectName("zoneCheckBox5") 
        parent._zCBoxes.append(parent.zoneCheckBox5) 
        
        parent.zoneCheckBox6 = QtGui.QCheckBox()
        parent.zoneCheckBox6.setObjectName("zoneCheckBox6") 
        parent._zCBoxes.append(parent.zoneCheckBox6)  
               
        parent.zoneCheckBox7 = QtGui.QCheckBox()
        parent.zoneCheckBox7.setObjectName("zoneCheckBox7") 
        parent._zCBoxes.append(parent.zoneCheckBox7) 
        
        parent.zoneCheckBox8 = QtGui.QCheckBox()
        parent.zoneCheckBox8.setObjectName("zoneCheckBox8")
        parent._zCBoxes.append(parent.zoneCheckBox8)                                                         
        # #----------------------------------------------- end of zoneCheckBoxes
        
        # #---------------------------------------------------------- zoneValues
        parent.zoneValue1 = TauValueLabel()
        parent.zoneValue1.setObjectName("zoneValue1")
        parent.zoneValue1.setDisabled(True)        
        parent.zoneValue1.setUseParentModel(True)        
        parent._zValues.append(parent.zoneValue1)
        
        parent.zoneValue2 = TauValueLabel()
        parent.zoneValue2.setObjectName("zoneValue2")
        parent.zoneValue2.setDisabled(True)        
        parent.zoneValue2.setUseParentModel(True)        
        parent._zValues.append(parent.zoneValue2) 
        
        parent.zoneValue3 = TauValueLabel()
        parent.zoneValue3.setObjectName("zoneValue3")
        parent.zoneValue3.setDisabled(True)        
        parent.zoneValue3.setUseParentModel(True)
        parent._zValues.append(parent.zoneValue3) 
                
        parent.zoneValue4 = TauValueLabel()
        parent.zoneValue4.setObjectName("zoneValue4")
        parent.zoneValue4.setDisabled(True)        
        parent.zoneValue4.setUseParentModel(True)
        parent._zValues.append(parent.zoneValue4) 
        
        parent.zoneValue5 = TauValueLabel()
        parent.zoneValue5.setObjectName("zoneValue5")
        parent.zoneValue5.setDisabled(True)        
        parent.zoneValue5.setUseParentModel(True)
        parent._zValues.append(parent.zoneValue5) 
        
        parent.zoneValue6 = TauValueLabel()
        parent.zoneValue6.setObjectName("zoneValue6")
        parent.zoneValue6.setDisabled(True)        
        parent.zoneValue6.setUseParentModel(True)
        parent._zValues.append(parent.zoneValue6)  
               
        parent.zoneValue7 = TauValueLabel()
        parent.zoneValue7.setObjectName("zoneValue7")
        parent.zoneValue7.setDisabled(True)        
        parent.zoneValue7.setUseParentModel(True)
        parent._zValues.append(parent.zoneValue7)
        
        parent.zoneValue8 = TauValueLabel()
        parent.zoneValue8.setObjectName("zoneValue8")
        parent.zoneValue8.setDisabled(True)
        parent.zoneValue8.setUseParentModel(True)        
        parent._zValues.append(parent.zoneValue8)
        # #--------------------------------------------------- end of zoneValues
        
        # #------------------------------------------------------ zoneValueLayouts
        zoneValue1Layout = QtGui.QHBoxLayout()
        zoneValue1Layout.addWidget(parent.zoneValue1)
        zoneValue1Layout.addWidget(QtGui.QLabel("%"))
        
        zoneValue2Layout = QtGui.QHBoxLayout()
        zoneValue2Layout.addWidget(parent.zoneValue2)
        zoneValue2Layout.addWidget(QtGui.QLabel("%"))
        
        zoneValue3Layout = QtGui.QHBoxLayout()
        zoneValue3Layout.addWidget(parent.zoneValue3)
        zoneValue3Layout.addWidget(QtGui.QLabel("%"))
        
        zoneValue4Layout = QtGui.QHBoxLayout()
        zoneValue4Layout.addWidget(parent.zoneValue4)
        zoneValue4Layout.addWidget(QtGui.QLabel("%"))
        
        zoneValue5Layout = QtGui.QHBoxLayout()
        zoneValue5Layout.addWidget(parent.zoneValue5)
        zoneValue5Layout.addWidget(QtGui.QLabel("%"))
        
        zoneValue6Layout = QtGui.QHBoxLayout()
        zoneValue6Layout.addWidget(parent.zoneValue6)
        zoneValue6Layout.addWidget(QtGui.QLabel("%"))
        
        zoneValue7Layout = QtGui.QHBoxLayout()
        zoneValue7Layout.addWidget(parent.zoneValue7)
        zoneValue7Layout.addWidget(QtGui.QLabel("%"))
        
        zoneValue8Layout = QtGui.QHBoxLayout()
        zoneValue8Layout.addWidget(parent.zoneValue8)
        zoneValue8Layout.addWidget(QtGui.QLabel("%"))
        # #----------------------------------------------- end of zoneValueLayouts
        
#        # #------------------------------------------------------- zoneSpinBoxes
#        parent.zoneSpinBox1 = TauValueSpinBox()
#        parent.zoneSpinBox1.setObjectName("zoneSpinBox1")
#        parent.zoneSpinBox1.setUseParentModel(True)
##        parent.zoneSpinBox1.setModel("/Output_1_Limit")        
#        parent._zSBoxes.append(parent.zoneSpinBox1)
#        
#        parent.zoneSpinBox2 = TauValueSpinBox()
#        parent.zoneSpinBox2.setObjectName("zoneSpinBox2")
#        parent.zoneSpinBox2.setUseParentModel(True)        
##        parent.zoneSpinBox2.setModel("/Output_2_Limit")
#        parent._zSBoxes.append(parent.zoneSpinBox2) 
#        
#        parent.zoneSpinBox3 = TauValueSpinBox()
#        parent.zoneSpinBox3.setObjectName("zoneSpinBox3")
#        parent.zoneSpinBox3.setUseParentModel(True)        
##        parent.zoneSpinBox3.setModel("/Output_3_Limit")
#        parent._zSBoxes.append(parent.zoneSpinBox3)
#        
#        parent.zoneSpinBox4 = TauValueSpinBox()
#        parent.zoneSpinBox4.setObjectName("zoneSpinBox4")
#        parent.zoneSpinBox4.setUseParentModel(True)        
##        parent.zoneSpinBox4.setModel("/Output_4_Limit")
#        parent._zSBoxes.append(parent.zoneSpinBox4)
#        
#        parent.zoneSpinBox5 = TauValueSpinBox()
#        parent.zoneSpinBox5.setObjectName("zoneSpinBox5")
#        parent.zoneSpinBox5.setUseParentModel(True)        
##        parent.zoneSpinBox5.setModel("/Output_5_Limit") 
#        parent._zSBoxes.append(parent.zoneSpinBox5)
#        
#        parent.zoneSpinBox6 = TauValueSpinBox()
#        parent.zoneSpinBox6.setObjectName("zoneSpinBox6")
#        parent.zoneSpinBox6.setUseParentModel(True)        
##        parent.zoneSpinBox6.setModel("/Output_6_Limit") 
#        parent._zSBoxes.append(parent.zoneSpinBox6)
#            
#        parent.zoneSpinBox7 = TauValueSpinBox()
#        parent.zoneSpinBox7.setObjectName("zoneSpinBox7")
#        parent.zoneSpinBox7.setUseParentModel(True)        
##        parent.zoneSpinBox7.setModel("/Output_7_Limit") 
#        parent._zSBoxes.append(parent.zoneSpinBox7)
#        
#        parent.zoneSpinBox8 = TauValueSpinBox()
#        parent.zoneSpinBox8.setObjectName("zoneSpinBox8")
#        parent.zoneSpinBox8.setUseParentModel(True)        
##        parent.zoneSpinBox8.setModel("/Output_8_Limit")
#        parent._zSBoxes.append(parent.zoneSpinBox8)
#        # #------------------------------------------------ end of zoneSpinBoxes
#        
#        # #------------------------------------------------------ zoneSpinBoxLayouts
#        zoneSpinBox1Layout = QtGui.QHBoxLayout()
#        zoneSpinBox1Layout.addWidget(parent.zoneSpinBox1)
#        zoneSpinBox1Layout.addWidget(QtGui.QLabel("%"))
#        
#        zoneSpinBox2Layout = QtGui.QHBoxLayout()
#        zoneSpinBox2Layout.addWidget(parent.zoneSpinBox2)
#        zoneSpinBox2Layout.addWidget(QtGui.QLabel("%"))
#        
#        zoneSpinBox3Layout = QtGui.QHBoxLayout()
#        zoneSpinBox3Layout.addWidget(parent.zoneSpinBox3)
#        zoneSpinBox3Layout.addWidget(QtGui.QLabel("%"))
#        
#        zoneSpinBox4Layout = QtGui.QHBoxLayout()
#        zoneSpinBox4Layout.addWidget(parent.zoneSpinBox4)
#        zoneSpinBox4Layout.addWidget(QtGui.QLabel("%"))
#        
#        zoneSpinBox5Layout = QtGui.QHBoxLayout()
#        zoneSpinBox5Layout.addWidget(parent.zoneSpinBox5)
#        zoneSpinBox5Layout.addWidget(QtGui.QLabel("%"))
#        
#        zoneSpinBox6Layout = QtGui.QHBoxLayout()
#        zoneSpinBox6Layout.addWidget(parent.zoneSpinBox6)
#        zoneSpinBox6Layout.addWidget(QtGui.QLabel("%"))
#        
#        zoneSpinBox7Layout = QtGui.QHBoxLayout()
#        zoneSpinBox7Layout.addWidget(parent.zoneSpinBox7)
#        zoneSpinBox7Layout.addWidget(QtGui.QLabel("%"))
#        
#        zoneSpinBox8Layout = QtGui.QHBoxLayout()
#        zoneSpinBox8Layout.addWidget(parent.zoneSpinBox8)
#        zoneSpinBox8Layout.addWidget(QtGui.QLabel("%"))                                                        
#        # #----------------------------------------------- end of zoneSpinBoxLayouts
          
        # #-------------------------------------------------------- zoneGroupBox1
        zoneGroupBox1 = QtGui.QGroupBox()
        zoneGroupBox1.setLayout(QtGui.QFormLayout())
        zoneGroupBox1.layout().addRow("Zone 1", parent.zoneCheckBox1)
        zoneGroupBox1.layout().addRow("Output", zoneValue1Layout)
#        zoneGroupBox1.layout().addRow("Limit", zoneSpinBox1Layout)
        parent._zGBoxes.append(zoneGroupBox1)
        # #------------------------------------------------ end of zoneGroupBox1

        # #-------------------------------------------------------- zoneGroupBox2
        zoneGroupBox2 = QtGui.QGroupBox()
        zoneGroupBox2.setLayout(QtGui.QFormLayout())
        zoneGroupBox2.layout().addRow("Zone 2", parent.zoneCheckBox2)
        zoneGroupBox2.layout().addRow("Output", zoneValue2Layout)
#        zoneGroupBox2.layout().addRow("Limit", zoneSpinBox2Layout)
        parent._zGBoxes.append(zoneGroupBox2)      
        # #------------------------------------------------ end of zoneGroupBox2        

        # #-------------------------------------------------------- zoneGroupBox3
        zoneGroupBox3 = QtGui.QGroupBox()
        zoneGroupBox3.setLayout(QtGui.QFormLayout())
        zoneGroupBox3.layout().addRow("Zone 3", parent.zoneCheckBox3)
        zoneGroupBox3.layout().addRow("Output", zoneValue3Layout)
#        zoneGroupBox3.layout().addRow("Limit", zoneSpinBox3Layout)
        parent._zGBoxes.append(zoneGroupBox3)       
        # #------------------------------------------------ end of zoneGroupBox3
        
        # #-------------------------------------------------------- zoneGroupBox4        
        zoneGroupBox4 = QtGui.QGroupBox()
        zoneGroupBox4.setLayout(QtGui.QFormLayout())
        zoneGroupBox4.layout().addRow("Zone 4", parent.zoneCheckBox4)
        zoneGroupBox4.layout().addRow("Output", zoneValue4Layout)
#        zoneGroupBox4.layout().addRow("Limit", zoneSpinBox4Layout)
        parent._zGBoxes.append(zoneGroupBox4)        
        # #------------------------------------------------ end of zoneGroupBox4        
       
        # #-------------------------------------------------------- zoneGroupBox5       
        zoneGroupBox5 = QtGui.QGroupBox()
        zoneGroupBox5.setLayout(QtGui.QFormLayout())
        zoneGroupBox5.layout().addRow("Zone 5", parent.zoneCheckBox5)
        zoneGroupBox5.layout().addRow("Output", zoneValue5Layout)
#        zoneGroupBox5.layout().addRow("Limit", zoneSpinBox5Layout)
        parent._zGBoxes.append(zoneGroupBox5)        
        # #------------------------------------------------ end of zoneGroupBox5        
        
        # #-------------------------------------------------------- zoneGroupBox6        
        zoneGroupBox6 = QtGui.QGroupBox()
        zoneGroupBox6.setLayout(QtGui.QFormLayout())
        zoneGroupBox6.layout().addRow("Zone 6", parent.zoneCheckBox6)
        zoneGroupBox6.layout().addRow("Output", zoneValue6Layout)
#        zoneGroupBox6.layout().addRow("Limit", zoneSpinBox6Layout)
        parent._zGBoxes.append(zoneGroupBox6)        
        # #------------------------------------------------ end of zoneGroupBox6        
        
        # #-------------------------------------------------------- zoneGroupBox7        
        zoneGroupBox7 = QtGui.QGroupBox()
        zoneGroupBox7.setLayout(QtGui.QFormLayout())
        zoneGroupBox7.layout().addRow("Zone 7", parent.zoneCheckBox7)
        zoneGroupBox7.layout().addRow("Output", zoneValue7Layout)
#        zoneGroupBox7.layout().addRow("Limit", zoneSpinBox7Layout)
        parent._zGBoxes.append(zoneGroupBox7)        
        # #------------------------------------------------ end of zoneGroupBox7        

        # #-------------------------------------------------------- zoneGroupBox8
        zoneGroupBox8 = QtGui.QGroupBox()
        zoneGroupBox8.setLayout(QtGui.QFormLayout())
        zoneGroupBox8.layout().addRow("Zone 8", parent.zoneCheckBox8)
        zoneGroupBox8.layout().addRow("Output", zoneValue8Layout)
#        zoneGroupBox8.layout().addRow("Limit", zoneSpinBox8Layout)
        parent._zGBoxes.append(zoneGroupBox8)
        # #------------------------------------------------ end of zoneGroupBox8
         
        zonesLayout.addWidget(zoneGroupBox1, 0, 0, 1, 4)
        zonesLayout.addWidget(zoneGroupBox2, 0, 4, 1, 4)
        zonesLayout.addWidget(zoneGroupBox3, 0, 8, 1, 4)
        zonesLayout.addWidget(zoneGroupBox4, 0, 12, 1, 4)
        zonesLayout.addWidget(zoneGroupBox5, 1, 0, 1, 4)
        zonesLayout.addWidget(zoneGroupBox6, 1, 4, 1, 4)
        zonesLayout.addWidget(zoneGroupBox7, 1, 8, 1, 4)
        zonesLayout.addWidget(zoneGroupBox8, 1, 12, 1, 4)
        #---------------------------------------------------- end of zonesLayout
        
        #--------------------------------------------------------- buttonsLayout
        buttonsLayout = QtGui.QHBoxLayout()
        
        # #---------------------------------------------------------- saveButton
        parent.saveButton = QtGui.QPushButton("Save")
        parent.saveButton.setObjectName("saveButton")
        parent.saveButton.setSizePolicy(
                            parent.saveButton.sizePolicy().horizontalPolicy(),
                            QtGui.QSizePolicy.MinimumExpanding)
        parent.saveButton.setDisabled(True)        
        # #--------------------------------------------------- end of saveButton
        
        # #--------------------------------------------------------- startButton
        parent.startButton = QtGui.QPushButton("Start")
        parent.startButton.setObjectName("startButton")       
        parent.startButton.setSizePolicy(
                            parent.saveButton.sizePolicy().horizontalPolicy(),
                            parent.saveButton.sizePolicy().verticalPolicy())
        parent.startButton.setDisabled(True)
        # #-------------------------------------------------- end of startButton

        # #---------------------------------------------------------- stopButton
        parent.stopButton = QtGui.QPushButton("Stop")
        parent.stopButton.setObjectName("stopButton")
        parent.stopButton.setSizePolicy(
                            parent.saveButton.sizePolicy().horizontalPolicy(),
                            parent.saveButton.sizePolicy().verticalPolicy())
        parent.stopButton.setDisabled(True)
        # #--------------------------------------------------- end of stopButton
        
        buttonsLayout.addWidget(parent.saveButton)
        buttonsLayout.addWidget(parent.startButton)
        buttonsLayout.addWidget(parent.stopButton)        
        #-------------------------------------------------- end of buttonsLayout
        
        parent.layout().addLayout(pressureLayout, 0, 0)
        parent.layout().addWidget(parent.table, 1, 0)
        parent.layout().addWidget(graphGroupBox, 0, 1, 2, 1)
        parent.layout().addLayout(buttonsLayout, 2, 0)
        parent.layout().addWidget(progressGroupBox, 3, 0)
        parent.layout().addLayout(zonesLayout, 2, 1, 2, 1)
        
        parent.metaObject().connectSlotsByName(parent)
        
#    setupUi()
