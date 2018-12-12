from __future__ import division
from PyQt4 import QtCore, QtGui, Qwt5 as Qwt
from Ui_BakeOutProgrammer import *
from PyTango import Database, DevFailed
from PyTangoArchiving.widget import ContextToolBar
from tau.core import TauEventType, TauAttribute
from tau.widget import TauBaseComponent, TauMainWindow, TauValueLabel, TauValueSpinBox, TauWidget, TauValue 
from tau.widget.qwt import TauTrend

TEMP_ROOM = 25.
TEMP_DEFAULT = 1200.
PROGRAM_DEFAULT = [TEMP_DEFAULT, 0., -1.]
PARAMS_DEFAULT = [TEMP_DEFAULT, 0., 0., 0.]

class BakeOutProgrammerMainWindow(TauMainWindow):
    def __init__(self, parent=None, flags=0):
        TauMainWindow.__init__(self, parent, flags)
        
        self._numbers = set()
        self._zStates = [QtCore.Qt.Unchecked]*8
        
        UiMainWindow().setupUi(self)
        self.addControllerComboItems()

#        self._listener = BakeOutProgrammerListener(self)
#        self._listener.setUseParentModel(True)
#        self._listener.setModel("/Temperature_All")         
        
#    __init__()

    @QtCore.pyqtSignature("QString")
    def on_controllerCombo_currentIndexChanged(self, devModel):
        self.debug("on_controllerCombo_currentIndexChanged)\tdevModel: %s" % devModel)
        self.reset()
        self.setModel(devModel)
        modelObj = self.getModelObj()
        if ( modelObj ):
            self.tabWidget.setEnabled(True)
            programs = []
            for number in range(1, 9):
                try:
                    try:
                        program = modelObj.getAttribute("Program_%s" % number).read().value.tolist()
                    except AttributeError:
                        continue
                    try:
                        zones = modelObj.getAttribute("Program_%s_Zones" % number).read().value.tolist()
                    except AttributeError:
                        zones = []
                except DevFailed:
                    break
                if ( program != [PROGRAM_DEFAULT] ):
                    programs.append((number, program, zones))
            
            self.loadPrograms(programs)
        else:
            pass
#            self.tabWidget.setDisabled(True)
            
        if ( not self.tabWidget.count() ):
            self.tabAddRequest()
            
#    on_deviceCombo_currentIndexChanged()
 
    @QtCore.pyqtSignature("")
    def on_newProgramButton_clicked(self):
        self.tabAddRequest()      
         
#    on_closeProgramButton_clicked()
   
    def on_tabWidget_tabCloseRequested(self, index):
        self.tabCloseRequest(index)
        
#    on_tabWidget_tabCloseRequested()    
    
    @QtCore.pyqtSignature("")    
    def on_closeProgramButton_clicked(self):
        self.tabCloseRequest(self.tabWidget.currentIndex())

#    on_newProgramButton_clicked()

    def zoneState(self, zone):
        return self._zStates[zone - 1]
    
#    zoneState()
    
    def setZoneState(self, zone, state):
        if ( not self._zStates[zone - 1] == state ):
            self._zStates[zone - 1] = state
        
#    setZoneState()

    def setZonesDisabled(self, zone=None):
        for tabIndex in range(self.tabWidget.count()):
            self.tabWidget.widget(tabIndex).setZoneDisabled(zone)       
        
#    setZonesDisabled()

    def listener(self):
        return self._listener
    
#    listener()
    
    def loadPrograms(self, programs):
        if ( programs ):
            for tabIndex, (number, program, zones) in enumerate(programs):                   
                if ( not self.tabWidget.widget(tabIndex) ):
                    if ( not self.tabAddRequest() ):
                        break                 
                self.tabWidget.widget(tabIndex).loadProgram(number, program, zones)
                
            self.updateNumbers()
                    
#    loadPrograms()

    def reset(self):
        self.debug("reset")
        self._numbers = set()        
        self._zStates = [QtCore.Qt.Unchecked]*8
        
        delTab = self.tabWidget.widget(0)
        while ( delTab ):
            self.tabWidget.removeTab(0)
            delTab.deleteLater()
            delTab = self.tabWidget.widget(0)
        
