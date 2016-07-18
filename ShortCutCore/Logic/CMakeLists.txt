project(vtkSlicer${MODULE_NAME}ModuleLogic)

#-----------------------------------------------------------------------------
find_package(OpenCV REQUIRED)

#-----------------------------------------------------------------------------
set(KIT ${PROJECT_NAME})

set(${KIT}_EXPORT_DIRECTIVE "VTK_SLICER_${MODULE_NAME_UPPER}_MODULE_LOGIC_EXPORT")

set(${KIT}_INCLUDE_DIRECTORIES
  ${vtkSlicerQuickTCGAModuleLogic_INCLUDE_DIRS}
  )

set(${KIT}_WRAP_EXCLUDE_SRCS
  ShortCut.h
  ShortCut.cpp
  ShortCutCoreSegmenter.h
  ShortCutCoreSegmenter.cxx
  )

set(${KIT}_SRCS
  vtkSlicer${MODULE_NAME}Logic.cxx
  vtkSlicer${MODULE_NAME}Logic.h
  vtkShortCutCore.cxx
  vtkShortCutCore.h
  ${${KIT}_WRAP_EXCLUDE_SRCS}
  )

set_source_files_properties(
  ${${KIT}_WRAP_EXCLUDE_SRCS}
  PROPERTIES
    WRAP_EXCLUDE 1
    WRAP_EXCLUDE_PYTHON 1
  )

set(${KIT}_TARGET_LIBRARIES
  ${OpenCV_LIBS}
  vtkSlicerQuickTCGAModuleLogic
  )

#-----------------------------------------------------------------------------
SlicerMacroBuildModuleLogic(
  NAME ${KIT}
  EXPORT_DIRECTIVE ${${KIT}_EXPORT_DIRECTIVE}
  INCLUDE_DIRECTORIES ${${KIT}_INCLUDE_DIRECTORIES}
  SRCS ${${KIT}_SRCS}
  TARGET_LIBRARIES ${${KIT}_TARGET_LIBRARIES}
  )
