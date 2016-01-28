set(NucleiSegSrc BinaryMaskAnalysisFilter.cxx Normalization.cpp PixelOperations.cpp ProcessTileUtils.cxx)
add_library(NucleiSegLib ${NucleiSegSrc})
target_link_libraries(NucleiSegLib ${QuickTCGA_LIBS})