#    reset()
    
    def tabAddRequest(self):
        tabCount = self.tabWidget.count()
        if ( tabCount >= 8 ):
            return False
        elif ( tabCount == 7 ):
            self.newProgramButton.hide()
        elif ( tabCount >= 1 ):
            if ( QtCore.PYQT_VERSION_STR >= "4.5" ): 
                self.tabWidget.setTabsClosable(True)
            else:
                self.closeProgramButton.show()                
        
        number = self.nextNumber()
        self.tabWidget.addTab(BakeOutProgrammerTab(number), "Program " + str(number))
        return True        
        
#    tabAddRequest()
    
    def tabCloseRequest(self, index):
        delTab = self.tabWidget.widget(index)
        tabCount = self.tabWidget.count()        
        if ( tabCount <= 1 ):
            return False
        elif ( tabCount == 2 ):
            if ( QtCore.PYQT_VERSION_STR >= "4.5" ):
                self.tabWidget.setTabsClosable(False)
            else:
                self.closeProgramButton.hide()                
        elif ( tabCount <= 8 ):
            self.newProgramButton.show()
                
        for zone in range(1, 9):
            if ( delTab.zoneState(zone) == QtCore.Qt.Checked ):
                self.setZoneState(zone, QtCore.Qt.Unchecked)
            
        self._numbers.remove(delTab.number())
        self.tabWidget.removeTab(index)
        delTab.deleteLater()

        self.setZonesDisabled()
        return True      
        
#    tabCloseRequest()

    def nextNumber(self):
        numbers = set(range(1, 9))
        numbers.difference_update(self._numbers)
        number = min(numbers)
        self._numbers.add(number)     
        return number
    
#    nextNumber()
 
    def updateNumbers(self):
        self._numbers = set()
        for tabIndex in range(self.tabWidget.count()):
            self._numbers.add(self.tabWidget.widget(tabIndex).number())
            
#    updateNumbers()

    def addControllerComboItems(self):
        db = Database()
        items = [""] 
        items.extend(db.get_device_exported("*/elotech*").value_string)
        items.extend(db.get_device_exported("*/bestec*").value_string)
        self.controllerCombo.addItems(sorted(i for i in items if not i.startswith("dserver")))
    
#    addControllerComboItems()     

#BakeOutProgrammerMainWindow()

class BakeOutProgrammerTab(TauWidget):  
    def __init__(self, number):
        TauWidget.__init__(self)

        self._number = number
        self._pModel = ""
        self._rButtons = []
        self._zStates = [QtCore.Qt.Unchecked]*8
        self._program = [PROGRAM_DEFAULT]
        self._sTemp, self._sTime, self._pTime, self._fTime = tuple(PARAMS_DEFAULT)
        self._eFTime = 0.
        self._eSFTimes = []
        self._state = [False, False, False]
        self._cStep = 0
        self._sCount = 0
            
        UiTab().setupUi(self)
        self.addPressureComboItems()
        
        self._listener = BakeOutProgrammerListener(self)
        self._listener.setUseParentModel(True)
        self._listener.setModel("/Temperature_All")            
        self.connect(self._listener,
                     QtCore.SIGNAL("valueChanged(PyQt_PyObject)"),
                     self.on_listener_valueChanged)
        
#    __init__()

    def event(self, event):
        if ( event.type() == QtCore.QEvent.ParentChange and isinstance(self.window(), BakeOutProgrammerMainWindow) ):
            self.setUseParentModel(True)
            self.setZoneDisabled()
            return True
        return False
    
#    event()

    def on_currentProgressBar_valueChanged(self, value):
        print value
        
#        on_currentProgressBar_valueChanged()        
    
    @QtCore.pyqtSignature("")
    def on_addButton_clicked(self):
        self.debug("on_addButton_clicked()")
        self.disconnect(self.table,
                        QtCore.SIGNAL("itemChanged(QTableWidgetItem*)"),
                        self.on_table_itemChanged)
        self.addRow()
        self.connect(self.table,
                    QtCore.SIGNAL("itemChanged(QTableWidgetItem*)"),
                    self.on_table_itemChanged)
        
#    on_addButton_clicked()

    def on_listener_valueChanged(self, value):
        self.debug("on_paramsChanged()")

        l = len(value)
        if ( l == 4 ):
            change = self.setStartTemp(value[0]), self.setStartTime(value[1]), self.setPauseTime(value[2]), self.setFinishTime(value[3])
            
            if ( any(change) ):
                if ( self.startTime() ):
                    self.setStarted(True)
                    running = True
                else:
                    self.setStarted(False)
                    running = False        
                if ( self.finishTime() ):
                    self.setRunning(False)
                else:
                    self.setRunning(running)
        
                self.updateProgram()
            self.updateProgressBars()
        elif ( l == 8 ):
            temps = [value[z - 1] for z in self.zones() if value[z - 1] != TEMP_DEFAULT]
            dTemps = [abs(self._program[0][0] - t) for t in temps]
            sTemp = dTemps and temps[dTemps.index(max(dTemps))] or TEMP_DEFAULT
            self.setStartTemp(sTemp)
            self.resetStartTime()
            self.updateProgram()
        else:
            raise ValueError          

#    on_paramsChanged()

    @QtCore.pyqtSignature("QString")
    def on_pressureCombo_activated(self, devModel):
        self.debug("on_pressureCombo_activated()\tdevModel:" % devModel)
        self.gaugeCombo.clear()   
        attributes = [""]
        if ( devModel ):
            attributes.extend(["P1", "P2", "P3", "P4", "P5"])
            self.gaugeCombo.setEnabled(True)
        else:
            self.gaugeCombo.setDisabled(True)
        
        self.gaugeCombo.addItems(sorted(attributes))
        self.hidePressureCurve()
  
#    on_pressureCombo_currentIndexChanged()

    @QtCore.pyqtSignature("QString")
    def on_gaugeCombo_activated(self, attrModel):
        self.debug("on_gaugeCombo_activated()\tattrModel:" % attrModel)
        if ( attrModel ):
            self.hidePressureCurve()
            self.setPressureModel(self.pressureCombo.currentText() + "/" + attrModel)
            self.togglePressureCurve(self.isStarted())
        else:
            self.hidePressureCurve()
            self.resetPressureModel()
  
#    on_gaugeCombo_currentIdnexChanged()

    @QtCore.pyqtSignature("")
    def on_removeButton_clicked(self):
        row = self._rButtons.index(self.sender())
        valid = self.isValid(row)
        self.table.removeRow(row)
        self._rButtons.remove(self.sender())
        if ( self.table.rowCount() <= 1 ):
            self.removeAllButton.setEnabled(False)
        if ( valid ):
            self.setModified(True)
            self.updateProgram()
        
#    on_removeButton_clicked()
    
    @QtCore.pyqtSignature("")    
    def on_removeAllButton_clicked(self):
        valid = False
        while ( self.table.rowCount() > 1  ):
            if ( not valid ):
                valid = self.isValid(0)
            self.table.removeRow(0)
        self._rButtons = []
        self.removeAllButton.setEnabled(False)
        if ( valid ):
            self.setModified(True)
            self.updateProgram()
            
#    on_removeAllButton_clicked()

    @QtCore.pyqtSignature("")
    def on_saveButton_clicked(self):
        self.debug("on_saveButton_clicked")      
        modelObj = self.getModelObj()
        if ( modelObj ):
            self.setModified(False)
            self.currentProgressBar.reset()
            self.overallProgressBar.reset()            
            self.resetPressureModel()
            self.graphPlot.resetModel()
            self.listener().setModel("/Temperature_All")
            zones = self.zones()
            modelObj.write_attribute("Program_%s" % self.number(), self._program)
            modelObj.write_attribute("Program_%s_Zones" % self.number(), zones)
            self.updateProgram()
        
#    onSaveButton_clicked()

    @QtCore.pyqtSignature("")
    def on_startButton_clicked(self):
        self.debug("on_startButton_clicked")       
        modelObj = self.getModelObj()
        if ( modelObj ):
            self.setStarted(True)
            self.setRunning(True)
            self.currentProgressBar.reset()
            self.overallProgressBar.reset()
            modelObj.Start(self._number)
            self.listener().setModel("/Program_%s_Params" % self.number())
            self.updateProgram()
            self.togglePressureCurve(True)
            for zone in self.zones():
                self.toggleTempCurve(zone, True)
        
