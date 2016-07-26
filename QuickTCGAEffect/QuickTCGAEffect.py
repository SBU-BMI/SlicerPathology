import os
import json
import vtk, qt, ctk, slicer
import EditorLib
from EditorLib.EditOptions import HelpButton
from EditorLib.EditOptions import EditOptions
from EditorLib import EditUtil
from EditorLib import LabelEffect

# Added libs
from EditorLib import Effect
from EditorLib import LabelEffectLogic

from copy import copy, deepcopy
import numpy as np
params = {}
cparams = {"algorithm":"Yi"}

#
# The Editor Extension itself.
#
# This needs to define the hooks to be come an editor effect.
#

#
# QuickTCGAEffectOptions - see LabelEffect, EditOptions and Effect for superclasses
#

class QuickTCGAEffectOptions(EditorLib.LabelEffectOptions):
  """ QuickTCGAEffect-specfic gui
  """

  def __init__(self, parent=0):
    super(QuickTCGAEffectOptions,self).__init__(parent)
    editUtil = EditorLib.EditUtil.EditUtil()
    parameterNode = editUtil.getParameterNode()
    lm = slicer.app.layoutManager()
    self.redSliceWidget = lm.sliceWidget('Red')
    self.yellowSliceWidget = lm.sliceWidget('Yellow')
    self.greenSliceWidget = lm.sliceWidget('Green')
    self.parameterNode=parameterNode
    self.attributes = ('MouseTool')
    self.displayName = 'QuickTCGAEffect Effect'
    self.omode = 0

  def __del__(self):
    super(QuickTCGAEffectOptions,self).__del__()

  def create(self):
    super(QuickTCGAEffectOptions,self).create()
    self.helpLabel = qt.QLabel("Press Y to run automatic segmentation on the current image using given parameters.", self.frame)
    self.frame.layout().addWidget(self.helpLabel)

    #create a "Start Bot" button
    self.botButton = qt.QPushButton(self.frame)
    self.botButton.text = "Start Quick TCGA Segmenter"
    self.frame.layout().addWidget(self.botButton)
    self.botButton.connect('clicked()', self.onStartBot)

    self.clearButton = qt.QPushButton(self.frame)
    self.clearButton.text = "Clear Selection"
    self.frame.layout().addWidget(self.clearButton)
    self.clearButton.connect('clicked()', self.clearSelection)

    self.segButton = qt.QPushButton(self.frame)
    self.segButton.text = "Run Segmentation"
    self.frame.layout().addWidget(self.segButton)
    self.segButton.connect('clicked()', self.RunSegmenter)

    self.outlineButton = qt.QPushButton(self.frame)
    self.outlineButton.text = "Toggle Outline"
    self.frame.layout().addWidget(self.outlineButton)
    self.outlineButton.connect('clicked()', self.toggleOutline)

    self.locRadFrame = qt.QFrame(self.frame)
    self.locRadFrame.setLayout(qt.QHBoxLayout())
    self.frame.layout().addWidget(self.locRadFrame)
    self.widgets.append(self.locRadFrame)

    # Nucleus segmentation parameters (Yi Gao's algorithm)
    nucleusSegCollapsibleButton = ctk.ctkCollapsibleButton()
    nucleusSegCollapsibleButton.text = "Nucleus Segmentation Parameters (Yi Gao)"
    nucleusSegCollapsibleButton.collapsed = True;
    self.frame.layout().addWidget(nucleusSegCollapsibleButton)

    self.structuresView = slicer.util.findChildren(slicer.modules.SlicerPathologyWidget.editorWidget.volumes, 'StructuresView')[0]
    self.structuresView.connect("activated(QModelIndex)", self.onStructureClickedOrAdded)

    # Layout within the parameter button
    nucleusSegFormLayout = qt.QFormLayout(nucleusSegCollapsibleButton)
    self.frameOtsuSlider = ctk.ctkSliderWidget()
    self.frameOtsuSlider.connect('valueChanged(double)', self.OtsuSliderValueChanged)
    self.frameOtsuSlider.decimals = 1
    self.frameOtsuSlider.minimum = 0.5
    self.frameOtsuSlider.maximum = 1.5
    self.frameOtsuSlider.value = 1.0
    self.frameOtsuSlider.singleStep = 0.1
    nucleusSegFormLayout.addRow("Otsu Threshold:", self.frameOtsuSlider)

    self.frameCurvatureWeightSlider = ctk.ctkSliderWidget()
    self.frameCurvatureWeightSlider.connect('valueChanged(double)', self.CurvatureWeightSliderValueChanged)
    self.frameCurvatureWeightSlider.decimals = 1
    self.frameCurvatureWeightSlider.minimum = 0
    self.frameCurvatureWeightSlider.maximum = 10
    self.frameCurvatureWeightSlider.value = 8
    self.frameCurvatureWeightSlider.singleStep = 0.1
    nucleusSegFormLayout.addRow("Curvature Weight:", self.frameCurvatureWeightSlider)

    self.frameSizeThldSlider = ctk.ctkSliderWidget()
    self.frameSizeThldSlider.connect('valueChanged(double)', self.SizeThldSliderValueChanged)
    self.frameSizeThldSlider.decimals = 1
    self.frameSizeThldSlider.minimum = 1
    self.frameSizeThldSlider.maximum = 30
    self.frameSizeThldSlider.value = 3
    self.frameSizeThldSlider.singleStep = 0.1
    nucleusSegFormLayout.addRow("Size Threshold:", self.frameSizeThldSlider)

    self.frameSizeUpperThldSlider = ctk.ctkSliderWidget()
    self.frameSizeUpperThldSlider.connect('valueChanged(double)', self.SizeUpperThldSliderValueChanged)
    self.frameSizeUpperThldSlider.decimals = 0
    self.frameSizeUpperThldSlider.minimum = 1
    self.frameSizeUpperThldSlider.maximum = 500
    self.frameSizeUpperThldSlider.value = 50
    nucleusSegFormLayout.addRow("Size Upper Threshold:", self.frameSizeUpperThldSlider)

    self.frameKernelSizeSlider = ctk.ctkSliderWidget()
    self.frameKernelSizeSlider.connect('valueChanged(double)', self.KernelSizeSliderValueChanged)
    self.frameKernelSizeSlider.decimals = 0
    self.frameKernelSizeSlider.minimum = 1
    self.frameKernelSizeSlider.maximum = 30
    self.frameKernelSizeSlider.value = 20
    nucleusSegFormLayout.addRow("Kernel Size:", self.frameKernelSizeSlider)

    self.frameMPPSlider = ctk.ctkSliderWidget()
    self.frameMPPSlider.connect('valueChanged(double)', self.MPPSliderValueChanged)
    self.frameMPPSlider.decimals = 5
    self.frameMPPSlider.minimum = 0.01
    self.frameMPPSlider.maximum = 1
    self.frameMPPSlider.value = 0.25
    self.frameMPPSlider.singleStep = 0.01
    nucleusSegFormLayout.addRow("Micron Per Pixel:", self.frameMPPSlider)


    HelpButton(self.frame, ("TO USE: \n Start the QuickTCGA segmenter and initialize the segmentation with any other editor tool like PaintEffect. Press the following keys to interact:" +
     "\n KEYS for Global Segmentation: " +
      "\n S: start Global segmentation \n E: toggle between seed image and segmentation result" +
      " \n R: reset seed/label image for Global Segmentation " +
      "\n F: toggle between selected ROI(Region of Interest) and segmentation result" +
      "\n Space key to go back to Slicer mode"
      "\n \nKEYS for ShortCut"
      "\n C: start ShortCut to refine the segmentation inside ROI"+
      "\n N: run ShortCut" +
      "\n R: reset ShortCut parameters"
      "\n Q: quit ShortCut" +
      "\n Mouse: LEFT for foreground, RIGHT for background") )
    self.frame.layout().addStretch(1) # Add vertical spacer

    if hasattr(slicer.modules, 'TCGAEditorBot'):
      slicer.util.showStatusMessage(slicer.modules.TCGAEditorBot.logic.currentMessage)
      self.botButton.text = "Stop Quick TCGA Segmenter"
    if self.locRadFrame:
      self.locRadFrame.hide()
    else:
      self.botButton.text = "Start Quick TCGA Segmenter"
    if self.locRadFrame:
      self.locRadFrame.show()
    self.omode = 0
    self.toggleOutline()

  def destroy(self):
    self.currentMessage = ""
    slicer.util.showStatusMessage(self.currentMessage)
    super(QuickTCGAEffectOptions,self).destroy()

  def RunSegmenter(self):
    if hasattr(slicer.modules, 'TCGAEditorBot'):
      slicer.modules.TCGAEditorBot.logic.runQTCGA_NucleiSegYi()

  def toggleOutline(self):
    if (self.omode == 1):
      self.omode = 0
    else:
      self.omode = 1
    self.editUtil.setLabelOutline(self.omode)

  def clearSelection(self):
    EditUtil.EditUtil().getParameterNode().UnsetParameter("QuickTCGAEffect,currentXYPosition")
    EditUtil.EditUtil().getParameterNode().UnsetParameter("QuickTCGAEffect,startXYPosition")
    slicer.modules.QuickTCGAEffectTool.startXYPosition = (0,0)
    slicer.modules.QuickTCGAEffectTool.currentXYPosition = (0,0)
    slicer.modules.QuickTCGAEffectTool.updateGlyph()
    slicer.modules.QuickTCGAEffectTool.sliceView.scheduleRender()

  def updateSliders(self):
    r = self.structuresView.currentIndex().row()
    if (r>-1):
      ei = slicer.modules.SlicerPathologyWidget.editorWidget.helper.structures.item(r,3).text()
    else:
      ei = EditUtil.EditUtil().getParameterNode().GetParameter('SlicerPathology,tilename')+'-label'
    if ei not in params:
      params[ei] = cparams.copy()
      if (r<0):
        params[ei]['label'] = slicer.modules.SlicerPathologyWidget.editorWidget.helper.editUtil.getLabelName()
      else:
        params[ei]['label'] = slicer.modules.SlicerPathologyWidget.editorWidget.helper.structures.item(r,2).text()
      jstr = json.dumps(params,sort_keys=True, indent=4, separators=(',', ': '))
      self.parameterNode.SetParameter("QuickTCGAEffect,erich", jstr)
    self.frameOtsuSlider.value = params[ei]["otsuRatio"]
    self.frameCurvatureWeightSlider.value = params[ei]["curvatureWeight"]
    self.frameSizeThldSlider.value = params[ei]["sizeThld"]
    self.frameSizeUpperThldSlider.value = params[ei]["sizeUpperThld"]
    self.frameMPPSlider.value = params[ei]["mpp"]
    self.frameKernelSizeSlider.value = params[ei]["KernelSize"]

  def onStructureClickedOrAdded(self):
    self.updateSliders();

  def updateParam(self,p,v):
    r = self.structuresView.currentIndex().row()
    if (r>-1):
      ei = slicer.modules.SlicerPathologyWidget.editorWidget.helper.structures.item(r,3).text()
    else:
      ei = EditUtil.EditUtil().getParameterNode().GetParameter('SlicerPathology,tilename')+'-label'
    if ei not in params:
      params[ei] = cparams.copy()
      if (r<0):
        params[ei]['label'] = slicer.modules.SlicerPathologyWidget.editorWidget.helper.editUtil.getLabelName()
      else:
        params[ei]['label'] = slicer.modules.SlicerPathologyWidget.editorWidget.helper.structures.item(r,2).text()
    params[ei][p] = v
    cparams[p] = v
    jstr = json.dumps(params,sort_keys=True, indent=4, separators=(',', ': '))
    self.parameterNode.SetParameter("QuickTCGAEffect,erich", jstr)

  def OtsuSliderValueChanged(self,value):
    self.parameterNode.SetParameter("QuickTCGAEffect,otsuRatio", str(value))
    self.updateParam("otsuRatio",value)
    self.updateMRMLFromGUI()

  def CurvatureWeightSliderValueChanged(self,value):
    self.parameterNode.SetParameter("QuickTCGAEffect,curvatureWeight", str(value))
    self.updateParam("curvatureWeight",value)
    self.updateMRMLFromGUI()

  def SizeThldSliderValueChanged(self,value):
    self.parameterNode.SetParameter("QuickTCGAEffect,sizeThld", str(value))
    self.updateParam("sizeThld",value)
    self.updateMRMLFromGUI()

  def SizeUpperThldSliderValueChanged(self,value):
    self.parameterNode.SetParameter("QuickTCGAEffect,sizeUpperThld", str(value))
    self.updateParam("sizeUpperThld",value)
    self.updateMRMLFromGUI()

  def MPPSliderValueChanged(self,value):
    self.parameterNode.SetParameter("QuickTCGAEffect,mpp", str(value))
    self.updateParam("mpp",value)
    self.updateMRMLFromGUI()

  def KernelSizeSliderValueChanged(self,value):
    self.parameterNode.SetParameter("QuickTCGAEffect,kernelSize", str(value))
    self.updateParam("kernelSize",value)
    self.updateMRMLFromGUI()


  # note: this method needs to be implemented exactly as-is
  # in each leaf subclass so that "self" in the observer
  # is of the correct type
  def updateParameterNode(self, caller, event):
    node = EditUtil.EditUtil().getParameterNode()
    if node != self.parameterNode:
      if self.parameterNode:
        node.RemoveObserver(self.parameterNodeTag)
      self.parameterNode = node
      self.parameterNodeTag = node.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updateGUIFromMRML)

  def setMRMLDefaults(self):
    super(QuickTCGAEffectOptions,self).setMRMLDefaults()

  def onStartBot(self):
    print "onStartBot is starting..."
    """Stop Quick TCGA bot to avoid conflicts"""
    if hasattr(slicer.modules, 'editorBot'):
      slicer.modules.editorBot.stop()
      del(slicer.modules.editorBot)

    """create the bot for background editing"""
    if hasattr(slicer.modules, 'TCGAEditorBot'):
      slicer.modules.TCGAEditorBot.stop()
      del(slicer.modules.TCGAEditorBot)
      if self.botButton:
        self.botButton.text = "Start Quick TCGA Segmenter"
        slicer.util.showStatusMessage("TCGA Segmenter: stopped")
      if self.locRadFrame:
        self.locRadFrame.show()
    else:
      TCGASegBot(self)
      slicer.modules.TCGAEditorBot.logic.emergencyStopFunc = self.botEstop; #save the function that stops bot, destroys ShortCut segmenter, if things go wrong
      if self.botButton:
        self.botButton.text = "Stop Quick TCGA Segmenter"
        self.currentMessage =  "Quick TCGA Segmenter started: Press 'Y' to start automatic nucleus segmentation; Or go to PaintEffect to edit label image."
        slicer.util.showStatusMessage(self.currentMessage)

      if self.locRadFrame:
        self.locRadFrame.hide()

  def updateGUIFromMRML(self,caller,event):
    self.disconnectWidgets()
    super(QuickTCGAEffectOptions,self).updateGUIFromMRML(caller,event)
    self.connectWidgets()

  def updateMRMLFromGUI(self):
    if self.updatingGUI:
      return
    disableState = self.parameterNode.GetDisableModifiedEvent()
    self.parameterNode.SetDisableModifiedEvent(1)
    super(QuickTCGAEffectOptions,self).updateMRMLFromGUI()
    self.parameterNode.SetDisableModifiedEvent(disableState)
    if not disableState:
      self.parameterNode.InvokePendingModifiedEvent()


  def botEstop(self):
    if hasattr(slicer.modules, 'TCGAEditorBot'):
      slicer.modules.TCGAEditorBot.stop()
      del(slicer.modules.TCGAEditorBot)
      if self.botButton:
        self.botButton.text = "Start Quick TCGA Segmenter"
      if self.locRadFrame:
        self.locRadFrame.show()

