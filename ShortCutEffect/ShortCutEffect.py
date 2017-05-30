import os
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
from vtk.util import numpy_support
from vtk.util.numpy_support import vtk_to_numpy

#
# The Editor Extension itself.
#
# This needs to define the hooks to be come an editor effect.
#

#
# ShortCutOptions - see LabelEffect, EditOptions and Effect for superclasses
#

class ShortCutOptions(EditorLib.LabelEffectOptions):
  """ ShortCut-specfic gui
  """

  def __init__(self, parent=0):
    super(ShortCutOptions,self).__init__(parent)

    editUtil = EditorLib.EditUtil.EditUtil()
    parameterNode = editUtil.getParameterNode()
    lm = slicer.app.layoutManager()
    self.redSliceWidget = lm.sliceWidget('Red')
    self.yellowSliceWidget = lm.sliceWidget('Yellow')
    self.greenSliceWidget = lm.sliceWidget('Green')
    self.parameterNode=parameterNode
    
    self.attributes = ('MouseTool')
    self.displayName = 'ShortCut Effect'

  def __del__(self):
    super(ShortCutOptions,self).__del__()

  def create(self):
    super(ShortCutOptions,self).create()
    self.helpLabel = qt.QLabel("Run the Quick TCGA Segmenter on the current label/seed image.", self.frame)
    self.frame.layout().addWidget(self.helpLabel)
    
    #create a "Start Bot" button
    self.botButton = qt.QPushButton(self.frame)

    self.frame.layout().addWidget(self.botButton)
    self.botButton.connect('clicked()', self.onStartBot)

    self.locRadFrame = qt.QFrame(self.frame)
    self.locRadFrame.setLayout(qt.QHBoxLayout())
    self.frame.layout().addWidget(self.locRadFrame)
    self.widgets.append(self.locRadFrame)
    

    
    # Nucleus segmentation parameters (Yi Gao's algorithm)
    #nucleusSegCollapsibleButton = ctk.ctkCollapsibleButton()
    #nucleusSegCollapsibleButton.text = "Nucleus Segmentation Parameters (Yi Gao)"
    #nucleusSegCollapsibleButton.collapsed = True;
    #self.frame.layout().addWidget(nucleusSegCollapsibleButton)
    
    # Layout within the parameter button
    #nucleusSegFormLayout = qt.QFormLayout(nucleusSegCollapsibleButton)
    #frameOtsuSlider = ctk.ctkSliderWidget()
    #frameOtsuSlider.connect('valueChanged(double)', self.OtsuSliderValueChanged)
    #frameOtsuSlider.decimals = 0
    #frameOtsuSlider.minimum = 0
    #frameOtsuSlider.maximum = 10
    #frameOtsuSlider.value = 1.0
    #nucleusSegFormLayout.addRow("Otsu Threshold:", frameOtsuSlider)
    
    #frameCurvatureWeightSlider = ctk.ctkSliderWidget()
    #frameCurvatureWeightSlider.connect('valueChanged(double)', self.CurvatureWeightSliderValueChanged)
    #frameCurvatureWeightSlider.decimals = 0
    #frameCurvatureWeightSlider.minimum = 0
    #frameCurvatureWeightSlider.maximum = 10
    #frameCurvatureWeightSlider.value = 8
    #nucleusSegFormLayout.addRow("Curvature Weight:", frameCurvatureWeightSlider)
    
    #frameSizeThldSlider = ctk.ctkSliderWidget()
    #frameSizeThldSlider.connect('valueChanged(double)', self.SizeThldSliderValueChanged)
    #frameSizeThldSlider.decimals = 0
    #frameSizeThldSlider.minimum = 1
    #frameSizeThldSlider.maximum = 100
    #frameSizeThldSlider.value = 3
    #nucleusSegFormLayout.addRow("Size Threshold:", frameSizeThldSlider)
    
    #frameSizeUpperThldSlider = ctk.ctkSliderWidget()
    #frameSizeUpperThldSlider.connect('valueChanged(double)', self.SizeUpperThldSliderValueChanged)
    #frameSizeUpperThldSlider.decimals = 0
    #frameSizeUpperThldSlider.minimum = 100
    #frameSizeUpperThldSlider.maximum = 500
    #frameSizeUpperThldSlider.value = 300
    #nucleusSegFormLayout.addRow("Size Upper Threshold:", frameSizeUpperThldSlider)
    
    #frameMPPSlider = ctk.ctkSliderWidget()
    #frameMPPSlider.connect('valueChanged(double)', self.MPPSliderValueChanged)
    #frameMPPSlider.decimals = 0
    #frameMPPSlider.minimum = 0
    #frameMPPSlider.maximum = 100
    #frameMPPSlider.value = 25
    #nucleusSegFormLayout.addRow("Size Upper Threshold:", frameMPPSlider)

    HelpButton(self.frame, ("TO USE: \n Start the ShortCutCore segmenter and initialize the segmentation with any other editor tool like PaintEffect. Press the following keys to interact:" +
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

  def destroy(self):
    self.currentMessage = ""
    slicer.util.showStatusMessage(self.currentMessage)
    super(ShortCutOptions,self).destroy()
    
  #def OtsuSliderValueChanged(self,value):
  #  self.parameterNode.SetParameter("ShortCut,otsuRatio", str(value))
  #  self.updateMRMLFromGUI()
  
  #def CurvatureWeightSliderValueChanged(self,value):
  #  self.parameterNode.SetParameter("ShortCut,curvatureWeight", str(value))
  #  self.updateMRMLFromGUI()  
    
  #def SizeThldSliderValueChanged(self,value):
  #  self.parameterNode.SetParameter("ShortCut,sizeThld", str(value))
  #  self.updateMRMLFromGUI()  
    
  #def SizeUpperThldSliderValueChanged(self,value):
  #  self.parameterNode.SetParameter("ShortCut,sizeUpperThld", str(value))
  #  self.updateMRMLFromGUI()  
    
  #def MPPSliderValueChanged(self,value):
  #  self.parameterNode.SetParameter("ShortCut,mpp", str(value))
  #  self.updateMRMLFromGUI()  
 
  #def onRadiusSpinBoxChanged(self,value):
  #  self.parameterNode.SetParameter("ShortCut,radius", str(value))
  #  self.updateMRMLFromGUI()

  # note: this method needs to be implemented exactly as-is
  # in each leaf subclass so that "self" in the observer
  # is of the correct type
  #def updateParameterNode(self, caller, event):
  #  node = EditUtil.EditUtil().getParameterNode()
  #  if node != self.parameterNode:
  #    if self.parameterNode:
  #      node.RemoveObserver(self.parameterNodeTag)
  #    self.parameterNode = node
  #    self.parameterNodeTag = node.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updateGUIFromMRML)

  def setMRMLDefaults(self):
    super(ShortCutOptions,self).setMRMLDefaults()

  def onStartBot(self):

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
      slicer.modules.TCGAEditorBot.logic.emergencyStopFunc = self.botEstop; #save the function that stops bot, destroys FastGrowCut segmenter, if things go wrong
      if self.botButton:
        self.botButton.text = "Stop Quick TCGA Segmenter"  
        self.currentMessage =  "Quick TCGA Segmenter started: Press 'Y' to start automatic nucleus segmentation; Or go to PaintEffect to edit label image or press 'S' to start global segmentation process."
        slicer.util.showStatusMessage(self.currentMessage)        
        
      if self.locRadFrame:
        self.locRadFrame.hide()

  def updateGUIFromMRML(self,caller,event):
    self.disconnectWidgets()
    super(ShortCutOptions,self).updateGUIFromMRML(caller,event)
    self.connectWidgets()

  def updateMRMLFromGUI(self):
    if self.updatingGUI:
      return
    disableState = self.parameterNode.GetDisableModifiedEvent()
    self.parameterNode.SetDisableModifiedEvent(1)
    super(ShortCutOptions,self).updateMRMLFromGUI()
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
    self.logic = ShortCutLogic( self.redSliceWidget.sliceLogic() )

  def stop(self):

    self.logic.destroy()
#
# ShortCutTool
#

class ShortCutTool(LabelEffect.LabelEffectTool):
  """
  One instance of this will be created per-view when the effect
  is selected.  It is responsible for implementing feedback and
  label map changes in response to user input.
  This class observes the editor parameter node to configure itself
  and queries the current view for background and label volume
  nodes to operate on.
  """

  def __init__(self, sliceWidget):
    super(ShortCutTool,self).__init__(sliceWidget)
    # create a logic instance to do the non-gui work
    #self.logic = ShortCutLogic(self.sliceWidget.sliceLogic())

  def cleanup(self):
    super(ShortCutTool,self).cleanup()

  #def processEvent(self, caller=None, event=None):
   # """
   # handle events from the render window interactor
   # """

   # # let the superclass deal with the event if it wants to
   # if super(ShortCutTool,self).processEvent(caller,event):
   #   return

   # # events from the slice node
  #  if caller and caller.IsA('vtkMRMLSliceNode'):
  #    # here you can respond to pan/zoom or other changes
   #   # to the view
   #   pass
  def processEvent(self, caller=None, event=None):
    """
handle events from the render window interactor
"""
    if event == "LeftButtonPressEvent":
      xy = self.interactor.GetEventPosition()
      viewName,orient = get_view_names(self.sliceWidget)
      ijk= smart_xyToIJK(xy,self.sliceWidget)
      if not orient:
        print "Warning, unexpected view orientation!?"
    if event == 'EnterEvent':
      pass #print "EnterEvent in KSliceEffect."
    else:
      pass

#
# ShortCutLogic
#

class ShortCutLogic(LabelEffect.LabelEffectLogic):
  """
  This class contains helper methods for a given effect
  type.  It can be instanced as needed by an ShortCutTool
  or ShortCutOptions instance in order to compute intermediate
  results (say, for user feedback) or to implement the final
  segmentation editing operation.  This class is split
  from the ShortCutTool so that the operations can be used
  by other code without the need for a view context.
  """

  def __init__(self,sliceLogic):
    print("Preparing Quick TCGA Interaction")
    self.attributes = ('MouseTool')
    self.displayName = 'ShortCutCore Effect'

    # disconnect all shortcuts that may exist, to allow ShortCutCore's to work, reconnect once bot is turned off
    if hasattr(slicer.modules, 'EditorWidget'):
      slicer.modules.EditorWidget.removeShortcutKeys()
    self.sliceLogic = sliceLogic
    self.editUtil = EditUtil.EditUtil()
    self.swRed = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
    self.sw = slicer.app.layoutManager().sliceWidget('Red')
    self.interactor = self.sw.sliceView().interactor() #initialize to red slice interactor
    #self.computeCurrSliceSmarter() #initialize the current slice to something meaningful

    self.mouse_obs_growcut, self.swLUT_growcut = bind_view_observers(self.updateShortCutROI)

    #initialize Fast GrowCut
    self.init_ShortCutCore()
    
    self.ShortCutCoreCreated=False
  
  def init_ShortCutCore(self):
	
	self.emergencyStopFunc = None    
	self.dialogBox=qt.QMessageBox() #will display messages to draw users attention if he does anything wrong
	self.dialogBox.setWindowTitle("ShortCutCore Error")
	self.dialogBox.setWindowModality(qt.Qt.NonModal) #will allow user to continue interacting with Slicer
    
    # TODO: check this claim- might be causing leaks
    # set the image, label nodes (this will not change although the user can
    # alter what is bgrnd/frgrnd in editor)
    # Confused about how info propagates UIarray to UIVol, not the other way, NEEDS AUTO TESTS
    
	self.labelNode = self.editUtil.getLabelVolume() #labelLogic.GetVolumeNode()
	self.backgroundNode = self.editUtil.getBackgroundVolume() #backgroundLogic.GetVolumeNode()
	self.foregroundNode = self.swRed.GetForegroundLayer().GetVolumeNode()
	#self.labelNode = self.swRed.GetLabelLayer().GetVolumeNode()
    
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
         
    # ShortCutCore shortcuts
	resetQTCGAKey = qt.QKeySequence(qt.Qt.Key_R) # reset initialization flag
	runQTCGAClusterKey = qt.QKeySequence(qt.Qt.Key_S) # run fast growcut
	#runNucleiSegKey = qt.QKeySequence(qt.Qt.Key_Y)
	editTCGAKey = qt.QKeySequence(qt.Qt.Key_E) # edit seed labels
	runQTCGATemplateKey = qt.QKeySequence(qt.Qt.Key_T)
	runQTCGARefineCurvatureKey = qt.QKeySequence(qt.Qt.Key_U)
	runQTCGAShortCutKey = qt.QKeySequence(qt.Qt.Key_C)
	runQTCGAShortEditCutKey = qt.QKeySequence(qt.Qt.Key_F)

	print " keys to run ShortCutCore segmentation, ShortCut, edit ShortCut, edit seed, reset parameters are S, C, F, E, R"
    
	self.qtkeyconnections = []
	self.qtkeydefsQTCGA = [[resetQTCGAKey, self.resetQTCGAFlag],
                             [runQTCGAClusterKey,self.runQTCGA_Segmentation],
                             [runQTCGATemplateKey, self.runQTCGA_Template],
                             [runQTCGARefineCurvatureKey, self.runQTCGA_Refine_Curvature],
                             [runQTCGAShortCutKey, self.runQTCGA_ShortCut],
                             [runQTCGAShortEditCutKey, self.editShortCut],
                             [editTCGAKey, self.editTCGA]]

	for keydef in self.qtkeydefsQTCGA:
		s = qt.QShortcut(keydef[0], slicer.util.mainWindow()) # connect this qt event to mainWindow focus
        #s.setContext(1)
		s.connect('activated()', keydef[1])
        #s.connect('activatedAmbiguously()', keydef[1])
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
	#roiVTK.UpdateInformation()
    
  
	import vtkSlicerShortCutCoreModuleLogicPython
	
	node = EditUtil.EditUtil().getParameterNode() # get the parameters from MRML
	otsuRatio = 1.0
	if node.GetParameter("ShortCut,otsuRatio") is not '':
	  otsuRatio = float(node.GetParameter("ShortCut,otsuRatio"))
	print(otsuRatio)

	curvatureWeight = 0.8
	if node.GetParameter("ShortCut,curvatureWeight") is not '':
	  curvatureWeight = float(node.GetParameter("ShortCut,curvatureWeight"))/10
	print(curvatureWeight)

	sizeThld = 3.0
	if node.GetParameter("ShortCut,sizeThld") is not '':
	  sizeThld = float(node.GetParameter("ShortCut,sizeThld"))
	print(sizeThld)

	sizeUpperThld = 200.0
	if node.GetParameter("ShortCut,sizeUpperThld") is not '':
	  sizeUpperThld = float(node.GetParameter("ShortCut,sizeUpperThld"))
	print(sizeUpperThld)

	mpp = 0.25
	if node.GetParameter("ShortCut,mpp") is not '':
	  mpp = float(node.GetParameter("ShortCut,mpp"))/100
	print(mpp)

	qTCGAMod = vtkSlicerShortCutCoreModuleLogicPython.vtkShortCutCore()
	qTCGAMod.SetSourceVol(self.foregroundNode.GetImageData())
	qTCGAMod.SetotsuRatio(otsuRatio)
	qTCGAMod.SetcurvatureWeight(curvatureWeight)
	qTCGAMod.SetsizeThld(sizeThld)
	qTCGAMod.SetsizeUpperThld(sizeUpperThld)
	qTCGAMod.Setmpp(mpp)
	
	#qTCGAMod.SetSeedVol(self.labelNode.GetImageData())r
	qTCGAMod.Initialization()
	self.qTCGAMod = qTCGAMod   
	self.ShortCutCoreCreated=True #tracks if completed the initializtion (so can do stop correctly) of KSlice

 

  # run Quick TCGA segmenter for the current master volume and label volume
  
  def runQTCGA_Segmentation(self):
	if self.bEditTCGA == True:

		self.currentMessage = "Quick TCGA: running classification ..."
		slicer.util.showStatusMessage(self.currentMessage)
		seedArray = slicer.util.array(self.labelNode.GetName())
		self.qTCGASeedArray[:]  = seedArray[:]
		
		self.qTCGAMod.SetSourceVol(self.foregroundNode.GetImageData())
		self.qTCGAMod.SetSeedVol(self.labelNode.GetImageData())
		self.qTCGAMod.Run_QTCGA_Segmentation()
		self.qTCGASegArray[:] = seedArray[:]
		
		self.labelNode.GetImageData().Modified()
		self.labelNode.Modified()
			
		self.bEditTCGA = False
		
		self.currentMessage = "Quick TCGA done: press 'E' to add more prior information, or 'R' to reset Quick TCGA parameters; or press 'F' to enable ROI selection for refinement"
		slicer.util.showStatusMessage(self.currentMessage)
	else:
		self.currentMessage = "Quick TCGA: go to seed labels first by pressing 'E'"
		slicer.util.showStatusMessage(self.currentMessage)
		
	#if self.bEditTCGA == True:

#		self.currentMessage = "Quick TCGA: running nucleus segmentation ..."
#		slicer.util.showStatusMessage(self.currentMessage)
#		seedArray = slicer.util.array(self.labelNode.GetName())
#		self.qTCGASeedArray[:]  = seedArray[:]
#		
#		node = EditUtil.EditUtil().getParameterNode() # get the parameters from MRML
#		otsuRatio = float(node.GetParameter("ShortCut,otsuRatio"))
#		print(otsuRatio)
#		curvatureWeight = float(node.GetParameter("ShortCut,curvatureWeight"))/10
#		print(curvatureWeight)
#		sizeThld = float(node.GetParameter("ShortCut,sizeThld"))
#		print(sizeThld)
#		sizeUpperThld = float(node.GetParameter("ShortCut,sizeUpperThld"))
#		print(sizeUpperThld)
#		mpp = float(node.GetParameter("ShortCut,mpp"))/100
#		print(mpp)

#		self.qTCGAMod.SetotsuRatio(otsuRatio)
#		self.qTCGAMod.SetcurvatureWeight(curvatureWeight)
#		self.qTCGAMod.SetsizeThld(sizeThld)
#		self.qTCGAMod.SetsizeUpperThld(sizeUpperThld)
#		self.qTCGAMod.Setmpp(mpp)
#		
#		self.qTCGAMod.SetSourceVol(self.foregroundNode.GetImageData())
#		self.qTCGAMod.SetSeedVol(self.labelNode.GetImageData())
#		self.qTCGASegArray[:] = seedArray[:]
#		
#		self.labelNode.GetImageData().Modified()
#		self.labelNode.Modified()
#			
		#self.bEditTCGA = False
#		
#		self.currentMessage = "Quick TCGA done: nuclei segmetnation is done; press 'F' to enable ROI selection for refinement"
#		slicer.util.showStatusMessage(self.currentMessage)
#	#else:
#	#	self.currentMessage = "Quick TCGA: go to seed labels first by pressing 'E'"
#	#	slicer.util.showStatusMessage(self.currentMessage)

  def runQTCGA_Template(self):
	# return
	if self.bEditTCGA == True:
	
		self.currentMessage = "Quick TCGA: running template matching ..."
		slicer.util.showStatusMessage(self.currentMessage)
		seedArray = slicer.util.array(self.labelNode.GetName())
		self.qTCGASeedArray[:]  = seedArray[:]
		
		self.qTCGAMod.SetSourceVol(self.foregroundNode.GetImageData())
		self.qTCGAMod.SetSeedVol(self.labelNode.GetImageData())
		#self.qTCGAMod.SetInitializationFlag(bGCInitialized)
		self.qTCGAMod.Run_QTCGA_Template()
		self.qTCGASegArray[:] = seedArray[:]
		
		self.labelNode.GetImageData().Modified()
		self.labelNode.Modified()
			
		self.bEditTCGA = False
		
		self.currentMessage = "Quick TCGA done: press 'E' to add more prior information or 'R' to reset Quick TCGA parameters; or press 'F' to enable ROI selection for refinement "
		slicer.util.showStatusMessage(self.currentMessage)
	else:
		self.currentMessage = "Quick TCGA: go to seed labels first by pressing 'E'"
		slicer.util.showStatusMessage(self.currentMessage)

  def runQTCGA_ShortCut(self):
	if self.bEditShortCut == True:

		self.currentMessage = "Quick TCGA: running ShortCut ..."
		slicer.util.showStatusMessage(self.currentMessage)
		seedArray = slicer.util.array(self.labelNode.GetName())
		
		seedArray[:] = self.qTCGASegArray[:]
		
		self.qTCGAMod.SetSourceVol(self.foregroundNode.GetImageData())
		self.qTCGAMod.SetSeedVol(self.labelNode.GetImageData())
		
		roiArray = vtk_to_numpy(self.roiVTK.GetPointData().GetScalars())
		roiArray = roiArray.reshape(1, self.volSize[0], self.volSize[1])
		roiArray[:] = self.qSCutROIArray[:]
		self.qTCGAMod.SetSCROIVol(self.roiVTK)
		
		self.qTCGAMod.Run_QTCGA_ShortCut()	
		self.qTCGASegArray[:] = seedArray[:]
		
		self.labelNode.GetImageData().Modified()
		self.labelNode.Modified()
		
		
			
		self.bEditShortCut = False
		
		self.currentMessage = "Quick TCGA done: press 'F' to enable ROI selection and left click to select ROI and press 'C' to start refinement; Or press 'E' to add more seed information, or 'R' to reset Quick TCGA parameters"
		slicer.util.showStatusMessage(self.currentMessage)
	else:
		self.currentMessage = "Quick TCGA: go to ROI first by pressing 'F'"
		slicer.util.showStatusMessage(self.currentMessage)
		
  def runQTCGA_Refine_Curvature(self):
	# return

	self.currentMessage = "Quick TCGA: running refinement ..."
	slicer.util.showStatusMessage(self.currentMessage)
	
	self.qTCGAMod.SetSourceVol(self.foregroundNode.GetImageData())
	self.qTCGAMod.SetSeedVol(self.labelNode.GetImageData())
	self.qTCGAMod.Run_Refine_Curvature()
	
	self.labelNode.GetImageData().Modified()
	self.labelNode.Modified()
			
		
	self.currentMessage = "Quick TCGA done: press 'U' to keep refining segmentation, or 'R' to reset Quick TCGA parameters"
	slicer.util.showStatusMessage(self.currentMessage)
	#else:
	#	self.currentMessage = "Quick TCGA: go to seed labels first by pressing 'E'"
	#	slicer.util.showStatusMessage(self.currentMessage)
	#	

  
  # reset Quick TCGA
  def resetQTCGAFlag(self):
        self.bEditTCGA = True
        self.bEditShortCut = False;
        self.qTCGASeedArray[:] = 0
        self.qTCGASegArray[:] = 0
        
        seedArray = slicer.util.array(self.labelNode.GetName())
        seedArray[:] = 0
        
        self.labelNode.GetImageData().Modified()
        self.labelNode.Modified()
        print('reset Quick TCGA parameters')
        self.currentMessage = "Quick TCGA: parameters have been reset. Press 'Y' to do automatic nucleus segmentation, Or go to PaintEffect to initialize labels and press 'S' to start global segmentation"
        slicer.util.showStatusMessage(self.currentMessage)
        
        
  def editTCGA(self):
	
    seedArray = slicer.util.array(self.labelNode.GetName())
    if self.bEditTCGA == False:
        self.qTCGASegArray[:] = seedArray[:]
        seedArray[:] = self.qTCGASeedArray[:]
        self.bEditTCGA = True
        self.labelNode.GetImageData().Modified()
        self.labelNode.Modified()
		
        print('show seed image')
        self.currentMessage = "Quick TCGA: seed image is shown. Press 'E' to segmentation result; Or go to PaintEffect to refine labels if necessary,and press 'S' to start global segmentation"
        slicer.util.showStatusMessage(self.currentMessage)
    else:
        if self.qTCGASegArray.any() != 0 :
		
			seedArray[:] = self.qTCGASegArray[:]
			self.bEditTCGA = False
			self.labelNode.GetImageData().Modified()
			self.labelNode.Modified()
			
			print('show segmentation')
			self.currentMessage = "Quick TCGA: segmentation result is shown. If not satisfied, press 'E' to edit seeds and run Quick TCGA again"
			slicer.util.showStatusMessage(self.currentMessage)
        else:
			print('no segmentation result')	
			self.currentMessage = "Quick TCGA:: no segmentation result available"
			slicer.util.showStatusMessage(self.currentMessage)
			
  def editShortCut(self):
	
    seedArray = slicer.util.array(self.labelNode.GetName())
    
    if self.bEditShortCut == False:
        seedArray[:] = self.qSCutROIArray[:]
        self.bEditShortCut = True
        self.labelNode.GetImageData().Modified()
        self.labelNode.Modified()
		
        print('show seed image')
        self.currentMessage = "Quick TCGA: ROI image is shown. Press 'F' to check segmentation result or left click the mouse to reselect the ROI, then press 'C' to start ShortCut for refinement"
        slicer.util.showStatusMessage(self.currentMessage)
    else:
        if self.qTCGASegArray.any() != 0 :
		
			seedArray[:] = self.qTCGASegArray[:]
			self.bEditShortCut = False
			self.labelNode.GetImageData().Modified()
			self.labelNode.Modified()
			
			print('show segmentation')
			self.currentMessage = "Quick TCGA: segmentation result is shown. If not satisfied, press 'F' to enable ROI selection and press 'C' to run ShortCut again"
			slicer.util.showStatusMessage(self.currentMessage)
        else:
			print('no segmentation result')	
			self.currentMessage = "Quick TCGA:: no segmentation result available"
			slicer.util.showStatusMessage(self.currentMessage)
			
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
    
    # destroy ShortCutCore objects
    self.qTCGASeedArray = None
    self.qTCGASegArray = None
    self.qTCGAMod = None
    self.currentMessage = ""
    self.imgName = None
    self.imgBgrdName = None
    self.imgFgrdName = None
    self.labelNode = None
    self.backgroundNode = None
    
    # remove GrowCut observer
    self.sliceLogic.RemoveObserver(self.qTCGALabMod_tag)

    # put back the editor shortcuts we removed
    if hasattr(slicer.modules, 'EditorWidget'):
      slicer.modules.EditorWidget.installShortcutKeys()

    print("Deletion completed")

   
  def sliceViewMatchEditor(self, sliceLogic):
    #if self.dialogBox==type(None): #something deleted teh dialogBox, this function then breaks, bail
    # if self.emergencyStopFunc:
    # self.emergencyStopFunc()
    # return False
    
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
    #~ dimImg=imgNode.GetImageData().GetDimensions()
    #~ dimLab=labelNode.GetImageData().GetDimensions()

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
    #interactor=caller # should be called by the slice interactor...
    #self.interactor=interactor
    #self.sw = self.swLUT_growcut[interactor]
    #self.sliceLogic = self.sw.sliceLogic() #this is a hack, look at init function, self.sliceLogic already defined as just "Red" slice
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
				#self.qSCutROIArray[np.ix_([ijk[0] - self.SCutROIRad, ijk[0] + self.SCutROIRad],[ijk[1] - self.SCutROIRad, ijk[1] + self.SCutROIRad],[0,1])] = 2
				self.qSCutROIArray[0,ijk[1]-self.SCutROIRad:ijk[1]+self.SCutROIRad, ijk[0]-self.SCutROIRad:ijk[0]+self.SCutROIRad] = 2
				#print ("EditROI")
				
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
# The ShortCut class definition
#

class ShortCutExtension(LabelEffect.LabelEffect):
  """Organizes the Options, Tool, and Logic classes into a single instance
  that can be managed by the EditBox
  """

  def __init__(self):
    # name is used to define the name of the icon image resource (e.g. ShortCut.png)
    self.name = "ShortCut"
    # tool tip is displayed on mouse hover
    self.toolTip = "Paint: circular paint brush for label map editing"

    self.options = ShortCutOptions
    self.tool = ShortCutTool
    self.logic = ShortCutLogic

""" Test:

sw = slicer.app.layoutManager().sliceWidget('Red')
import EditorLib
pet = EditorLib.ShortCutTool(sw)

"""

#
# ShortCut
#

class ShortCutEffect:
  """
  This class is the 'hook' for slicer to detect and recognize the extension
  as a loadable scripted module
  """
  def __init__(self, parent):
    parent.dependencies = ["Editor"]
    parent.title = "Editor ShortCut Effect"
    parent.categories = ["Developer Tools.Editor Extensions"]
    parent.contributors = ["Liangjia Zhu, Erich Bremer, Joel Saltz, Allen Tannenbaum (Stony Brook University)"] # insert your name in the list
    parent.helpText = """Interactive TCGA editor extension."""
    parent.acknowledgementText = """ This editor extension was developed by Liangjia Zhu, Erich Bremer, Joel Saltz, Allen Tannenbaum  (Stony Brook University) """


    # TODO:
    # don't show this module - it only appears in the Editor module
    #parent.hidden = True

    # Add this extension to the editor's list for discovery when the module
    # is created.  Since this module may be discovered before the Editor itself,
    # create the list if it doesn't already exist.
    try:
      slicer.modules.editorExtensions
    except AttributeError:
      slicer.modules.editorExtensions = {}
    slicer.modules.editorExtensions['ShortCutEffect'] = ShortCutExtension

#
# ShortCutWidget
#

class ShortCutWidget:
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
  #print( ijkFloat )
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

