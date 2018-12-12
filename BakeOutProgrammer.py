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

class BakeOutProgrammerMainWindow(UiMainWindow):
    def __init__(self, parent=None, flags=0):
        UiMainWindow.__init__(self, parent, flags)
        self._numbers = set()
        self._channelStates = [QtCore.Qt.Unchecked]*8

        self.addControllerComboItems()

#        self._listener = BakeOutProgrammerListener(self)
#        self._listener.setUseParentModel(True)
#        self._listener.setModel("/Temperature_All")
#        
#        self.connect(self._listener,
#                     QtCore.SIGNAL("valueChanged(PyQt_PyObject)"),
#                     self.on_listener_valueChanged)                 
        
#    __init__()

    def on_listener_valueChanged(self, value):
        self.emit(QtCore.SIGNAL("valueChanged(PyQt_PyObject)"), value)
        
#    on_listener_valueChanged()

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
                        channels = modelObj.getAttribute("Program_%s_Zones" % number).read().value.tolist()
                    except AttributeError:
                        channels = []
                except DevFailed:
                    break
                if ( program != [PROGRAM_DEFAULT] ):
                    programs.append((number, program, channels))
            
            self.loadPrograms(programs)
        else:
            self.tabWidget.setDisabled(True)
            
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

    def channelState(self, channel):
        return self._channelStates[channel - 1]
    
#    channelState()
    
    def setChannelState(self, channel, state):
        if ( not self._channelStates[channel - 1] == state ):
            self._channelStates[channel - 1] = state
        
#    setChannelState()

    def setChannelsDisabled(self, channel=None):
        for tabIndex in range(self.tabWidget.count()):
            self.tabWidget.widget(tabIndex).setChannelDisabled(channel)       
        
#    setChannelsDisabled()

    def listener(self):
        return self._listener
    
#    listener()
    
    def loadPrograms(self, programs):
        if ( programs ):
            for tabIndex, (number, program, channels) in enumerate(programs):                   
                if ( not self.tabWidget.widget(tabIndex) ):
                    if ( not self.tabAddRequest() ):
                        break                 
                self.tabWidget.widget(tabIndex).loadProgram(number, program, channels)
                
            self.updateNumbers()
                    
#    loadPrograms()

    def reset(self):
        self.debug("reset")
        self._numbers = set()        
        self._channelStates = [QtCore.Qt.Unchecked]*8
        
        delTab = self.tabWidget.widget(0)
        while ( delTab ):
            self.tabWidget.removeTab(0)
            delTab.deleteLater()
            delTab = self.tabWidget.widget(0)
            
        self.newProgramButton.show()
        self.closeProgramButton.hide()
        
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
                
        for channel in range(1, 9):
            if ( delTab.channelState(channel) == QtCore.Qt.Checked ):
                self.setChannelState(channel, QtCore.Qt.Unchecked)
            
        self._numbers.remove(delTab.number())
        self.tabWidget.removeTab(index)
        delTab.deleteLater()

        self.setChannelsDisabled()
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

class BakeOutProgrammerTab(UiTab):  
    def __init__(self, number, parent=None, flags=0):
        UiTab.__init__(self, parent, flags)
        self._number = number
        self._pressureModel = ""
        self._removeButtons = []
        self._channelStates = [QtCore.Qt.Unchecked]*8
        self._program = [PROGRAM_DEFAULT]
        self._startTemp = TEMP_DEFAULT
        self._startTime = long(0)
        self._pauseTime = long(0)
        self._finishTime = long(0)
        self._state = [False, False, False]
        
        self._listener = BakeOutProgrammerListener(self)
        self._listener.setUseParentModel(True)
        self._listener.setModel("/Temperature_All")            
        
        self.addPressureComboItems()
        for channel in range(1, 9):
            self.channelTemp(channel).setUseParentModel(True)
            self.channelTemp(channel).setModel("/Temperature_%s" % channel)
        
        self.connect(self._listener,
                     QtCore.SIGNAL("valueChanged(PyQt_PyObject)"),
                     self.on_listener_valueChanged)
        
#    __init__()

    def event(self, event):
        if ( event.type() == QtCore.QEvent.ParentChange and isinstance(self.window(), BakeOutProgrammerMainWindow) ):
            self.setUseParentModel(True)
            self.setChannelDisabled()
#            self.connect(self.window(),
#                         QtCore.SIGNAL("valueChanged(PyQt_PyObject)"),
#                         self.on_parent_valueChanged)
            return True
        return False
    