class TCGASegBot(object): #stays active even when running the other editor effects
  """
Task to run in the background for this effect.
Receives a reference to the currently active options
so it can access tools if needed.
"""
  def __init__(self,options):
    self.editUtil = EditUtil.EditUtil()
    #self.sliceWidget = options.tools[0].sliceWidget
    self.sliceWidget = slicer.app.layoutManager().sliceWidget('Red')
    if hasattr(slicer.modules, 'TCGAEditorBot'):
      slicer.modules.TCGAEditorBot.active = False
      del(slicer.modules.TCGAEditorBot)
    slicer.modules.TCGAEditorBot = self

    self.redSliceWidget=options.redSliceWidget
    self.greenSliceWidget=options.greenSliceWidget
    self.yellowSliceWidget=options.yellowSliceWidget
    self.start()

  def start(self):
    sliceLogic = self.sliceWidget.sliceLogic()
    self.logic = QuickTCGAEffectLogic( self.redSliceWidget.sliceLogic() )

  def stop(self):
    self.logic.destroy()

#
# QuickTCGAEffectTool
#

class QuickTCGAEffectTool(LabelEffect.LabelEffectTool):
  """
  One instance of this will be created per-view when the effect
  is selected.  It is responsible for implementing feedback and
  label map changes in response to user input.
  This class observes the editor parameter node to configure itself
  and queries the current view for background and label volume
  nodes to operate on.
  """

  def __init__(self, sliceWidget):
    super(QuickTCGAEffectTool,self).__init__(sliceWidget)
    # create a logic instance to do the non-gui work
    #self.logic = QuickTCGAEffectLogic(self.sliceWidget.sliceLogic())

    self.sliceWidget = sliceWidget
    self.sliceLogic = sliceWidget.sliceLogic()
    self.sliceView = self.sliceWidget.sliceView()
    self.interactor = self.sliceView.interactorStyle().GetInteractor()
    self.renderWindow = self.sliceWidget.sliceView().renderWindow()

    self.actionState = None
    self.startXYPosition = None
    self.currentXYPosition = None

    self.createGlyph()

    self.mapper = vtk.vtkPolyDataMapper2D()
    self.actor = vtk.vtkActor2D()
    self.mapper.SetInputData(self.polyData)
    self.actor.SetMapper(self.mapper)
    property_ = self.actor.GetProperty()
    property_.SetColor(1,1,0)
    property_.SetLineWidth(1)
    self.renderer.AddActor2D( self.actor )
    self.actors.append( self.actor )
    slicer.modules.QuickTCGAEffectTool = self

  def cleanup(self):
    super(QuickTCGAEffectTool,self).cleanup()

  def createGlyph(self):
    self.polyData = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()
    self.polyData.SetPoints( points )
    self.polyData.SetLines( lines )
    prevPoint = None
    firstPoint = None
    for x,y in ((0,0),)*4:
      p = points.InsertNextPoint( x, y, 0 )
      if prevPoint is not None:
        idList = vtk.vtkIdList()
        idList.InsertNextId( prevPoint )
        idList.InsertNextId( p )
        self.polyData.InsertNextCell( vtk.VTK_LINE, idList )
      prevPoint = p
      if firstPoint is None:
        firstPoint = p
    # make the last line in the polydata
    idList = vtk.vtkIdList()
    idList.InsertNextId( p )
    idList.InsertNextId( firstPoint )
    self.polyData.InsertNextCell( vtk.VTK_LINE, idList )
    self.updateGlyph()

  def updateGlyph(self):
    if not self.startXYPosition or not self.currentXYPosition:
      return
    points = self.polyData.GetPoints()
    xlo,ylo = self.startXYPosition
    xhi,yhi = self.currentXYPosition
    points.SetPoint( 0, xlo, ylo, 0 )
    points.SetPoint( 1, xlo, yhi, 0 )
    points.SetPoint( 2, xhi, yhi, 0 )
    points.SetPoint( 3, xhi, ylo, 0 )

  def processEvent(self, caller=None, event=None):
    """
handle events from the render window interactor
"""
    if event == "LeftButtonPressEvent":
      self.actionState = "dragging"
      self.cursorOff()
      xy = self.interactor.GetEventPosition()
      self.startXYPosition = xy
      self.currentXYPosition = xy
      EditUtil.EditUtil().getParameterNode().SetParameter("QuickTCGAEffect,startXYPosition", str(xy))
      EditUtil.EditUtil().getParameterNode().SetParameter("QuickTCGAEffect,currentXYPosition", str(xy))
      self.updateGlyph()
      self.abortEvent(event)
