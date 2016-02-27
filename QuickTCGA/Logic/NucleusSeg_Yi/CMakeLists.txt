
#-----------------------------------------------------------------------------
find_package(ITK COMPONENTS ITKVideoBridgeOpenCV REQUIRED)
include(${ITK_USE_FILE})

#-----------------------------------------------------------------------------
find_package(OpenCV 3.1 REQUIRED)

#-----------------------------------------------------------------------------
set(NucleiSegSrc
  BinaryMaskAnalysisFilter.cxx
  Normalization.cpp
  PixelOperations.cpp
  ProcessTileUtils.cxx
  )
add_library(NucleiSegLib STATIC ${NucleiSegSrc})
target_link_libraries(NucleiSegLib ${OpenCV_LIBS})
target_include_directories(NucleiSegLib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
