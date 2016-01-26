cmake_minimum_required(VERSION 3.0.1)

project(SlicerPathology)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://www.example.com/Slicer/Extensions/SlicerPathology")
set(EXTENSION_CATEGORY "Pathology")
set(EXTENSION_CONTRIBUTORS "Erich Bremer (Stony Brook University), Yi Gao (Stony Brook University), Joel Saltz (Stony Brook University)")
set(EXTENSION_DESCRIPTION "An extension to provide multiscale segmentation tools.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/SlicerPathology.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/SlicerPathology/Screenshots/1.png")
set(EXTENSION_DEPENDS "SlicerOpenCV")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Get OpenCV from the SlicerOpenCV extension
set(SLICEROPENCV_DIR "" CACHE PATH "SlicerOpenCV qt loadable module directory")
MESSAGE(STATUS "SLICEROPENCV_DIR = ${SLICEROPENCV_DIR}")

# Set up include directories
set(SLICEROPENCV_INCLUDE_DIR "${SLICEROPENCV_DIR}/include")
INCLUDE_DIRECTORIES( ${SLICEROPENCV_INCLUDE_DIR} ${SLICEROPENCV_INCLUDE_DIR}/opencv ${SLICEROPENCV_INCLUDE_DIR}/ITK-4.9)
# Set up link directories
LINK_DIRECTORIES(${SLICEROPENCV_DIR}/lib)

#-----------------------------------------------------------------------------
set(MODULE_NAME SlicerPathology)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  Util/__init__.py
  Util/mixins.py
  ${MODULE_NAME}.py
  )
  
set(MODULE_PYTHON_RESOURCES
  Resources/Icons/icon-submission.png
  Resources/Icons/icon-infoBox.png
  Resources/Icons/icon-segmentation.png
  Resources/Icons/icon-imageselection.png
  Resources/Icons/icon-setup.png
  Resources/Icons/SlicerPathology-simple-small.png
  Resources/Icons/SlicerPathologyExtensionLogo.png
  Resources/Icons/SlicerPathology128px.png
  )

#-----------------------------------------------------------------------------

 slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS} 
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )
  
  
#-----------------------------------------------------------------------------
# Extension modules

add_subdirectory(QuickTCGAEffect)
add_subdirectory(ShortCut)
add_subdirectory(SPsegmentation)
## NEXT_MODULE

#-----------------------------------------------------------------------------
# include(${Slicer_EXTENSION_CPACK})