#      viewName,orient = get_view_names(self.sliceWidget)
#      ijk= smart_xyToIJK(xy,self.sliceWidget)
#      if not orient:
#        print "Warning, unexpected view orientation!?"
    elif event == "LeftButtonReleaseEvent":
      self.actionState = ""
      self.cursorOn()
      ##self.apply()
      #self.startXYPosition = (0,0)
      #self.currentXYPosition = (0,0)
      #self.updateGlyph()
      self.abortEvent(event)
    elif event == "MouseMoveEvent":
      if self.actionState == "dragging":
        self.currentXYPosition = self.interactor.GetEventPosition()
        a = abs(self.currentXYPosition[0]-self.startXYPosition[0])
        b = abs(self.currentXYPosition[1]-self.startXYPosition[1])
        c = self.startXYPosition[0]
        d = self.startXYPosition[1]
        if (a<b):
          self.currentXYPosition = (c+a,d-a)
        else:
          self.currentXYPosition = (c+b,d-b)
        EditUtil.EditUtil().getParameterNode().SetParameter("QuickTCGAEffect,currentXYPosition", str(self.currentXYPosition))
        self.updateGlyph()
        self.sliceView.scheduleRender()
        self.abortEvent(event)
    if event == 'EnterEvent':
      pass #print "EnterEvent in KSliceEffect."
    else:
      pass
  def apply(self):
    lines = self.polyData.GetLines()
    if lines.GetNumberOfCells() == 0: return
    self.logic.undoRedo = self.undoRedo
    self.logic.applyPolyMask(self.polyData)

#
# QuickTCGAEffectLogic
#

class QuickTCGAEffectLogic(LabelEffect.LabelEffectLogic):
  """
  This class contains helper methods for a given effect
  type.  It can be instanced as needed by an QuickTCGAEffectTool
  or QuickTCGAEffectOptions instance in order to compute intermediate
  results (say, for user feedback) or to implement the final
  segmentation editing operation.  This class is split
  from the QuickTCGAEffectTool so that the operations can be used
  by other code without the need for a view context.
  """

  def __init__(self,sliceLogic):
    print("Preparing Quick TCGA Interaction")
    self.attributes = ('MouseTool')
    self.displayName = 'QuickTCGA Effect'

    #disconnect all shortcuts that may exist, to allow QuickTCGA's to work, reconnect once bot is turned off
    slicer.modules.SlicerPathologyWidget.editorWidget.removeShortcutKeys()
    self.sliceLogic = sliceLogic
    self.editUtil = EditUtil.EditUtil()
    self.swRed = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
    self.sw = slicer.app.layoutManager().sliceWidget('Red')
    self.interactor = self.sw.sliceView().interactor() #initialize to red slice interactor
    #self.computeCurrSliceSmarter() #initialize the current slice to something meaningful

    self.mouse_obs_growcut, self.swLUT_growcut = bind_view_observers(self.updateShortCutROI)

    #initialize Fast GrowCut
    self.init_QuickTCGA()

    self.QuickTCGACreated=False

  def init_QuickTCGA(self):
    self.emergencyStopFunc = None
    self.dialogBox=qt.QMessageBox() #will display messages to draw users attention if he does anything wrong
    self.dialogBox.setWindowTitle("QuickTCGA Error")
    self.dialogBox.setWindowModality(qt.Qt.NonModal) #will allow user to continue interacting with Slicer

    # TODO: check this claim- might be causing leaks
    # set the image, label nodes (this will not change although the user can
    # alter what is bgrnd/frgrnd in editor)
    # Confused about how info propagates UIarray to UIVol, not the other way, NEEDS AUTO TESTS

    self.labelNode = self.editUtil.getLabelVolume() #labelLogic.GetVolumeNode()
    self.backgroundNode = self.editUtil.getBackgroundVolume() #backgroundLogic.GetVolumeNode()
    self.foregroundNode = self.swRed.GetForegroundLayer().GetVolumeNode()

    #perform safety check on right images/labels being selected, #set up images
    #if red slice doesnt have a label or image, go no further
    if type(self.backgroundNode)==type(None) or type(self.labelNode)==type(None):
      self.dialogBox.setText("Either Image (must be Background Image) or Label not set in slice views.")
      self.dialogBox.show()

    if self.emergencyStopFunc:
      self.emergencyStopFunc()
      return

    volumesLogic = slicer.modules.volumes.logic()

    self.labelName = self.labelNode.GetName() # record name of label so user, cant trick us
    self.imgBgrdName = self.backgroundNode.GetName()
    self.imgFgrdName = self.foregroundNode.GetName()

    if self.sliceViewMatchEditor(self.sliceLogic)==False: # do nothing, exit function if user has played with images
      if self.emergencyStopFunc:
        self.emergencyStopFunc()
        return

    # QuickTCGA shortcuts
  ##resetQTCGAKey = qt.QKeySequence(qt.Qt.Key_R) # reset initialization flag
  ##runQTCGAClusterKey = qt.QKeySequence(qt.Qt.Key_S) # run fast growcut
    runNucleiSegKey = qt.QKeySequence(qt.Qt.Key_Y)
  ##editTCGAKey = qt.QKeySequence(qt.Qt.Key_E) # edit seed labels
  ##runQTCGATemplateKey = qt.QKeySequence(qt.Qt.Key_T)
  ##runQTCGARefineCurvatureKey = qt.QKeySequence(qt.Qt.Key_U)
  ##runQTCGAShortCutKey = qt.QKeySequence(qt.Qt.Key_C)
  ##runQTCGAShortEditCutKey = qt.QKeySequence(qt.Qt.Key_F)

    print " key to run QuickTCGA segmentation is  Y"

    self.qtkeyconnections = []
    self.qtkeydefsQTCGA = [[runNucleiSegKey, self.runQTCGA_NucleiSegYi]]

    for keydef in self.qtkeydefsQTCGA:
      s = qt.QShortcut(keydef[0], slicer.util.mainWindow()) # connect this qt event to mainWindow focus
      s.connect('activated()', keydef[1])
      self.qtkeyconnections.append(s)

    self.qTCGALabMod_tag = self.sliceLogic.AddObserver("ModifiedEvent", self.QTCGAChangeLabelInput) # put test listener on the whole window

    # Quick TCGA parameters
    self.bEditTCGA = True
    self.bEditShortCut = False
    self.currentMessage = ""

    seedArray = slicer.util.array(self.labelName)
    self.qTCGASeedArray = seedArray.copy()
    self.qTCGASegArray = seedArray.copy()
    self.qTCGASeedArray[:] = 0
    self.qTCGASegArray[:] = 0

    self.SCutROIRad = 50
    self.volSize=self.labelNode.GetImageData().GetDimensions()
    self.qSCutROIArray = seedArray.copy() #np.zeros([self.volSize[0],self.volSize[1],1])
    self.qSCutROIArray[:] = 0

    roiVTK = vtk.vtkImageData()
    roiVTK.DeepCopy(self.labelNode.GetImageData())
    self.roiVTK = roiVTK

    import vtkSlicerQuickTCGAModuleLogicPython

    node = EditUtil.EditUtil().getParameterNode() # get the parameters from MRML
    otsuRatio = float(node.GetParameter("QuickTCGAEffect,otsuRatio"))
    curvatureWeight = float(node.GetParameter("QuickTCGAEffect,curvatureWeight"))/10
    sizeThld = float(node.GetParameter("QuickTCGAEffect,sizeThld"))
    sizeUpperThld = float(node.GetParameter("QuickTCGAEffect,sizeUpperThld"))
    mpp = float(node.GetParameter("QuickTCGAEffect,mpp"))
    kernelSize = float(node.GetParameter("QuickTCGAEffect,kernelSize"))
    cparams["otsuRatio"]=otsuRatio
    cparams["curvatureWeight"]=curvatureWeight
    cparams["sizeThld"]=sizeThld
    cparams["sizeUpperThld"]=sizeUpperThld
    cparams["mpp"]=mpp
    cparams["kernelSize"]=kernelSize
    qTCGAMod =vtkSlicerQuickTCGAModuleLogicPython.vtkQuickTCGA()
    qTCGAMod.SetSourceVol(self.foregroundNode.GetImageData())
    qTCGAMod.SetotsuRatio(otsuRatio)
    qTCGAMod.SetcurvatureWeight(curvatureWeight)
    qTCGAMod.SetsizeThld(sizeThld)
    qTCGAMod.SetsizeUpperThld(sizeUpperThld)
    qTCGAMod.Setmpp(mpp)
    qTCGAMod.SetkernelSize(kernelSize)
    qTCGAMod.Initialization()
    self.qTCGAMod = qTCGAMod
    self.QuickTCGACreated=True #tracks if completed the initializtion (so can do stop correctly) of KSlice

    # run Quick TCGA segmenter for the current master volume and label volume

  def runQTCGA_NucleiSegYi(self):
    self.currentMessage = "Quick TCGA: running nucleus segmentation ..."
    slicer.util.showStatusMessage(self.currentMessage)
    seedArray = slicer.util.array(self.labelNode.GetName())
    self.qTCGASeedArray[:]  = seedArray[:]
    node = EditUtil.EditUtil().getParameterNode() # get the parameters from MRML
    otsuRatio = float(node.GetParameter("QuickTCGAEffect,otsuRatio"))
    curvatureWeight = float(node.GetParameter("QuickTCGAEffect,curvatureWeight"))/10
    sizeThld = float(node.GetParameter("QuickTCGAEffect,sizeThld"))
    sizeUpperThld = float(node.GetParameter("QuickTCGAEffect,sizeUpperThld"))
    mpp = float(node.GetParameter("QuickTCGAEffect,mpp"))
    kernelSize = float(node.GetParameter("QuickTCGAEffect,kernelSize"))
    self.qTCGAMod.SetotsuRatio(otsuRatio)
    self.qTCGAMod.SetcurvatureWeight(curvatureWeight)
    self.qTCGAMod.SetsizeThld(sizeThld)
    self.qTCGAMod.SetsizeUpperThld(sizeUpperThld)
    self.qTCGAMod.Setmpp(mpp)
    self.qTCGAMod.SetkernelSize(kernelSize)
    print("hererere.........")
    AA = self.foregroundNode.GetImageData()
    LL = self.labelNode.GetImageData()
    ddd = AA.GetDimensions()
    cp = EditUtil.EditUtil().getParameterNode().GetParameter('QuickTCGAEffect,currentXYPosition')
    if cp.__len__() == 0:
      a = (0,0)
      b = (ddd[0]-1,ddd[1]-1)
      slicer.modules.SlicerPathologyWidget.SaveButton.setEnabled(1)
    else:
      currentXYPosition = eval(cp)
      startXYPosition = eval(EditUtil.EditUtil().getParameterNode().GetParameter('QuickTCGAEffect,startXYPosition'))
      sliceLogic = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
      labelLogic = sliceLogic.GetLabelLayer()
      xyToIJK = labelLogic.GetXYToIJKTransform()
      currentXYPosition = xyToIJK.TransformDoublePoint(currentXYPosition+(0,))
      currentXYPosition = (int(round(currentXYPosition[0])), int(round(currentXYPosition[1])))
      startXYPosition = xyToIJK.TransformDoublePoint(startXYPosition+(0,))
      startXYPosition = (int(round(startXYPosition[0])), int(round(startXYPosition[1])))
      a = startXYPosition
      b = currentXYPosition
      slicer.modules.SlicerPathologyWidget.SaveButton.setEnabled(0)
    # d = min(abs(b[0]-a[0]), abs(b[1]-a[1]))
    # b = (a[0]+d,a[1]+d)
    BB = self.GetTile(AA,a[0],a[1],b[0],b[1])
    LL = self.GetTile(LL,a[0],a[1],b[0],b[1])
    self.qTCGAMod.SetSourceVol(BB)
    self.qTCGAMod.SetSeedVol(LL)
    self.qTCGAMod.Run_NucleiSegYi()
    self.qTCGASegArray[:] = seedArray[:]
    self.MergeImages(LL,self.labelNode.GetImageData(),a[0],a[1])
    self.foregroundNode.GetImageData().Modified()
    self.foregroundNode.Modified()
    self.labelNode.GetImageData().Modified()
    self.labelNode.Modified()
    self.currentMessage = "Quick TCGA : nuclei segmentation is done"
    slicer.util.showStatusMessage(self.currentMessage)

  def GetTile(self,image,x1,y1,x2,y2):
    i = vtk.vtkImageData().NewInstance()
    i.SetDimensions(x2-x1+1,y2-y1+1,1)
    i.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,image.GetNumberOfScalarComponents())
    for x in range(x1,x2+1):
      for y in range(y1,y2+1):
        for c in range(0,image.GetNumberOfScalarComponents()):
          i.SetScalarComponentFromDouble(x-x1,y-y1,0,c,image.GetScalarComponentAsDouble(x,y,0,c))
    return i

  def MergeImages(self, image1, image2, a, b):
    dim = image1.GetDimensions()
    for x in range(a,a+dim[0]):
      for y in range(b,b+dim[1]):
        for c in range(0,image1.GetNumberOfScalarComponents()):
          image2.SetScalarComponentFromDouble(x,y,0,c,image1.GetScalarComponentAsDouble(x-a,y-b,0,c))
    image2.Modified()

  def destroy(self):
    #destroy GrowCut key shortcuts
    for i in range(len(self.qtkeydefsQTCGA)):  #this will be an empty list if the KSlice part has been reached (all growcut functionality disabled)
        keyfun = self.qtkeydefsQTCGA[i]
        keydef = self.qtkeyconnections[i]
        test1=keydef.disconnect('activated()', keyfun[1])
        test2=keydef.disconnect('activatedAmbiguously()', keyfun[1])
        #self.qtkeyconnections.remove(keydef) #remove from list
        keydef.setParent(None)
        #why is this necessary for full disconnect (if removed, get the error that more and more keypresses are required if module is repetedly erased and created
        keydef.delete() #this causes errors

    # destroy QuickTCGA objects
    self.qTCGASeedArray = None
    self.qTCGASegArray = None
    self.qTCGAMod = None
    self.currentMessage = ""
    self.imgName = None
    self.imgBgrdName = None
    self.imgFgrdName = None
    self.labelNode = None
    self.backgroundNode = None

    #put back the editor shortcuts we removed
    slicer.modules.SlicerPathologyWidget.editorWidget.installShortcutKeys()

    print("Deletion completed")


  def sliceViewMatchEditor(self, sliceLogic):
    imgNode = sliceLogic.GetBackgroundLayer().GetVolumeNode()
    labelNode = sliceLogic.GetLabelLayer().GetVolumeNode()

    if type(imgNode)==type(None) or type(labelNode)==type(None) :
        self.dialogBox.setText("Either image (must be Background Image) or label not set in slice views.")
        self.dialogBox.show()
        if self.emergencyStopFunc:
            self.emergencyStopFunc()
        return False

    dimImg=self.backgroundNode.GetImageData().GetDimensions()
    dimLab=self.labelNode.GetImageData().GetDimensions()

    if not (dimImg[0]==dimLab[0] and dimImg[1]==dimLab[1] and dimImg[2]==dimLab[2]): #if sizes dont match up(doing this b/c cant reach HelperBox parameters
        self.dialogBox.setText("Mismatched label to image.")
        self.dialogBox.show()
        if self.emergencyStopFunc:
            self.emergencyStopFunc()
        return False

    if (self.imgBgrdName== imgNode.GetName()) and (self.labelName == labelNode.GetName()):
        return True
    else:
        self.dialogBox.setText("Set image to values used for starting the FastGrowCut bot or stop bot.")
        self.dialogBox.show()
        if self.emergencyStopFunc:
            self.emergencyStopFunc()
        return False

  def QTCGAChangeLabelInput(self, caller, event):

    if self.sliceViewMatchEditor(self.sliceLogic)==False:
       return #do nothing, exit function

  def entranceCursorDetect(self, caller, event):
    ijkPlane = self.sliceIJKPlane()
    self.ijkPlane = ijkPlane
    self.computeCurrSliceSmarter()

  def updateShortCutROI(self, caller, event):
    if event == "LeftButtonPressEvent":
      if self.bEditShortCut == True:
        xy = self.interactor.GetEventPosition()
        ijk = smart_xyToIJK(xy,self.sw)
        if ijk[0] > self.SCutROIRad and ijk[0] < self.volSize[0] - self.SCutROIRad and ijk[1] > self.SCutROIRad and ijk[1] < self.volSize[1] - self.SCutROIRad:
          self.qSCutROIArray[:] = 0
          self.qSCutROIArray[0,ijk[1]-self.SCutROIRad:ijk[1]+self.SCutROIRad, ijk[0]-self.SCutROIRad:ijk[0]+self.SCutROIRad] = 2

          # Update ROI
          roiArray = slicer.util.array(self.labelNode.GetName())
          roiArray[:] = self.qSCutROIArray[:]
          self.labelNode.GetImageData().Modified()
          self.labelNode.Modified()
      else:
        print ("Press key F to enable editing ShortCut region")
    else:
      pass