#    onStartButton_clicked()

    @QtCore.pyqtSignature("")
    def on_stopButton_clicked(self):
        self.debug("on_stopButton_clicked")
        modelObj = self.getModelObj()
        if ( modelObj ):
            self.setRunning(False)
            modelObj.Stop(self._number)
            self.updateProgram()
            
#    on_stopButton_clicked()

    def on_table_itemChanged(self, item):
        self.debug("on_table_itemChanged()")
        row = self.table.row(item)
        if ( self.isValid(row) ):
            self.setModified(True)
            self.updateProgram()

#    on_table_itemChanged()

    def on_zoneCheckBox1_stateChanged(self, state):
        self.on_checkBox_stateChanged(1, state)    
    
#    on_zoneCheckBox1_stateChanged()
    
    def on_zoneCheckBox2_stateChanged(self, state):
        self.on_checkBox_stateChanged(2, state)    
    
#    on_zoneCheckBox2_stateChanged()
    
    def on_zoneCheckBox3_stateChanged(self, state):
        self.on_checkBox_stateChanged(3, state)    
    
#    on_zoneCheckBox3_stateChanged()
    
    def on_zoneCheckBox4_stateChanged(self, state):
        self.on_checkBox_stateChanged(4, state)    
    
#    on_zoneCheckBox4_stateChanged()
    
    def on_zoneCheckBox5_stateChanged(self, state):
        self.on_checkBox_stateChanged(5, state)    
    
#    on_zoneCheckBox5_stateChanged()
    
    def on_zoneCheckBox6_stateChanged(self, state):
        self.on_checkBox_stateChanged(6, state)    
    
#    on_zoneCheckBox6_stateChanged()
    
    def on_zoneCheckBox7_stateChanged(self, state):
        self.on_checkBox_stateChanged(7, state)    
    
#    on_zoneCheckBox7_stateChanged()
    
    def on_zoneCheckBox8_stateChanged(self, state):
        self.on_checkBox_stateChanged(8, state)    
    
#    on_zoneCheckBox8_stateChanged()
    
    def on_checkBox_stateChanged(self, zone, state):
        self.debug("on_checkBox_stateChanged()\tzone: %s\tstate: %s" % (zone, state))
        self.setModified(True)
        self.setZoneState(zone, state)
        if ( isinstance(self.window(), BakeOutProgrammerMainWindow) ):
            self.window().setZoneState(zone, state)
            self.window().setZonesDisabled(zone)
        self.zoneValueLabel(zone).setEnabled(state)
#        self.zoneSpinBox(zone).setEnabled(state)
        if ( state ):
            self.zoneValueLabel(zone).setModel("/Output_%s" % zone)
#            self.zoneSpinBox(zone).setModel("/Output_%s_Limit" % zone)            
        else:
            self.zoneValueLabel(zone).resetModel()
#            self.zoneSpinBox(zone).resetModel()      
        self.updateTabText()
        self.updateProgram()
        self.toggleTempCurve(zone, state)
            
#    on_zoneCheckBox8_stateChanged()
   
    def setProgram(self, program):
        self.debug("setProgram()")
        self.disconnect(self.table,
                        QtCore.SIGNAL("itemChanged(QTableWidgetItem*)"),
                        self.on_table_itemChanged)
        for atRow, stepData in enumerate(program):
            self.addRow()
            for atCol, itemData in enumerate(stepData):
                if ( atCol == 3 ): continue
                self.table.item(atRow, atCol).setText(str(itemData))
        self.connect(self.table,
                    QtCore.SIGNAL("itemChanged(QTableWidgetItem*)"),
                    self.on_table_itemChanged)                
                
#    setProgram()

    def currentStep(self):
        return self._cStep
    
#    currentStep()

    def setCurrentStep(self, value):
        if ( value <= self.stepCount() ):        
            self._cStep = int(value)
        raise IndexError
        
