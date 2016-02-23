project(vtkSlicer${MODULE_NAME}ModuleLogic)

set(KIT ${PROJECT_NAME})

set(${KIT}_EXPORT_DIRECTIVE "VTK_SLICER_${MODULE_NAME_UPPER}_MODULE_LOGIC_EXPORT")

set(${KIT}_INCLUDE_DIRECTORIES
  )

#Build Logic as a lib
set(ShortCutCore_SRC
    ShortCutCoreSegmenter.h
    ShortCutCoreSegmenter.cxx
)

set(ShortCutCore_LIBS
${ITK_LIBRARIES}
${VTK_LIBRARIES}
${OpenCV_LIBS}
)

#add_library(ShortCutCoreLogic STATIC $ShortCutCore_SRC$)
#add_subdirectory(NucleusSeg_Yi)

add_library(ShortCutCoreLogic ShortCutCoreSegmenter.h ShortCutCoreSegmenter.cxx ShortCut.cpp)
target_link_libraries(ShortCutCoreLogic ${ShortCutCore_LIBS})


set(${KIT}_SRCS
  vtkSlicer${MODULE_NAME}Logic.cxx
  vtkSlicer${MODULE_NAME}Logic.h
  vtkShortCutCore.cxx
  vtkShortCutCore.h
  )

set(${KIT}_TARGET_LIBRARIES
#  ${ITK_LIBRARIES}
ShortCutCoreLogic
  )

#-----------------------------------------------------------------------------
SlicerMacroBuildModuleLogic(
  NAME ${KIT}
  EXPORT_DIRECTIVE ${${KIT}_EXPORT_DIRECTIVE}
  INCLUDE_DIRECTORIES ${${KIT}_INCLUDE_DIRECTORIES}
  SRCS ${${KIT}_SRCS}
  TARGET_LIBRARIES ${${KIT}_TARGET_LIBRARIES}
  )
