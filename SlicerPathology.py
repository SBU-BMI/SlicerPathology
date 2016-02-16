import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Util.mixins import ModuleWidgetMixin
from Editor import EditorWidget
import PythonQt
import json
import EditorLib
from EditorLib import EditUtil

#
# SlicerPathology
#

class SlicerPathology(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "SlicerPathology" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Pathology"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    Put some useful help text in here at some point....
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# SlicerPathologyWidget
#

class SlicerPathologyWidget(ScriptedLoadableModuleWidget, ModuleWidgetMixin):

  def __init__(self, parent = None):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    self.resourcesPath = os.path.join(slicer.modules.slicerpathology.path.replace(self.moduleName+".py",""), 'Resources')
    self.modulePath = os.path.dirname(slicer.util.modulePath(self.moduleName))
    self.currentStep = 1
  
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    # this section is for custom color box
    infoGroupBox = qt.QWidget()
    hbox = qt.QHBoxLayout()
    hbox.setMargin(0)
    self.studySelectionGroupBoxLayout = qt.QGridLayout()
    infoGroupBox.setLayout(hbox)
    self.studySelectionGroupBoxLayout.addWidget(infoGroupBox, 0, 3, 1, 1)
    infoIcon = qt.QPixmap(os.path.join(self.resourcesPath, 'Icons', 'icon-infoBox.png'))
    self.customLUTInfoIcon = qt.QLabel()
    self.customLUTInfoIcon.setPixmap(infoIcon)
    self.customLUTInfoIcon.setSizePolicy(PythonQt.QtGui.QSizePolicy())
    hbox.addWidget(self.customLUTInfoIcon)
    self.customLUTLabel = qt.QLabel()
    hbox.addWidget(self.customLUTLabel)
    # end of custom color box section  
    self.setupIcons()
    self.setupTabBarNavigation()
    self.setupsetupUI()
    self.setupimageSelectionUI()
    self.setupsegmentationUI()
    self.setupsubmissionUI()
    self.setupEditorWidget()
    
    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    #self.inputSelector = slicer.qMRMLNodeComboBox()
    #self.inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    #self.inputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    #self.inputSelector.selectNodeUponCreation = True
    #self.inputSelector.addEnabled = False
    #self.inputSelector.removeEnabled = False
    #self.inputSelector.noneEnabled = False
    #self.inputSelector.showHidden = False
    #self.inputSelector.showChildNodeTypes = False
    #self.inputSelector.setMRMLScene( slicer.mrmlScene )
    #self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    #parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # output volume selector
    #
    #self.outputSelector = slicer.qMRMLNodeComboBox()
    #self.outputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    #self.outputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    #self.outputSelector.selectNodeUponCreation = False
    #self.outputSelector.addEnabled = True
    #self.outputSelector.removeEnabled = True
    #self.outputSelector.noneEnabled = False
    #self.outputSelector.showHidden = False
    #self.outputSelector.showChildNodeTypes = False
    #self.outputSelector.setMRMLScene( slicer.mrmlScene )
    #self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    #parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # scale factor for screen shots
    #
    self.screenshotScaleFactorSliderWidget = ctk.ctkSliderWidget()
    self.screenshotScaleFactorSliderWidget.singleStep = 1.0
    self.screenshotScaleFactorSliderWidget.minimum = 1.0
    self.screenshotScaleFactorSliderWidget.maximum = 50.0
    self.screenshotScaleFactorSliderWidget.value = 1.0
    self.screenshotScaleFactorSliderWidget.setToolTip("Set scale factor for the screen shots.")
    parametersFormLayout.addRow("Screenshot scale factor", self.screenshotScaleFactorSliderWidget)

    #
    # Apply Button
    #
    #self.applyButton = qt.QPushButton("Apply")
    #self.applyButton.toolTip = "Run the algorithm."
    #self.applyButton.enabled = False
    #parametersFormLayout.addRow(self.applyButton)

    # connections
    #self.applyButton.connect('clicked(bool)', self.onApplyButton)
    #self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    #self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = SlicerPathologyLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    screenshotScaleFactor = int(self.screenshotScaleFactorSliderWidget.value)
    print("Run the algorithm")
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), enableScreenshotsFlag,screenshotScaleFactor)
    
  def setupIcons(self):
    self.setupIcon = self.createIcon('icon-setup.png')
    self.imageSelectionIcon = self.createIcon('icon-imageselection.png')
    self.segmentationIcon = self.createIcon('icon-segmentation.png')
    self.submissionIcon = self.createIcon('icon-submission.png')

  def setupTabBarNavigation(self):
    self.tabWidget = qt.QTabWidget()
    self.layout.addWidget(self.tabWidget)

    setupGroupBox = qt.QGroupBox()
    imageSelectionGroupBox = qt.QGroupBox()
    segmentationGroupBox = qt.QGroupBox()
    submissionGroupBox = qt.QGroupBox()

    self.setupGroupBoxLayout = qt.QFormLayout()
    self.imageSelectionGroupBoxLayout = qt.QFormLayout()
    self.segmentationGroupBoxLayout = qt.QGridLayout()
    self.submissionGroupBoxLayout = qt.QFormLayout()

    setupGroupBox.setLayout(self.setupGroupBoxLayout)
    imageSelectionGroupBox.setLayout(self.imageSelectionGroupBoxLayout)
    segmentationGroupBox.setLayout(self.segmentationGroupBoxLayout)
    submissionGroupBox.setLayout(self.submissionGroupBoxLayout)

    self.tabWidget.setIconSize(qt.QSize(85, 30))

    self.tabWidget.addTab(setupGroupBox, self.setupIcon, '')
    self.tabWidget.addTab(imageSelectionGroupBox, self.imageSelectionIcon, '')
    self.tabWidget.addTab(segmentationGroupBox, self.segmentationIcon, '')
    self.tabWidget.addTab(submissionGroupBox, self.submissionIcon, '')
    self.tabWidget.connect('currentChanged(int)',self.onTabWidgetClicked)

    self.setTabsEnabled([1,2,3,4], True)

  def onTabWidgetClicked(self, currentIndex):
    if currentIndex == 0:
      self.onStep1Selected()
    if currentIndex == 1:
      print "to be implemented..."
    if currentIndex == 2:
      print "to be implemented..."
    if currentIndex == 3:
      print "to be implemented..."

  def setTabsEnabled(self, indexes, enabled):
    for index in indexes:
      self.tabWidget.childAt(1, 1).setTabEnabled(index, enabled)
     
  def onStep1Selected(self):
