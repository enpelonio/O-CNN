from typing import Set


import os
main_folder = '/home/ervin/Desktop/Thesis/O-CNN/tensorflow/script/dataset/shapenet_segmentation/ply_reduced_10000_strict'

def get_week_classes():
    classes:set = set()
    files = getListOfFiles(main_folder)
    for file in files:
        file = str(getSafeFileName(file))
        start_idx = file.index('_')
        end_idx = file.rindex('_')
        classes.add(file[start_idx+1:end_idx])
    return classes

def getSafeFileName(file:str):
    index = file.rindex('/')
    return file[index+1:]
def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

print(get_week_classes())