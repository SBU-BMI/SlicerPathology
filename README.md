# 3D Slicer Pathology Extension

This is work in progress to develop tools for automatic and semi-automatic pathology segmentation tools for use as an extension within 3D Slicer (http://slicer.org).

# Contact

* Lead developer: Erich Bremer (https://github.com/ebremer erich.bremer@stonybrook.edu)
* Project PI: Joel Saltz (https://bmi.stonybrookmedicine.edu/people/joel_saltz)

# Acknowledgments

Additional Coding and 3D Slicer programming support:<br>
Nicole Aucoin (https://github.com/naucoin)<br>
Andrey Fedorov (https://github.com/fedorov)<br>

This work is supported by:

* U24 CA180924 Tools to Analyze Morphology and Spatially Mapped Molecular Data, PI Joel Saltz, Stony Brook University
* U24 CA180918 Quantitative Image Informatics for Cancer Research (QIICR), http://qiicr.org, PIs Ron Kikinis and Andrey Fedorov, Brigham and Women's Hospital

# Usage
Go to Module, Pathology.

Click "Load data directly from file" to select an image.

Click the button labeled Quick TCGA Effect.
This adds a palette to the interface where you can change the parameters of the run.

Click segmentation button to run an algorithm over the image with the current parameters.
Hit the "Y" key to continue.

After a few moments it’ll come back segmented.

Left-click & drag to select a subregion.
Now you can run the function on that area only.