#    event()

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
            temps = [value[z - 1] for z in self.channels() if value[z - 1] != TEMP_DEFAULT]
            dTemps = [abs(self.program()[0][0] - t) for t in temps]
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
            self.gaugeValue.setEnabled(True)            
        else:
            self.gaugeCombo.setDisabled(True)
            self.gaugeValue.setDisabled(True)            
        
        self.gaugeCombo.addItems(sorted(attributes))
        self.hidePressureCurve()
  
#    on_pressureCombo_currentIndexChanged()

    @QtCore.pyqtSignature("QString")
    def on_gaugeCombo_activated(self, attrModel):
        self.debug("on_gaugeCombo_activated()\tattrModel:" % attrModel)
        if ( attrModel ):
            self.hidePressureCurve()
            self.setPressureModel(self.pressureCombo.currentText() + "/" + attrModel)
            self.gaugeValue.setModel(self.pressureModel())
            self.togglePressureCurve(self.isStarted())
        else:
            self.gaugeValue.resetModel()
            self.hidePressureCurve()
            self.resetPressureModel()
  
#    on_gaugeCombo_currentIdnexChanged()

    @QtCore.pyqtSignature("")
    def on_removeButton_clicked(self):
        atRow = self._removeButtons.index(self.sender())
        valid = self.isStepValid(atRow)
        self.table.removeRow(atRow)
        self._removeButtons.pop(atRow)
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
                valid = self.isStepValid(0)
            self.table.removeRow(0)
        self._removeButtons = []
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
            self.resetPressureModel()
            self.graphPlot.resetModel()
            self.listener().setModel("/Temperature_All")
            channels = self.channels()
            modelObj.write_attribute("Program_%s" % self.number(), self.program())
            modelObj.write_attribute("Program_%s_Zones" % self.number(), channels)
            self.updateProgram()
        
#    onSaveButton_clicked()

    @QtCore.pyqtSignature("")
    def on_startButton_clicked(self):
        self.debug("on_startButton_clicked")       
        modelObj = self.getModelObj()
        if ( modelObj ):
            self.setStarted(True)
            self.setRunning(True)
            modelObj.Start(self.number())
            self.listener().setModel("/Program_%s_Params" % self.number())
            self.updateProgram()
            self.togglePressureCurve(True)
            for channel in self.channels():
                self.toggleTempCurve(channel, True)
        
#    onStartButton_clicked()

    @QtCore.pyqtSignature("")
    def on_stopButton_clicked(self):
        self.debug("on_stopButton_clicked")
        modelObj = self.getModelObj()
        if ( modelObj ):
            self.setRunning(False)
            modelObj.Stop(self.number())
            self.updateProgram()
            
#    on_stopButton_clicked()

    def on_table_itemChanged(self, item):
        self.debug("on_table_itemChanged()")
        atRow = self.table.row(item)
        if ( self.isStepValid(atRow) ):
            self.setModified(True)
            self.updateProgram()

#    on_table_itemChanged()

    def on_channelCheckBox1_stateChanged(self, state):
        self.on_checkBox_stateChanged(1, state)    
    
#    on_channelCheckBox1_stateChanged()
    
    def on_channelCheckBox2_stateChanged(self, state):
        self.on_checkBox_stateChanged(2, state)    
    
#    on_channelCheckBox2_stateChanged()
    
    def on_channelCheckBox3_stateChanged(self, state):
        self.on_checkBox_stateChanged(3, state)    
    
#    on_channelCheckBox3_stateChanged()
    
    def on_channelCheckBox4_stateChanged(self, state):
        self.on_checkBox_stateChanged(4, state)    
    
#    on_channelCheckBox4_stateChanged()
    
    def on_channelCheckBox5_stateChanged(self, state):
        self.on_checkBox_stateChanged(5, state)    
    
#    on_channelCheckBox5_stateChanged()
    
    def on_channelCheckBox6_stateChanged(self, state):
        self.on_checkBox_stateChanged(6, state)    
    
#    on_channelCheckBox6_stateChanged()
    
    def on_channelCheckBox7_stateChanged(self, state):
        self.on_checkBox_stateChanged(7, state)    
    
#    on_channelCheckBox7_stateChanged()
    
    def on_channelCheckBox8_stateChanged(self, state):
        self.on_checkBox_stateChanged(8, state)    
    
