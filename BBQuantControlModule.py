from os import walk
import BBQuant

def listfiles(directory, extension):
    filelist = []
    for(dirpath, dirnames, filenames) in walk(directory):
        for f in filenames:
             if f.endswith(extension):
                 #print(dirpath+"/"+ f)
                 filelist.append(dirpath+"/" + f)
    return(filelist)

a = listfiles("./", ".tif")
print(a)
#a = a[3:4]
for file in a:
    file2 = file.rsplit("/",1)[1].rsplit('.tif')[0]
    strain = file.rsplit("/",1)[0].rsplit("./",1)[1]
    #print(strain)
    print("\n \n Analyzing " + file + "\n")
    #filename = file.split("./")[1].split("/")[0]
    BBQuant.BBQuant(file, file2, strain)
