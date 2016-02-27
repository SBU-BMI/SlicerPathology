
#-----------------------------------------------------------------------------
find_package(ITK COMPONENTS ITKVideoBridgeOpenCV REQUIRED)
include(${ITK_USE_FILE})

#-----------------------------------------------------------------------------
find_package(OpenCV 3.1 REQUIRED)

message(STATUS "OpenCV library status:")
message(STATUS "    version: ${OpenCV_VERSION}")
message(STATUS "    libraries: ${OpenCV_LIBS}")

#-----------------------------------------------------------------------------
set(NucleiSegSrc BinaryMaskAnalysisFilter.cxx Normalization.cpp PixelOperations.cpp ProcessTileUtils.cxx)
add_library(NucleiSegLib STATIC ${NucleiSegSrc})
target_link_libraries(NucleiSegLib ${QuickTCGA_LIBS} ${OpenCV_LIBS})
