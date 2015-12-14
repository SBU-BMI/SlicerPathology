import os
import unittest
from __main__ import vtk, qt, ctk, slicer
#from slicer.ScriptedLoadableModule import *

#
# LoadTCGA
#

#class LoadTCGA(ScriptedLoadableModule):
class LoadTCGA:
  def __init__(self, parent):
    #ScriptedLoadableModule.__init__(self, parent)
    parent.title = "LoadTCGA" # TODO make this more human readable by adding spaces
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["Liangjia Zhu, Yi Gao"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = """
""" # replace with organization, grant and thanks.

#
# qLoadTCGAWidget
#

#class LoadTCGAWidget(ScriptedLoadableModuleWidget):
class LoadTCGAWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()
      
  def setup(self):
    #ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    
    loadDataButton = qt.QPushButton("Load Data")
    parametersFormLayout.addWidget(loadDataButton)
    loadDataButton.connect('clicked()', self.loadTCGAData)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = LoadTCGALogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    screenshotScaleFactor = int(self.screenshotScaleFactorSliderWidget.value)
    print("Run the algorithm")
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), enableScreenshotsFlag,screenshotScaleFactor)

  def loadTCGAData(self):
	  slicer.util.openAddVolumeDialog()
	  
	  red_logic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
	  red_cn = red_logic.GetSliceCompositeNode()
	  fgrdVolID = red_cn.GetBackgroundVolumeID()
	  fgrdNode = slicer.util.getNode(fgrdVolID)
	  fMat=vtk.vtkMatrix4x4()
	  fgrdNode.GetIJKToRASDirectionMatrix(fMat)
	  bgrdName = fgrdNode.GetName() + '_gray'
	  
	  # Get dummy grayscale image
	  magnitude = vtk.vtkImageMagnitude()
	  magnitude.SetInputData(fgrdNode.GetImageData())
	  magnitude.Update()
	  
	  bgrdNode = slicer.vtkMRMLScalarVolumeNode()
	  bgrdNode.SetImageDataConnection(magnitude.GetOutputPort())
	  bgrdNode.SetName(bgrdName)
	  bgrdNode.SetIJKToRASDirectionMatrix(fMat)
	  slicer.mrmlScene.AddNode(bgrdNode)
	  bgrdVolID = bgrdNode.GetID()
	  
	  # Reset slice configuration
	  red_cn.SetForegroundVolumeID(fgrdVolID)
	  red_cn.SetBackgroundVolumeID(bgrdVolID)
	  red_cn.SetForegroundOpacity(1) 
	  
	  # Start Editor
	  m = slicer.util.mainWindow()
	  m.moduleSelector().selectModule('Editor')
	  
	  print("Load...")
	  

#
# LoadTCGALogic
#

#class LoadTCGALogic(ScriptedLoadableModuleLogic):
class LoadTCGALogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    self.delayDisplay(description)

    if self.enableScreenshots == 0:
      return

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == -1:
      # full window
      widget = slicer.util.mainWindow()
    elif type == slicer.qMRMLScreenShotDialog().FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog().ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog().Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog().Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog().Green:
      # green slice window
      widget = lm.sliceWidget("Green")

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, self.screenshotScaleFactor, imageData)

  def run(self,inputVolume,outputVolume,enableScreenshots=0,screenshotScaleFactor=1):
    """
    Run the actual algorithm
    """

    self.delayDisplay('Running the aglorithm')

    self.enableScreenshots = enableScreenshots
    self.screenshotScaleFactor = screenshotScaleFactor

    self.takeScreenshot('LoadTCGA-Start','Start',-1)

    return True


#class LoadTCGATest(ScriptedLoadableModuleTest):
class LoadTCGATest:
  """
  This is the test case for your scripted module.
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_LoadTCGA1()

  def test_LoadTCGA1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        print('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        print('Loading %s...\n' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading\n')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = LoadTCGALogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
