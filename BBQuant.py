#This script is for quantifying fluorscence at the basal body of flagella
#Expected input is an image that has been cropped very closely to the basal bodies

from scipy import ndimage
from skimage import io
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from skimage.feature import peak_local_max
import pandas as pd
import csv
import os
import scipy.misc

def BBQuant(loc, name, strain):
    #Thresholding
    scalefactor = 4

    #loc = "./10.516-10.480.tif"
    img = io.imread(loc)
    nframes = int(img.shape[0])

    #Remove noise by subtractin minimum value
    minval = np.amin(img)
    img = img - minval
    for i in range(0, img.shape[0]):
        img[i] = ndimage.gaussian_filter(img[i], sigma = (3,1), order = 0)

    #For thresholding purposes, collect maximum pixel value
    maxval = np.amax(img)
    print("Max value:", maxval)

    #Make image that is the sum of all images
    img_sum = np.zeros((img.shape[1], img.shape[2]))
    for i in range(0, nframes):
        img_sum = img_sum + img[i]
    # plt.figure("Sum Image")
    # plt.imshow(img_sum, cmap = "gray")
    # plt.show()
    #Find local maxima. Threshold is set to find two local maxima, but may need adjusting
    thresh = 2*maxval
    img_peaks = peak_local_max(img_sum, min_distance = 2, threshold_abs = thresh)
    if((img_peaks.shape[0]) >= 2 and img_peaks.shape[0] > 0):
        print(img_peaks.shape[0])
        img_peaks = pd.DataFrame(img_peaks)
        #Collect the intensity of each peak
        inten = []
        for index, row in img_peaks.iterrows():
            inten.append(img_sum[row[0]][row[1]])
        img_peaks[2] = inten
        img_peaks = img_peaks.sort_values(by = 2, ascending = False).reset_index()
        print(img_peaks)

        #Reassign max value to be the maximum of local maxima
        print(img_peaks[0][0])

        # plt.figure("Peaks")
        # plt.imshow(img_sum, cmap = "gray")
        # plt.plot(img_peaks[1], img_peaks[0],'ro')
        # plt.show()

        #Now assign each pixel a group
        def listneighbors(y,x, img):
            newx = [x+1, x+1,x,x-1,x,x-1,x-1,x-1]
            newy = [y, y+1,y+1,y+1,y-1,y-1,y,y+1]
            nval = []
            for i in range(0, len(newx)):
                nval.append(img[newy[i]][newx[i]])
            return(max(nval))

        img_group = np.zeros((img.shape))
        #Mark the local maxima in each frame
        for i in range(0, nframes):
            locmax = np.amax(img[i])
            if(img[i][img_peaks[0][0]][img_peaks[1][0]] > maxval/scalefactor):
                img_group[i][img_peaks[0][0]][img_peaks[1][0]]= 1
            if(img[i][img_peaks[0][1]][img_peaks[1][1]] > maxval/scalefactor):
                img_group[i][img_peaks[0][1]][img_peaks[1][1]] = 2

        #Two rounds of chamfer method to group the cells
        for i in range(0, img.shape[0]):
            for j in range(1, img.shape[1]-1):
                for k in range(1, img.shape[2]-1):
                    if(img_group[i][j][k] <= listneighbors(j,k,img_group[i]) and img[i][j][k] > maxval/scalefactor):
                        img_group[i][j][k] = listneighbors(j,k,img_group[i])

        for i in range(0, img.shape[0]):
            for j in range(img.shape[1]-2, 2, -1):
                for k in range(img.shape[2]-2, 2, -1):
                    if(img_group[i][j][k] <= listneighbors(j,k,img_group[i]) and img[i][j][k] > maxval/scalefactor):
                        img_group[i][j][k] = listneighbors(j,k,img_group[i])

        # for i in range(0, img.shape[0]):
        # plt.subplot(121), plt.imshow(img[i])
        # plt.subplot(122), plt.imshow(img_group[i])
        # plt.show()

        #Now, collect data in a frame [group, value]
        pixData = []
        TotalInt = 0 #To store total intensity of object
        pixcount = 0
        fla1 = 0
        fla2 = 0
        points = []
        for i in range(0, img.shape[0]):
            for j in range(0,img.shape[1]):
                for k in range(0, img.shape[2]):
                    if(img_group[i][j][k] != 0):
                        pixData.append([img_group[i][j][k], img[i][j][k]])
                        TotalInt = TotalInt + img[i][j][k]
                        pixcount = pixcount + 1
                        points.append([i,j,k])
                    if(img_group[i][j][k] == 1):
                        fla1 = fla1 + img[i][j][k]
                    elif(img_group[i][j][k] == 2):
                        fla2 = fla2 + img[i][j][k]

        # points = pd.DataFrame(points)
        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')
        # ax.scatter(xs = points[0],ys = points[1], zs = points[2],s = 100)
        # plt.show()

        if(pixcount > 0):
            #Write Data
            Data = [name, TotalInt, strain, TotalInt/pixcount, pixcount, fla1, fla2]
            if(not os.path.isfile("Data.csv")):
                with open(r"Data.csv",'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Sample', 'TotalInt', 'Strain', "avgInt", "pixelcount", "fla1", "fla2"])

            with open(r"Data.csv", 'a') as f:
                writer = csv.writer(f)
                writer.writerow(Data)

            # io.imshow_collection(img)
            # io.imshow_collection(img_group)
            # plt.show()
