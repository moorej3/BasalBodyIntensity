# BasalBodyIntensity
Determine the total fluorscence of basal bodies of chlamydomonas flagella

Procedure:
  1. Crop z-stacks of basal bodies to include only the two basal bodies and as little else as possible
  2. Put the BBQuant.py and BBQuantControlModule.py files in the same directory as your images.
  3. Run the BBQuantControlModule, which will search for all .tif files and analyze them
  4. The BBQuant program segments the basal bodies in 3d and sums the fluorescence of pixels belonging to the basal bodies.
  
Program Details:

  Dependencies: scipy, skimage, numpy, matplotlib, pandas, csv, os
