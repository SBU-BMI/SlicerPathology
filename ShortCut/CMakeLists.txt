cmake_minimum_required(VERSION 3.0.1)

#-----------------------------------------------------------------------------
set(MODULE_NAME ShortCut)

#-----------------------------------------------------------------------------
set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/4.3/Extensions/ShortCut")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "Steve Pieper (Isomics)")
set(EXTENSION_DESCRIPTION "This is an example of extension bundling one scripted loadable editor effect")
set(EXTENSION_ICONURL "http://viewvc.slicer.org/viewvc.cgi/Slicer4/trunk/Extensions/Testing/ShortCut/ShortCut.png?revision=21750&view=co")
set(EXTENSION_SCREENSHOTURLS "http://wiki.slicer.org/slicerWiki/images/4/42/Slicer-r19441-ShortCut-screenshot.png")

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  )

set(MODULE_PYTHON_RESOURCES
  ${MODULE_NAME}.png
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  VERBOSE
  )