#    setCurrentStep()

    def nextStep(self):
        if ( self._cStep + 1 <= self.stepCount() ):
            self._cStep += 1
        raise IndexError
    
#    nextStep()

    def stepCount(self):
        return self._sCount
    
#    stepCount()

    def setStepCount(self, value):
        self._sCount = int(value)
        
#    setStepCount()

    def resetStepCount(self):
        self._sCount = 0
        
#    resetStepCount()

    def expectedFinishTime(self):
        return self._eFTime
    
#    expectedFinishTime()

    def setExpectedFinishTime(self, t):
        self._eFTime = t
        
#    setExpectedFinishTime()

    def setExcpectedStepFinishTimes(self, t):
        self._eSFTimes = t
        
#    setExpectedStepFinishTime()

    def currentStepStartTime(self):
        return self._eSFTimes[(self.currentStep() - 1) * 2]
    
#    stepStartTime()

    def currentStepExpectedFinishTime(self):
        return self._eSFTimes[(self.currentStep()) * 2]
    
#    currentStepExpectedFinishTime()

    def resetPressureModel(self):
        self._pModel = ""
        
#    resetPressureModel()
  
    def setPressureModel(self, model):
        self._pModel = str(model)
        
#    setPressureModel()
  
    def pressureModel(self):
        return self._pModel
    
#    pressureModel()
  
    def startTemp(self):
        return self._sTemp
    
#    startTemp()

    def setStartTemp(self, temp):
        if ( self._sTemp != temp ):
            self._sTemp = temp
            return True
        return False
            
#    setStartTemp()

    def startTime(self):
        return self._sTime
    
#    startTime()

    def setStartTime(self, time):
        if ( self._sTime != time ):
            self._sTime = time
            return True
        return False
            
#    setStartTemp()

    def resetStartTime(self):
        if ( self._sTime ):
            self._sTime = 0.
            
#    resetStartTime()

    def finishTime(self):
        return self._fTime
    
#    finishTime()

    def setFinishTime(self, time):
        if ( self._fTime != time ):
            self._fTime = time
            return True
        return False
            
#    setFinishTime()

    def pauseTime(self):
        return self._pTime
    
#    pauseTime()

    def setPauseTime(self, time):
        if ( self._pTime != time ):
            self._pTime = time
            
#    setPauseTime()

    def number(self):
        return self._number
    
#    number()
 
    def zones(self):
        return [z for z in range(1, 9) if self.zoneState(z)]
    
#    zones()
      
    def zoneState(self, zone):
        return self._zStates[zone - 1]
    
#    zoneState()
    
    def zoneCheckBox(self, zone):
        return self._zCBoxes[zone - 1]
    
#    zoneCheckBox()
  
    def zoneGroupBox(self, zone):
        return self._zGBoxes[zone - 1]
    
#    zoneGroupBox()
  
    def zoneSpinBox(self, zone):
        return self._zSBoxes[zone - 1]
    
#    zoneSpinBox()
   
    def zoneValueLabel(self, zone):
        return self._zValues[zone - 1]
    
#    zoneValueLabel()
 
    def setZoneState(self, zone, state):
        self._zStates[zone - 1] = state
        
#    setZoneState()

    def isRunning(self):
        return self._state[2]
    
#    isRunning()
        
    def setRunning(self, yesno):
        if ( self._state[2] != yesno ):        
            self._state[2] = yesno
            self.updateButtons()
        
#    setRunning

    def isModified(self):
        return self._state[0]
    
#    isModified
  
    def setModified(self, yesno):
        if ( self._state[0] != yesno and not self._state[2] ):
            self._state[0] = yesno
            if ( yesno ):
                self._state[1] = self._state[2] = False
            self.updateButtons()
        
#    setModified()
 
    def isStarted(self):
        return self._state[1]
    
#    isStarted()
 
    def setStarted(self, yesno):
        if ( self._state[1] != yesno ):        
            self._state[1] = yesno
            self.updateButtons()
        
#    setStarted()

    def listener(self):
        return self._listener
    