#if self.checkStep3or4Leave() is True:
#return
    if self.currentStep == 1:
      return
    self.currentStep = 1
    self.setTabsEnabled([0],True)
    self.setTabsEnabled([1,2,3], False)
    
  def setupsetupUI(self):
    self.setupUserName = qt.QLineEdit()
    self.setupGroupBoxLayout.addRow("Username:", self.setupUserName)
    self.setupPassword = qt.QLineEdit()
    self.setupPassword.setEchoMode(2)
    self.setupGroupBoxLayout.addRow("Password:", self.setupPassword)
    
  def setupimageSelectionUI(self):
    self.loadDataButton = qt.QPushButton("Load Data")
    self.imageSelectionGroupBoxLayout.addWidget(self.loadDataButton)
    self.loadDataButton.connect('clicked()', self.loadTCGAData)

  def setupsegmentationUI(self):
    #self.segmentationGroupBoxLayout.addWidget(self.SomeButton)
    print "ading this for now..."
    
  def setupsubmissionUI(self):
    self.dataDirButton = ctk.ctkDirectoryButton()
    self.submissionGroupBoxLayout.addWidget(qt.QLabel("Data directory:") )
    self.submissionGroupBoxLayout.addWidget(self.dataDirButton)
    self.SaveButton = qt.QPushButton("Save")
    self.submissionGroupBoxLayout.addWidget(self.SaveButton)
    self.SaveButton.connect('clicked()', self.onSaveButtonClicked)
    self.WebSaveButton = qt.QPushButton("Submit to web")
    self.submissionGroupBoxLayout.addWidget(self.WebSaveButton)
    self.WebSaveButton.connect('clicked()', self.onWebSaveButtonClicked)
    
  def onSaveButtonClicked(self):
    print "local save"
    a = EditUtil.EditUtil()
    p = a.getParameterNode()
    bundle = p.GetParameter('QuickTCGAEffect,erich')
    j = json.loads(bundle)
    j['username'] = self.setupUserName.text
    print "* * *"
    print j
    print "= = ="
    labelNodes = slicer.util.getNodes('vtkMRMLLabelMapVolumeNode*')
    savedMessage = 'Segmentations for the following series were saved:\n\n'
    for label in labelNodes.values():
      labelName = label.GetName()
      labelFileName = os.path.join(self.dataDirButton.directory, labelName + '.tif')
      print "labelFileName : "+labelFileName
      sNode = slicer.vtkMRMLVolumeArchetypeStorageNode()
      sNode.SetFileName(labelFileName)
      sNode.SetWriteFileFormat('tif')
      sNode.SetURI(None)
      success = sNode.WriteData(label)
      if success:
        print "successful writing "+labelFileName
      else:
        print "failed writing "+labelFileName
    ci = slicer.util.findChildren(slicer.modules.SlicerPathologyWidget.editorWidget.volumes, 'StructuresView')[0] 
    ci = ci.currentIndex().row()
    print ci
    jstr = json.dumps(j,sort_keys=True, indent=4, separators=(',', ': '))
    f = open(os.path.join(self.dataDirButton.directory, labelName + '.json'),'w')
    f.write(jstr)
    f.close()

  def onWebSaveButtonClicked(self):
    print "Web Save to be implemented...."

  def checkAndSetLUT(self):
    # Default to module color table
    self.resourcesPath = os.path.join(slicer.modules.slicerpathology.path.replace(self.moduleName+".py",""), 'Resources')
    self.colorFile = os.path.join(self.resourcesPath, "Colors/SlicerPathology.csv")
    self.customLUTLabel.setText('Using Default LUT')
    try:
        self.editorWidget.helper.structureListWidget.merge = None
    except AttributeError:
        pass
    # setup the color table, make sure SlicerPathology LUT is a singleton
    allColorTableNodes = slicer.util.getNodes('vtkMRMLColorTableNode*').values()
    for ctn in allColorTableNodes:
        #print "color: "+ctn.GetName()
        if ctn.GetName() == 'SlicerPathologyColor':
            slicer.mrmlScene.RemoveNode(ctn)
            break
    self.SlicerPathologyColorNode = slicer.vtkMRMLColorTableNode()
    colorNode = self.SlicerPathologyColorNode
    colorNode.SetName('SlicerPathologyColor')
    slicer.mrmlScene.AddNode(colorNode)
    colorNode.SetTypeToUser()
    with open(self.colorFile) as f:
        n = sum(1 for line in f)
    colorNode.SetNumberOfColors(n-1)
    colorNode.NamesInitialisedOn()
    import csv
    self.structureNames = []
    with open(self.colorFile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for index,row in enumerate(reader):
            success = colorNode.SetColor(index ,row['Label'],float(row['R'])/255,float(row['G'])/255,float(row['B'])/255,float(row['A']))
            if not success:
                print "color %s could not be set" % row['Label']
            self.structureNames.append(row['Label'])

  def setupEditorWidget(self):
    editorWidgetParent = slicer.qMRMLWidget()
    editorWidgetParent.setLayout(qt.QVBoxLayout())
    editorWidgetParent.setMRMLScene(slicer.mrmlScene)
    self.editorWidget = EditorWidget(parent=editorWidgetParent)
    self.editorWidget.setup()
    self.segmentationGroupBoxLayout.addWidget(self.editorWidget.parent)
#    self.segmentationGroupBoxLayout.addWidget(editorWidgetParent)
#    self.hideUnwantedEditorUIElements()
#    self.configureEditorEffectsUI()

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
    #m = slicer.util.mainWindow()
    #m.moduleSelector().selectModule('Editor')
    #print("Load...")
    self.checkAndSetLUT() 
    cv = slicer.util.getNode('FA')
    self.volumesLogic = slicer.modules.volumes.logic()
    labelName = 'FA-label'
    refLabel = self.volumesLogic.CreateAndAddLabelVolume(slicer.mrmlScene,cv,labelName)
    refLabel.GetDisplayNode().SetAndObserveColorNodeID(self.SlicerPathologyColorNode.GetID())
    slicer.modules.EditorWidget.helper.setMergeVolume(refLabel)
    #slicer.util.mainWindow().moduleSelector().selectModule('Editor')
    #editorWidgetParent = slicer.qMRMLWidget()
    #editorWidgetParent.setLayout(qt.QVBoxLayout())
    #editorWidgetParent.setMRMLScene(slicer.mrmlScene)
    #self.editorWidget = EditorWidget(parent=editorWidgetParent)
    #self.editorWidget.setup()
    #self.segmentationGroupBoxLayout.addWidget(self.editorWidget.parent)
#
# SlicerPathologyLogic
#

class SlicerPathologyLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
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
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

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

    self.takeScreenshot('SlicerPathology-Start','Start',-1)

    return True


class SlicerPathologyTest(ScriptedLoadableModuleTest):

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_SlicerPathology1()

  def test_SlicerPathology1(self):
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
    logic = SlicerPathologyLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
