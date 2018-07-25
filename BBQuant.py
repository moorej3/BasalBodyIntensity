#This script is for quantifying fluorscence at the basal body of flagella
#Expected input is an image that has been cropped very closely to the basal bodies

from scipy import ndimage
from skimage import io
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import peak_local_max
import pandas as pd
import csv
import os
def BBQuant(loc, name):
    #loc = "./10.516-10.480.tif"
    img = io.imread(loc)
    nframes = int(img.shape[0])

    #For thresholding purposes, collect maximum pixel value
    maxval = np.amax(img)
    print("Max value:", maxval)

    #Make image that is the sum of all images
    img_sum = np.zeros((img.shape[1], img.shape[2]))
    for i in range(0, nframes):
        img_sum = img_sum + img[i]
    # plt.figure("Sum Image")
    # plt.imshow(img_sum, cmap = "gray")

    #Find local maxima. Threshold is set to find two local maxima, but may need adjusting
    thresh = 2.5*maxval
    img_peaks = peak_local_max(img_sum, min_distance = 2, threshold_abs = thresh)
    img_peaks = pd.DataFrame(img_peaks)
    print(img_peaks)
    # plt.figure("Peaks")
    # plt.imshow(img_sum, cmap = "gray")
    # plt.plot(img_peaks[1], img_peaks[0],'ro')

    #Now assign each pixel a group
    def listneighbors(y,x, img):
        newx = [x+1, x+1,x,x-1,x,x-1,x-1,x-1]
        newy = [y, y+1,y+1,y+1,y-1,y-1,y,y+1]
        nval = []
        for i in range(0, len(newx)):
            nval.append(img[newy[i]][newx[i]])
        return(max(nval))

    img_group = np.zeros((img.shape))
    for i in range(0, nframes):
        img_group[i][img_peaks[0][0]][img_peaks[1][0]] = 1
        img_group[i][img_peaks[0][1]][img_peaks[1][1]] = 2

    #Two rounds of chamfer method to group the cells
    for i in range(0, img.shape[0]):
        for j in range(1, img.shape[1]-1):
            for k in range(1, img.shape[2]-1):
                if(img_group[i][j][k] <= listneighbors(j,k,img_group[i]) and img[i][j][k] > maxval/3):
                    img_group[i][j][k] = listneighbors(j,k,img_group[i])

    for i in range(0, img.shape[0]):
        for j in range(img.shape[1]-2, 2, -1):
            for k in range(img.shape[2]-2, 2, -1):
                if(img_group[i][j][k] <= listneighbors(j,k,img_group[i]) and img[i][j][k] > maxval/3):
                    img_group[i][j][k] = listneighbors(j,k,img_group[i])

    #Now, collect data in a frame [group, value]
    pixData = []
    TotalInt = 0 #To store total intensity of object
    for i in range(0, img.shape[0]):
        for j in range(0,img.shape[1]):
            for k in range(0, img.shape[2]):
                if(img_group[i][j][k] != 0):
                    pixData.append([img_group[i][j][k], img[i][j][k]])
                    TotalInt = TotalInt + img[i][j][k]


    #Write Data
    Data = [name, TotalInt]
    if(not os.path.isfile("Data.csv")):
        with open(r"Data.csv",'a') as f:
            writer = csv.writer(f)
            writer.writerow(['Sample', 'TotalInt'])

    with open(r"Data.csv", 'a') as f:
        writer = csv.writer(f)
        writer.writerow(Data)