#    listener()

    def loadProgram(self, number, program, zones):
        self.debug("loadProgram()")
        self._number = number
        modelObj = self.getModelObj()
        if ( modelObj ):
            params = modelObj.getAttribute("Program_%s_Params" % self._number).read().value.tolist()
            if ( params[3] ):
                self.setRunning(False)
            if ( params[1] ):
                self.setStarted(True)
                self.setRunning(True)
                self.listener().setModel("/Program_%s_Params" % self._number)          
            if ( zones ):
                for zone in zones:
                    self.zoneCheckBox(zone).setCheckState(QtCore.Qt.Checked)
            else:
                self.updateTabText()
            self.setModified(False)
            self.setProgram(program)
            self.updateProgram()
        
#    loadProgram()

    def setZoneDisabled(self, zone=None):
        if ( isinstance(self.window(), BakeOutProgrammerMainWindow) ):        
            for zone in zone and (zone,) or range(1, 9):
                checkBox = self.zoneCheckBox(zone)
                if ( not checkBox.isChecked() ):
                    self.zoneGroupBox(zone).setDisabled(self.window().zoneState(zone))

#    setZoneDisabled()

    def updateButtons(self):
        self.debug("updateButtons()")
        self.setTableItemsEditable(not self.isRunning())
        self.saveButton.setEnabled(self.isModified())
        self.startButton.setDisabled(self.isModified() or self.isRunning())
        self.stopButton.setEnabled(self.isRunning())
  
#    updateButtons()
  
    def setTableItemsEditable(self, editable):
        if ( self.table.rowCount() > 1 ):
            self.disconnect(self.table,
                            QtCore.SIGNAL("itemChanged(QTableWidgetItem*)"),
                            self.on_table_itemChanged)
            for atRow in range(self.table.rowCount() - 1):
                for atCol in range(3):
                    if ( editable ):
                        self.table.item(atRow, atCol).setFlags(QtCore.Qt.ItemIsEditable\
                                                               | QtCore.Qt.ItemIsEnabled)
                    else:
                        self.table.item(atRow, atCol).setFlags(QtCore.Qt.ItemIsEnabled)
            self.connect(self.table,
                        QtCore.SIGNAL("itemChanged(QTableWidgetItem*)"),
                        self.on_table_itemChanged)                        
                        
#    setTableItemsEditable()            
  
    def updateProgram(self):
        self.debug("updateProgram()")
        program = []
        for atRow in range(self.table.rowCount() - 1):
            step = []
            for atCol in range(self.table.columnCount() - 1):
                item = self.table.item(atRow, atCol)
                if ( item ):
                    double, ok = item.text().toDouble()
                    if ( ok ):
                        step.append(double)
            
            if ( len(step) == self.table.columnCount() - 1 ):
                program.append(step)
        
        self._program = program or [PROGRAM_DEFAULT]
        self.updateProgramCurve()

#    updateProgram()

    def updateTabText(self):
        self.debug("updateTabText()")
        if ( isinstance(self.window(), BakeOutProgrammerMainWindow) ):
            tabWidget = self.window().tabWidget
            currentIndex = tabWidget.indexOf(self)
    
            zones = map(str, self.zones())
            self.reduceZones(zones)
            tabText = "Program " + str(self._number) +\
                   ((" [Zones " if ( len(zones) > 1 or len(zones[0]) > 1 ) else " [Zone ") +\
                   ", ".join(zones) + "]" if ( len(zones) > 0 ) else "")
                   
            tabWidget.setTabText(currentIndex, tabText)
        
#    updateTabText()

    def updateProgramCurve(self):
        self.debug("updateProgramCurve()")
        rawData = self.toRawData(self._program, self.startTime(), self.startTemp())
        if ( rawData != [PROGRAM_DEFAULT] ):
            self.setStepCount((len(rawData[0]) - 1) / 2)
            self.setExpectedFinishTime(rawData[0][-1])
            self.setExcpectedStepFinishTimes(rawData[0])
            xData, yData = rawData[0], rawData[1]
            if ( self.graphPlot.getCurve("Program") ):
                self.graphPlot.getCurve("Program").setData(xData, yData)
            else:
                self.graphPlot.attachRawData(dict(zip(("title", "x", "y"), ("Program", xData, yData))))
        else:
            self.resetStepCount()
            if ( self.graphPlot.getCurve("Program") ):
                self.graphPlot.detachRawData("Program")
                
        self.graphPlot.replot()
            