#    on_channelCheckBox8_stateChanged()
    
    def on_checkBox_stateChanged(self, channel, state):
        self.debug("on_checkBox_stateChanged()\tchannel: %s\tstate: %s" % (channel, state))
        self.setModified(True)
        self.setChannelState(channel, state)
        if ( isinstance(self.window(), BakeOutProgrammerMainWindow) ):
            self.window().setChannelState(channel, state)
            self.window().setChannelsDisabled(channel)
        self.channelOutput(channel).setEnabled(state)
#        self.channelLimit(channel).setEnabled(state)
        if ( state ):
            self.channelOutput(channel).setModel("/Output_%s" % channel)
#            self.channelLimit(channel).setModel("/Output_%s_Limit" % channel)            
        else:
            self.channelOutput(channel).resetModel()
#            self.channelLimit(channel).resetModel()      
        self.updateTabText()
        self.updateProgram()
        self.toggleTempCurve(channel, state)
            
#    on_checkBox_stateChanged()
 
    def listener(self):
        return self._listener
    
#    listener()
  
    def program(self):
        return self._program
    
#    program()
   
    def setProgram(self, value):
        self._program = value
                
#    setProgram()

    def resetPressureModel(self):
        self._pressureModel = ""
        
#    resetPressureModel()
  
    def setPressureModel(self, model):
        self._pressureModel = str(model)
        
#    setPressureModel()
  
    def pressureModel(self):
        return self._pressureModel
    
#    pressureModel()
  
    def startTemp(self):
        return self._startTemp
    
#    startTemp()

    def setStartTemp(self, temp):
        if ( self._startTemp != temp ):
            self._startTemp = temp
            return True
        return False
            
#    setStartTemp()

    def startTime(self):
        return self._startTime
    
#    startTime()

    def setStartTime(self, time):
        if ( self._startTime != time ):
            self._startTime = time
            return True
        return False
            
#    setStartTemp()

    def resetStartTime(self):
        if ( self._startTime ):
            self._startTime = 0.
            
#    resetStartTime()

    def finishTime(self):
        return self._finishTime
    
#    finishTime()

    def setFinishTime(self, time):
        if ( self._finishTime != time ):
            self._finishTime = time
            return True
        return False
            
#    setFinishTime()

    def pauseTime(self):
        return self._pauseTime
    
#    pauseTime()

    def setPauseTime(self, time):
        if ( self._pauseTime != time ):
            self._pauseTime = time
            
#    setPauseTime()

    def number(self):
        return self._number
    
#    number()

    def setNumber(self, value):
        self._number = value
        
#    setNumber()
 
    def channels(self):
        return [z for z in range(1, 9) if self.channelState(z)]
    
#    channels()
      
    def channelState(self, channel):
        return self._channelStates[channel - 1]
    
#    channelState()
   
    def setChannelState(self, channel, state):
        self._channelStates[channel - 1] = state
        
#    setChannelState()
   
    def channelGroupBox(self, channel):
        return self._cGroupBoxes[channel - 1]
    
#    channelGroupBox()
   
    def channelCheckBox(self, channel):
        return self._cCheckBoxes[channel - 1]
    
#    channelCheckBox()

    def channelTemp(self, channel):
        return self._cTemps[channel - 1]
    
#    channelTemp()

    def channelLimit(self, channel):
        return self._cLimits[channel - 1]
    
#    channelLimit()
   
    def channelOutput(self, channel):
        return self._cOutputs[channel - 1]
    
#    channelOutput()

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

    def loadProgram(self, number, program, channels):
        self.debug("loadProgram()")
        self.setNumber(number)
        modelObj = self.getModelObj()
        if ( modelObj ):
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
            params = modelObj.getAttribute("Program_%s_Params" % self.number()).read().value.tolist()
            if ( params[3] ):
                self.setRunning(False)
            if ( params[1] ):
                self.setStarted(True)
                self.setRunning(True)
                self.listener().setModel("/Program_%s_Params" % self.number())          
            if ( channels ):
                for channel in channels:
                    self.channelCheckBox(channel).setCheckState(QtCore.Qt.Checked)
                self.setModified(False)
            else:
                self.updateTabText()
            self.updateProgram()
        
#    loadProgram()

    def setChannelDisabled(self, channel=None):
        if ( isinstance(self.window(), BakeOutProgrammerMainWindow) ):        
            for channel in channel and (channel,) or range(1, 9):
                checkBox = self.channelCheckBox(channel)
                if ( not checkBox.isChecked() ):
                    self.channelGroupBox(channel).setDisabled(self.window().channelState(channel))