#
# The QuickTCGAEffect class definition
#

class QuickTCGAEffectExtension(LabelEffect.LabelEffect):
  """Organizes the Options, Tool, and Logic classes into a single instance
  that can be managed by the EditBox
  """

  def __init__(self):
    # name is used to define the name of the icon image resource (e.g. QuickTCGAEffect.png)
    self.name = "QuickTCGAEffect"
    # tool tip is displayed on mouse hover
    self.toolTip = "Paint: circular paint brush for label map editing"

    self.options = QuickTCGAEffectOptions
    self.tool = QuickTCGAEffectTool
    self.logic = QuickTCGAEffectLogic

""" Test:

sw = slicer.app.layoutManager().sliceWidget('Red')
import EditorLib
pet = EditorLib.QuickTCGAEffectTool(sw)

"""

#
# QuickTCGAEffect
#

class QuickTCGAEffect:
  """
  This class is the 'hook' for slicer to detect and recognize the extension
  as a loadable scripted module
  """
  def __init__(self, parent):
    parent.dependencies = ["Editor"]
    parent.title = "Editor QuickTCGAEffect Effect"
    parent.categories = ["Developer Tools.Editor Extensions"]
    parent.contributors = ["Liangjia Zhu, Erich Bremer, Joel Saltz, Allen Tannenbaum (Stony Brook University)"] # insert your name in the list
    parent.helpText = """Interactive TCGA editor extension."""
    parent.acknowledgementText = """ This editor extension was developed by Liangjia Zhu, Erich Bremer, Joel Saltz, Allen Tannenbaum  (Stony Brook University) """

    try:
      slicer.modules.editorExtensions
    except AttributeError:
      slicer.modules.editorExtensions = {}
    slicer.modules.editorExtensions['QuickTCGAEffect'] = QuickTCGAEffectExtension