#    updateProgramCurve()

    def updateProgressBars(self):
        return
        self.debug("updateProgressBar()")
        sStartTime = self.stepStartTime()
        if ( self.currentProgressBar.minimum() != sStartTime ):
            self.currentProgressBar.setMinimum(sStartTime)
        sFinishTime = self.stepFinishTime()
        if ( self.currentProgressBar.maximum() != sFinishTime ):
            self.currentProgressBar.setMaximum(sFinishTime)
        sTime = self.startTime()        
        if ( self.overallProgressBar.minimum() != sTime ):
            self.overallProgressBar.setMinimum(sTime)
        fTime = self.expectedFinishTime()
        if ( self.overallProgressBar.maximum() != fTime ):
            self.overallProgressBar.setMaximum(fTime)
        if ( self.isRunning() ):
            now = QtCore.QDateTime().currentDateTime().toTime_t()
            self.currentProgressBar.setValue(now)
            self.overallProgressBar.setValue(now)
        else:
            fTime = self.finishTime()
            if ( self.currentProgressBar.value() != fTime ):
                self.currentProgressBar.setValue(fTime)
            if ( self.overallProgressBar.value() != fTime ):
                self.overallProgressBar.setValue(fTime)
        
#    updateProgressBars()      

    def toggleTempCurve(self, zone, on):
        self.debug("toggleTempCurve()\tzone: %s\ton: %s" % (zone, on))
        if ( self.isStarted() ):
            modelObj = self.getModelObj()
            if ( modelObj ): 
                model = "%s/Temperature_%s" % (modelObj.getNormalName(), zone)
                if ( on ):
                    self.graphPlot.addModels([model])
                else:
                    self.graphPlot.removeModels([model])
                
#    toggleTempCurve()

    def hidePressureCurve(self):
        self.debug("hidePressureCurve()")
        model = self.pressureModel()
        if ( model ):     
            self.graphPlot.removeModels([model])
        
#    hidePressureCurve()          

    def togglePressureCurve(self, on):
        self.debug("togglePressureCurve()\ton: %s" % on)
        if ( self.isStarted() ):
            model = self.pressureModel()
            if ( model ):
                if ( on ):
                    self.graphPlot.addModels([model])
                    self.graphPlot.setCurvesYAxis(["%s[0]" % model], Qwt.QwtPlot.yRight)
                else:
                    self.graphPlot.removeModels([model])
            
#    togglePressureCurve()
   
    def addRow(self):
        self.debug("addRow()")

        atRow = self.table.rowCount() - 1
        self.table.insertRow(atRow)
        
        for atCol in range(4):
            if ( atCol == 3 ):
                removeButton = QtGui.QPushButton("Remove")
                self.table.setCellWidget(atRow, atCol, removeButton)
                self._rButtons.append(removeButton)
                self.connect(removeButton,
                             QtCore.SIGNAL("clicked()"),
                             self.on_removeButton_clicked)
            else:
                item = QtGui.QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignRight\
                                      | QtCore.Qt.AlignVCenter)
                item.setFlags(QtCore.Qt.ItemIsEditable\
                              | QtCore.Qt.ItemIsEnabled)
                self.table.setItem(atRow, atCol, item)
    
        if ( self.table.rowCount() > 1 ):
            self.removeAllButton.setEnabled(True)
            
#    addRow()

    def toRawStepData(self, step, x0, y0):
        y = step[0]
        a = abs(step[1])
        x1 = x0 + 60. * abs(y0 - y) / a
        x2 = x1 + 3600. * step[2]

        return map(long, (x1, x2)), (y, y)

#    toRawStepData()

    def toRawData(self, program, x0=0., y0=TEMP_ROOM):
        if ( program == [PROGRAM_DEFAULT] ):
            return [PROGRAM_DEFAULT]
        if ( y0 >= TEMP_DEFAULT ):
            y0 = TEMP_ROOM
        try:
            if ( not x0 ):              
                x0 = QtCore.QDateTime().currentDateTime().toTime_t()
            rawXData = [x0]
            rawYData = [y0]            
            for step in program:
                rawStepData = self.toRawStepData(step, rawXData[-1], rawYData[-1])
                rawXData.extend(rawStepData[0])
                rawYData.extend(rawStepData[1])
            
            return map(long, rawXData), rawYData                
        except TypeError:
            return [PROGRAM_DEFAULT]