#    setChannelDisabled()

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
            if ( len(step) == 3 ):
                program.append(step)
        self.setProgram(program or [PROGRAM_DEFAULT])
        self.updateProgramCurve()

#    updateProgram()

    def updateProgramCurve(self):
        self.debug("updateProgramCurve()")
        rawData = self.toRawData(self._program, self.startTime(), self.startTemp())
        if ( rawData != [PROGRAM_DEFAULT] ):
            xData, yData = rawData
            if ( self.graphPlot.getCurve("Program") ):
                self.graphPlot.getCurve("Program").setData(xData, yData)
            else:
                self.graphPlot.attachRawData(dict(zip(("title", "x", "y"), ("Program", xData, yData))))
        else:
            if ( self.graphPlot.getCurve("Program") ):
                self.graphPlot.detachRawData("Program")
                
        self.graphPlot.replot()
            
#    updateProgramCurve()

    def updateProgressBars(self):
        self.debug("updateProgressBar()")
        if ( self.isRunning() ):
            now = QtCore.QDateTime().currentDateTime().toTime_t()
            self.currentProgressBar.setValue(now)
            self.overallProgressBar.setValue(now)
        elif ( self.isStarted() ):
            fTime = self.finishTime()
            if ( self.currentProgressBar.value() != fTime ):
                self.currentProgressBar.setValue(fTime)
            if ( self.overallProgressBar.value() != fTime ):
                self.overallProgressBar.setValue(fTime)
        else:
            self.currentProgressBar.reset()
            self.overallProgressBar.reset()
        
#    updateProgressBars()      

    def updateTabText(self):
        self.debug("updateTabText()")
        if ( isinstance(self.window(), BakeOutProgrammerMainWindow) ):
            tabWidget = self.window().tabWidget
            currentIndex = tabWidget.indexOf(self)
            channels = self.reduceChannels(map(str, self.channels()))
            tabText = "Program " + str(self.number()) +\
                   ((" [Channels " if ( len(channels) > 1 or len(channels[0]) > 1 ) else " [Channel ") +\
                   ", ".join(channels) + "]" if ( len(channels) > 0 ) else "")
            tabWidget.setTabText(currentIndex, tabText)
        
#    updateTabText()

    def reduceChannels(self, strChannels):
        for i in range(len(strChannels) - 1):
            if ( (int(strChannels[i + 1][0]) - int(strChannels[i][-1])) == 1 ):
                strChannels[i + 1] = strChannels[i][0] + "-" + strChannels[i + 1]
                strChannels.pop(i)
                return self.reduceChannels(strChannels)
        return strChannels

#    reduceChannels()

    def toggleTempCurve(self, channel, on):
        self.debug("toggleTempCurve()\tchannel: %s\ton: %s" % (channel, on))
        if ( self.isStarted() ):
            modelObj = self.getModelObj()
            if ( modelObj ): 
                model = "%s/Temperature_%s" % (modelObj.getNormalName(), channel)
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
                    self.graphPlot.setCurvesYAxis([model + "[0]"], Qwt.QwtPlot.yRight)
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
                self.connect(removeButton,
                             QtCore.SIGNAL("clicked()"),
                             self.on_removeButton_clicked)
                self._removeButtons.append(removeButton)
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

    def toRawData(self, program, x0=long(0), y0=TEMP_ROOM):
        if ( program == [PROGRAM_DEFAULT] ):
            return program
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

    def isStepValid(self, row):
        self.debug("isStepValid()\trow: %s" % row)
        rowItems = (self.table.item(row, col) for col in range(self.table.columnCount() - 1))
        return all([ok[1] for ok in (item.text().toDouble() for item in rowItems)])
    
#    isStepValid()

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
        self.insertEventFilter(self.valueChangedFilter)
                                 
#    __init__()

    def valueChangedFilter(self, src, type, value):
        if ( type in (TauEventType.Change, TauEventType.Periodic) ):
            return src, type, value
        
#    valueChangedFilter()
                                 
    def handleEvent(self, src, type, value):
        if ( value ):
            self.emit(QtCore.SIGNAL("valueChanged(PyQt_PyObject)"), value.value.tolist())
        else:
            self.warning("Unexpected event value: %s" % value)
                        
#    handleEvent()
    
#BakeOutListener()

if ( __name__ == "__main__" ):
    import sys
    app = QtGui.QApplication(sys.argv)
    mainWindow = BakeOutProgrammerMainWindow()
    mainWindow.showMaximized()
    sys.exit(app.exec_())