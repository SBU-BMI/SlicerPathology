
#-----------------------------------------------------------------------------
set(MODULE_NAME SlicerPathology)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}Util/__init__.py
  ${MODULE_NAME}Util/mixins.py
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

# copy the color file to the build directory
set(colorfile "SlicerPathology.csv")
message(STATUS "Colorfile: build destination directory = ${CMAKE_BINARY_DIR}/${Slicer_SHARE_DIR}/Resources/Colors")
configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/Resources/Colors/${colorfile}
  ${CMAKE_BINARY_DIR}/${Slicer_SHARE_DIR}/Resources/Colors/${colorfile}
  COPYONLY
  )

# install the color file in the install directory
message(STATUS "Colorfile: install destination: '${CMAKE_INSTALL_DIR}/Resources/Colors/${colorfile}'")
install(
  FILES ${CMAKE_CURRENT_SOURCE_DIR}/Resources/Colors/${colorfile}
  DESTINATION ${CMAKE_INSTALL_PREFIX}/Resources/Colors/${colorfile}
  COMPONENT Runtime
  )