#    toRawData()

    def reduceZones(self, strZones):
        for i in range(len(strZones) - 1):
            if ( (int(strZones[i + 1][0]) - int(strZones[i][-1])) == 1 ):
                strZones[i + 1] = strZones[i][0] + "-" + strZones[i + 1]
                strZones.pop(i)
                return self.reduceZones(strZones)

#    reduceZones()

    def isValid(self, row):
        self.debug("isValid()\trow: %s" % row)
        rowItems = (self.table.item(row, col) for col in range(self.table.columnCount() - 1))
        ok = [result[1] for result in (item.text().toDouble() for item in rowItems)]
        if ( all(ok) ):
            return True
        return False
    
#    isValid()

    def addPressureComboItems(self):
        db = Database()
        items = [""] 
        items.extend(db.get_device_exported("*/vgct*").value_string)
        self.pressureCombo.addItems(sorted(i for i in items if not i.startswith("dserver")))
    
#    addPressureComboItems()

#BakeOutProgrammerTab()

class TauBaseListener(QtCore.QObject, TauBaseComponent):
    __pyqtSignals__ = ("modelChanged(QString)",)
    
    def __init__(self, parent=None):
        name = self.__class__.__name__
        QtCore.QObject.__init__(self, parent)
        TauBaseComponent.__init__(self, name)
        
#    __init__()
            
    def getParentTauComponent(self):
        try:
            p = self.parent()
            while ( p and not isinstance(p, TauBaseComponent) ):
                p = p.parent()
            self._parentTauComponent = p
            return p
        except:
            return None
    
#    getParentTauComponent()

    @QtCore.pyqtSignature("setUseParentModel(bool)")    
    def setUseParentModel(self, yesno):
        if ( not yesno == self._useParentModel ):
            self._updateUseParentModel(yesno)
        TauBaseComponent.setUseParentModel(self, yesno)
        
#    setUseParentModel()

    def _updateUseParentModel(self, yesno):
        parent_widget = self.getParentTauComponent()
        if parent_widget:
            if ( yesno ):
                self.connect(parent_widget, 
                             QtCore.SIGNAL("modelChanged(QString)"), 
                             self.parentModelChanged)
            else:
                self.disconnect(parent_widget,
                                QtCore.SIGNAL("modelChanged(QString)"), 
                                self.parentModelChanged)
                
#    _updateUseParentModel()
                
    @QtCore.pyqtSignature("parentModelChanged(QString)")
    def parentModelChanged(self, parentmodel_name):
        self.debug("parentModelChanged()\tmodel: %s" % parentmodel_name)
        parentmodel_name = str(parentmodel_name)
        if self.getUseParentModel():
            self.setModelCheck(self.getModel(), False)
            
#    parentModelChanged()
            
    def getModelClass(self):
        return TauAttribute
    
#    getModelClass()

#TauBaseListener()

class BakeOutProgrammerListener(TauBaseListener):
    __pyqtSignals__ = ("modelChanged(QString)",
                       "valueChanged(PyQt_PyObject)")
    
    def __init__(self, parent):
        TauBaseListener.__init__(self, parent)
        self.insertEventFilter(self.evtFilter)
                                 
#    __init__()

    def evtFilter(self, src, type, value):
        if ( type in (TauEventType.Change, TauEventType.Periodic) ):
            return src, type, value
        
#    eventFilter()
                                 
    def handleEvent(self, src, type, value):
        try:
            self.emit(QtCore.SIGNAL("valueChanged(PyQt_PyObject)"), value.value.tolist())
        except AttributeError :
            self.error("AttributeError")
                        
#    handleEvent()
    
#BakeOutListener()

if ( __name__ == "__main__" ):
    import sys
    app = QtGui.QApplication(sys.argv)
    mainWindow = BakeOutProgrammerMainWindow()
    mainWindow.showMaximized()
    sys.exit(app.exec_())