#
# QuickTCGAEffectWidget
#

class QuickTCGAEffectWidget:
  def __init__(self, parent = None):
    self.parent = parent

  def setup(self):
    # don't display anything for this widget - it will be hidden anyway
    pass

  def enter(self):
    pass

  def exit(self):
    pass

def get_view_names( sw ):
    viewName = sw.sliceLogic().GetSliceNode().GetName()
    lm = slicer.app.layoutManager()
    orient = lm.sliceWidget(viewName).sliceOrientation;
    valid_orient= ('Axial','Sagittal','Coronal','Reformat')
    viewOrient = None
    for vo in valid_orient:
      if vo == orient:
        viewOrient = vo
    return viewName,viewOrient


def smart_xyToIJK(xy,sliceWidget):
  xyz = sliceWidget.sliceView().convertDeviceToXYZ(xy);
  ll = sliceWidget.sliceLogic().GetLabelLayer()
  #~ xyToIJK = ll.GetXYToIJKTransform().GetMatrix()
  #~ ijkFloat = xyToIJK.MultiplyPoint(xyz+(1,))[:3]
  xyToIJK = ll.GetXYToIJKTransform()
  ijkFloat = xyToIJK.TransformDoublePoint(xyz)
  ijk = []
  for element in ijkFloat:
    try:
      index = int(round(element))
    except ValueError:
      index = 0
    ijk.append(index)
    #Print_Coord_Debug(xyz, RAS, xy, ijk, sliceWidget)
  return ijk


