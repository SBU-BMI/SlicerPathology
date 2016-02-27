cmake_minimum_required(VERSION 3.0.1)

project(SlicerPathology)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://www.example.com/Slicer/Extensions/SlicerPathology")
set(EXTENSION_CATEGORY "Pathology")
set(EXTENSION_CONTRIBUTORS "Erich Bremer (Stony Brook University), Yi Gao (Stony Brook University), Joel Saltz (Stony Brook University), Nicole Aucoin (BWH), Jean-Christophe Fillion-Robin (Kitware)")
set(EXTENSION_DESCRIPTION "An extension to provide multiscale segmentation tools.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/SlicerPathology.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/SlicerPathology/Screenshots/1.png")
set(EXTENSION_DEPENDS "SlicerOpenCV")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

find_package(SlicerOpenCV REQUIRED)

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(QuickTCGA)

add_subdirectory(QuickTCGAEffect)
add_subdirectory(ShortCut)
add_subdirectory(SlicerPathology)
## NEXT_MODULE

#-----------------------------------------------------------------------------
# include(${Slicer_EXTENSION_CPACK})
