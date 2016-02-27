project(vtkSlicer${MODULE_NAME}ModuleLogic)

#-----------------------------------------------------------------------------
set(KIT ${PROJECT_NAME})

set(${KIT}_EXPORT_DIRECTIVE "VTK_SLICER_${MODULE_NAME_UPPER}_MODULE_LOGIC_EXPORT")

set(${KIT}_INCLUDE_DIRECTORIES
  )

#Build Logic as a lib
set(QuickTCGA_SRC
  utilities.h
  QuickTCGASegmenter.h
  QuickTCGASegmenter.cxx
  )

set(QuickTCGA_LIBS
  ${ITK_LIBRARIES}
  ${VTK_LIBRARIES}
  )

#add_library(QuickTCGALogic STATIC $QuickTCGA_SRC$)
add_subdirectory(NucleusSeg_Yi)

add_library(QuickTCGALogic utilities.h QuickTCGASegmenter.h QuickTCGASegmenter.cxx)
target_link_libraries(QuickTCGALogic ${QuickTCGA_LIBS} NucleiSegLib)


set(${KIT}_SRCS
  vtkSlicer${MODULE_NAME}Logic.cxx
  vtkSlicer${MODULE_NAME}Logic.h
  vtkQuickTCGA.cxx
  vtkQuickTCGA.h
  )

set(${KIT}_TARGET_LIBRARIES
#  ${ITK_LIBRARIES}
  QuickTCGALogic
  )

#-----------------------------------------------------------------------------
SlicerMacroBuildModuleLogic(
  NAME ${KIT}
  EXPORT_DIRECTIVE ${${KIT}_EXPORT_DIRECTIVE}
  INCLUDE_DIRECTORIES ${${KIT}_INCLUDE_DIRECTORIES}
  SRCS ${${KIT}_SRCS}
  TARGET_LIBRARIES ${${KIT}_TARGET_LIBRARIES}
  )