def get_values_at_IJK( ijk, sliceWidget):
  labelLogic = sliceWidget.sliceLogic().GetLabelLayer()
  volumeNode = labelLogic.GetVolumeNode()
  imageData = volumeNode.GetImageData()
  if not imageData:
    return "No Label Image"
  dims = imageData.GetDimensions()
  #print "current view dims = " + str(dims)
  wasOutOfFrame = False
  values = {'label':None,'U':None}
  for ele in xrange(3):
    ijk
    if ijk[ele] < 0 or ijk[ele] >= dims[ele]:
      #print "Out of Frame"
      wasOutOfFrame=True
  if not wasOutOfFrame and volumeNode.GetLabelMap():
    labelIndex = int(imageData.GetScalarComponentAsDouble(ijk[0], ijk[1], ijk[2], 0))
    #print "labelIndex = " + str(labelIndex)
    values['label'] = labelIndex
  # TODO get the user-integral value too
  return values


def bind_view_observers( handlerFunc ):
  layoutManager = slicer.app.layoutManager()
  sliceNodeCount = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceNode')
  ObserverTags = []
  SliceWidgetLUT = {} # for sw = SliceWidget[caller] in handlerFunc
  for nodeIndex in xrange(sliceNodeCount):
    sliceNode = slicer.mrmlScene.GetNthNodeByClass(nodeIndex, 'vtkMRMLSliceNode')
    sliceWidget = layoutManager.sliceWidget(sliceNode.GetLayoutName())
    #print "did a bind_view_observers for view: " + str(sliceNode.GetLayoutName())
    if sliceWidget: # add obserservers and keep track of tags
      style = sliceWidget.sliceView().interactor()
      SliceWidgetLUT[style] = sliceWidget
      events = ("LeftButtonPressEvent","MouseMoveEvent", "RightButtonPressEvent","EnterEvent", "LeaveEvent")
      for event in events: # override active effect w/ priority
        tag = style.AddObserver(event, handlerFunc, 2.0)
        ObserverTags.append([style,tag])
  return ObserverTags,SliceWidgetLUT
