import logging
import qt
import vtk
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import numpy as np

#
# SegmentationVerification
#
class SegmentationVerification(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Segmentation Verification"
    self.parent.categories = ["Segmentation"]
    self.parent.dependencies = []
    self.parent.contributors = ["Csaba Pinter (EBATINCA)"]
    self.parent.helpText = """
This module allows manual revision of segments in a user friendly manner.
"""
    self.parent.acknowledgementText = """
This file was originally developed by Csaba Pinter (EBATINCA), with no funding.
"""


#
# SegmentationVerificationWidget
#
class SegmentationVerificationWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/SegmentationVerification.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = SegmentationVerificationLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    self.ui.showNeighborsCheckBox.clicked.connect(self.updateParameterNodeFromGUI)

    self.ui.segmentationNodeComboBox.currentNodeChanged.connect(self.onSegmentationChanged)
    self.ui.SegmentsTableView.selectionChanged.connect(self.onSegmentSelectionChanged)

    self.ui.nextButton.clicked.connect(self.onNextButton)
    self.ui.previousButton.clicked.connect(self.onPreviousButton)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.
    self.setParameterNode(self.logic.getParameterNode())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """
    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    self.ui.segmentationNodeComboBox.setCurrentNode(self._parameterNode.GetNodeReference("CurrentSegmentationNode"))

    showNeighbors = self._parameterNode.GetParameter("ShowNeighbors")
    self.ui.showNeighborsCheckBox.checked = True if showNeighbors == 'True' else False

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

    self._parameterNode.SetNodeReferenceID("CurrentSegmentationNode", self.ui.segmentationNodeComboBox.currentNodeID)

    self._parameterNode.SetParameter("ShowNeighbors", 'True' if self.ui.showNeighborsCheckBox.checked else 'False')

    self._parameterNode.EndModify(wasModified)

  def onSegmentationChanged(self, newSegmentationNode):
    """
    Switch to next segment.
    """
    if newSegmentationNode:
      self._parameterNode.SetNodeReferenceID("CurrentSegmentationNode", newSegmentationNode.GetID())
    else:
      self._parameterNode.SetNodeReferenceID("CurrentSegmentationNode", "")
      return

    # Set wait cursor
    qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)

    # Make sure segmentation is shown in 3D
    newSegmentationNode.CreateClosedSurfaceRepresentation()

    self.logic.initializeSegmentBoundingBoxes(self._parameterNode)

    # Enable next button but disable previous button until next is clicked
    self.ui.nextButton.setEnabled(True)
    self.ui.previousButton.setEnabled(False)

    qt.QApplication.restoreOverrideCursor()

  def onNextButton(self):
    """
    Switch to next segment.
    """
    segmentationNode = self._parameterNode.GetNodeReference("CurrentSegmentationNode")
    if not segmentationNode:
      raise ValueError("No segmentation node is selected")

    # Get next segment ID
    selectedSegmentIDs = self.ui.SegmentsTableView.selectedSegmentIDs()
    if len(selectedSegmentIDs) == 0:
      nextSegmentID = self.ui.SegmentsTableView.segmentIDForRow(0)
      logging.info(f'Selecting segment at row 0 (ID: {nextSegmentID})')
    else:
      selectedSegmentID = selectedSegmentIDs[0]
      nextRowIndex = self.ui.SegmentsTableView.rowForSegmentID(selectedSegmentID) + 1
      if nextRowIndex >= self.ui.SegmentsTableView.segmentCount():
        raise RuntimeError("There is no next segment")
      nextSegmentID = self.ui.SegmentsTableView.segmentIDForRow(nextRowIndex)
      logging.info(f'Selecting segment at row {nextRowIndex} (ID: {nextSegmentID})')

    # Select next segment
    self.ui.SegmentsTableView.setSelectedSegmentIDs([nextSegmentID])

  def onPreviousButton(self):
    """
    Switch to previous segment.
    """
    segmentationNode = self._parameterNode.GetNodeReference("CurrentSegmentationNode")
    if not segmentationNode:
      raise ValueError("No segmentation node is selected")

    # Get previous segment ID
    selectedSegmentIDs = self.ui.SegmentsTableView.selectedSegmentIDs()
    if len(selectedSegmentIDs) == 0:
      previousSegmentID = self.ui.SegmentsTableView.segmentIDForRow(self.ui.SegmentsTableView.segmentCount() - 1)
      logging.info(f'Selecting segment at row {self.ui.SegmentsTableView.segmentCount() - 1} (ID: {previousSegmentID})')
    else:
      selectedSegmentID = selectedSegmentIDs[0]
      previousRowIndex = self.ui.SegmentsTableView.rowForSegmentID(selectedSegmentID) - 1
      if previousRowIndex < 0:
        raise RuntimeError("There is no previous segment")
      previousSegmentID = self.ui.SegmentsTableView.segmentIDForRow(previousRowIndex)
      logging.info(f'Selecting segment at row {previousRowIndex} (ID: {previousSegmentID})')

    # Select previous segment
    self.ui.SegmentsTableView.setSelectedSegmentIDs([previousSegmentID])

  def onSegmentSelectionChanged(self):
    selectedSegmentIDs = self.ui.SegmentsTableView.selectedSegmentIDs()
    if len(selectedSegmentIDs) == 0 or len(selectedSegmentIDs) > 1:
      return
    selectedSegmentID = selectedSegmentIDs[0]

    # Set wait cursor
    qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)

    # Update next/previous button enabled state
    currentRowIndex = self.ui.SegmentsTableView.rowForSegmentID(selectedSegmentID)
    self.ui.nextButton.enabled = (currentRowIndex < self.ui.SegmentsTableView.segmentCount() - 1)
    self.ui.previousButton.enabled = (currentRowIndex > 0)

    # Perform segment selection
    self.logic.selectSegment(self._parameterNode, selectedSegmentID)

    qt.QApplication.restoreOverrideCursor()


#
# SegmentationVerificationLogic
#
class SegmentationVerificationLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)

    # Cached bounding boxes of all the segments
    self.segmentBoundingBoxes = {}

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("ShowNeighbors"):
      parameterNode.SetParameter("ShowNeighbors", "False")

  def initializeSegmentBoundingBoxes(self, parameterNode):
    if not parameterNode:
      raise ValueError("Invalid parameter node")
    segmentationNode = parameterNode.GetNodeReference("CurrentSegmentationNode")
    if not segmentationNode:
      raise ValueError("No segmentation node is selected")

    self.segmentBoundingBoxes = {}

    for segmentID in segmentationNode.GetSegmentation().GetSegmentIDs():
      segmentPolyData = vtk.vtkPolyData()
      segmentationNode.GetClosedSurfaceRepresentation(segmentID, segmentPolyData)

      #TODO: Apply transform if any

      segmentBoundingBox = np.zeros(6)
      segmentPolyData.GetBounds(segmentBoundingBox)
      self.segmentBoundingBoxes[segmentID] = segmentBoundingBox

  def selectSegment(self, parameterNode, segmentID):
    if not parameterNode:
      raise ValueError("Invalid parameter node")
    segmentationNode = parameterNode.GetNodeReference("CurrentSegmentationNode")
    if not segmentationNode:
      raise ValueError("No segmentation node is selected")

    # Center on tooth also in 3D
    boundingBox = self.segmentBoundingBoxes[segmentID]
    centerPointRas = np.array([(boundingBox[0] + boundingBox[1]) / 2.0, (boundingBox[2] + boundingBox[3]) / 2.0, (boundingBox[4] + boundingBox[5]) / 2.0])
    layoutManager = slicer.app.layoutManager()
    for threeDViewIndex in range(layoutManager.threeDViewCount) :
      view = layoutManager.threeDWidget(threeDViewIndex).threeDView()
      threeDViewNode = view.mrmlViewNode()
      cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(threeDViewNode)
      cameraNode.SetFocalPoint(centerPointRas)

    #TODO: Implement neighboring segment visualization
    showNeighbors = parameterNode.GetParameter("ShowNeighbors") == 'True'

    # Show only the selected segment
    #TODO: Allow only one update
    displayNode = segmentationNode.GetDisplayNode()
    for currentSegmentID in segmentationNode.GetSegmentation().GetSegmentIDs():
      displayNode.SetSegmentVisibility(currentSegmentID, segmentID == currentSegmentID)


#
# SegmentationVerificationTest
#
class SegmentationVerificationTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear()

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_SegmentationVerification1()

  def test_SegmentationVerification1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    # Get/create input data
    self.delayDisplay('Loaded test data set')

    outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")

    # Test the module logic
    logic = SegmentationVerificationLogic()

    self.delayDisplay('Test passed')
