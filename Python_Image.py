# Python_Image
# Written by Robin J Scales (2024-02-23)
# Sections that are mainly taken from the aforementioned url source will be distinctly sectioned
#
# Useful URLs and potential future features
# https://stackoverflow.com/questions/179369/how-do-i-abort-the-execution-of-a-python-script
# https://imagej.net/scripting/toolbox
# https://forum.image.sc/t/jython-ij-run-scale-problem/34421/15
# https://forum.image.sc/t/makerectangle-with-python/2127
# https://forum.image.sc/t/how-to-convert-macro-ijm-to-python-code/32471
# https://imagej.net/scripting/jython/examples
# https://imagej.net/scripting/jython/


from ij import IJ, Prefs
from ij.io import DirectoryChooser
import os
import sys
from fiji.util.gui import GenericDialogPlus

addScalebar = True

# The following is inspired from here
# https://imagej.net/scripting/generic-dialog
##################################################################################################
# Create an instance of GenericDialogPlus
gui = GenericDialogPlus("Settings")

# The GenericDialogPlus also allows to select files, folder or both using a browse button
gui.addFileField("Some_file path", "DefaultFilePath")
# For the below you can add in your own default folder by replacing DefaultFolder with a string of your path. Remember to change \ to / as I think that is needed to work.
gui.addNumericField("Scale Bar Length", 50)

gui.showDialog()

# Recover the inputs in order of "appearance"
if gui.wasOKed():
    scalebarlength = gui.getNextNumber()
    # Path are recovered as string
    filePath   = gui.getNextString()
    folderPath = gui.getNextString()
##################################################################################################

print(len(filePath))

#folderPath = folderPath.replace("\\", "/")

# The below is a nice hack that allows you to copy and paste the path to the image
if filePath[0] == '\"':
    filename = filePath.strip('\"')
else:
    filename = filePath

# This is the save directory to which the image will automatically be saved to
savedir = folderPath


# Loadings in the image from the filename
imp = IJ.openImage(filename)
# Shows the loaded image.
imp.show()
# Extract image width. Will be useful for scaling.
w = imp.getWidth()

# Dictionary containing the height to crop the image to in pixels
CropAmountDict = {
  "1024": 691,
  "2048": 1415,
  "4096": 2830
}

# Dictionary containing the heights of the scale bars in pixels
ScaleBarHeightDict = {
  "1024": 16,
  "2048": 32,
  "4096": 64
}

# Dictionary containing the fontsize to use for the scale bar
ScaleBarFSDict = {
  "1024": 60,
  "2048": 120,
  "4096": 240
}

# Extracts the corresponding correct crop amount from the dictionary
if CropAmountDict.get(str(w)) is not None:
    CropAmount = CropAmountDict.get(str(w))
else:
    print("Key does not exist in the dictionary.")

# The following does the same as above but will run into an error if not available
ScaleBarHeight = ScaleBarHeightDict.get(str(w))
ScaleBarFontSize = ScaleBarFSDict.get(str(w))
print("ScaleBarHeight "+str(ScaleBarHeight)+"\nScaleBarFontSize "+str(ScaleBarFontSize)+"\nCropAmount "+str(CropAmount))


# The following is inspired from here
# https://www.geeksforgeeks.org/python-program-to-print-lines-containing-given-string-in-file/
##################################################################################################
# entering try block 
try: 
  
    # opening and reading the file  
    file_read = open(filename, "r") 
  
    # asking the user to enter the string to be  
    # searched 
    text = "Image Pixel Size = " 
#    input("Enter the String: ") 
  
    # reading file content line by line. 
    lines = file_read.readlines() 
  
    new_list = [] 
    idx = 0
  
    # looping through each line in the file 
    for line in lines: 
#        print(line)
        # if line have the input string, get the index  
        # of that line and put the 
        # line into newly created list  
        if text in line: 
            new_list.insert(idx, line) 
            idx += 1
  
    # closing file after reading 
    file_read.close() 

    print(str(new_list))
#    print(str(idx))
  
    # if length of new list is 0 that means  
    # the input string doesn't 
    # found in the text file 
    if len(new_list)==0: 
        print("\n\"" +text+ "\" is not found in \"" +file_name+ "\"!") 
    else: 
  
        # displaying the lines  
        # containing given string 
        lineLen = len(new_list) 
        print("\n**** Lines containing \"" +text+ "\" ****\n") 
        # Could not get the below to work - RJS
#        for i in range(lineLen): 
#            print(end=new_list[i]) 
#        print() 
  
# entering except block 
# if input file doesn't exist  
except : 
  print("\nThe file doesn't exist!")
##################################################################################################

# The following uses the nice way to extract out the conversion from the tif file and extracts
# how many nm a pixel represents. It will never really use any other value usually.
calibration0 = new_list[0]
print(calibration0)
calibration1 = calibration0.split(" = ")
calibration2 = calibration1[1].split(" ")
calibration = calibration2[0]

# Sometimes the units of nm are actually reasonable rather than microns.
# If you set the scale manually based from the value if you use the value from the "new_list" you will see what I mean
metric = (float(1000)*float(scalebarlength))/float(calibration)
print(metric)
in_nm = metric>w
if in_nm:
    print("Having to convert to nm scale: "+str(in_nm))

# This draws a rectangle from which the image will be cropped
IJ.makeRectangle(0, 0, w, CropAmount)
# This command crops the image
IJ.run("Crop");
if in_nm:
    # This will be done if nm are the most reasonable units to show
    IJ.run("Set Scale...", "distance=1 known="+str(calibration)+" unit=nm");
else:
    # This will be done if microns are the most reasonable units to show
    IJ.run("Set Scale...", "distance=1000 known="+str(calibration)+" unit=um");
# This sets the scale bar parameters and can be changed manually
if addScalebar:
    IJ.run("Scale Bar...", "width="+str(scalebarlength)+" height="+str(ScaleBarHeight)+" font="+str(ScaleBarFontSize)+" color=White background=None location=[Lower Right] bold overlay")

# The following is inpsired from here
# https://note.nkmk.me/en/python-os-basename-dirname-split-splitext/
##################################################################################################
# Extract out the base name of the file you selected
basename_without_ext = os.path.splitext(os.path.basename(filename))[0]
##################################################################################################
# Generate save name
saveName = "SEM "+basename_without_ext+".png"
# Save the new image as a png in the directory savedir
IJ.saveAs(imp, "png", os.path.join(savedir, saveName));
print("Saved image as:\n"+saveName+"\nTo folder:\n"+savedir)

#IJ.run("Close");