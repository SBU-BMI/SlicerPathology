project(vtkSlicer${MODULE_NAME}ModuleLogic)

#-----------------------------------------------------------------------------
add_subdirectory(NucleusSeg_Yi)

#-----------------------------------------------------------------------------
find_package(OpenCV 3.1 REQUIRED)

#-----------------------------------------------------------------------------
set(KIT ${PROJECT_NAME})

set(${KIT}_EXPORT_DIRECTIVE "VTK_SLICER_${MODULE_NAME_UPPER}_MODULE_LOGIC_EXPORT")

set(${KIT}_INCLUDE_DIRECTORIES
  )

set(${KIT}_WRAP_EXCLUDE_SRCS
  QuickTCGASegmenter.cxx
  QuickTCGASegmenter.h
  TCGAUtilities.cxx
  TCGAUtilities.h
  TCGAUtilities.hxx
  )

set(${KIT}_SRCS
  vtkQuickTCGA.cxx
  vtkQuickTCGA.h
  vtkSlicer${MODULE_NAME}Logic.cxx
  vtkSlicer${MODULE_NAME}Logic.h
  ${${KIT}_WRAP_EXCLUDE_SRCS}
  )

set_source_files_properties(
  ${${KIT}_WRAP_EXCLUDE_SRCS}
  WRAP_EXCLUDE
  )

set(${KIT}_TARGET_LIBRARIES
  ${OpenCV_LIBS}
  NucleiSegLib
  )

#-----------------------------------------------------------------------------
SlicerMacroBuildModuleLogic(
  NAME ${KIT}
  EXPORT_DIRECTIVE ${${KIT}_EXPORT_DIRECTIVE}
  INCLUDE_DIRECTORIES ${${KIT}_INCLUDE_DIRECTORIES}
  SRCS ${${KIT}_SRCS}
  TARGET_LIBRARIES ${${KIT}_TARGET_LIBRARIES}
  )
