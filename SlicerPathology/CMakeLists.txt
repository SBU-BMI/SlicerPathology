
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
  Resources/Colors/SlicerPathology.csv
  )

#-----------------------------------------------------------------------------

 slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )
