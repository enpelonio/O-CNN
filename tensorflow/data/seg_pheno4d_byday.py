from cgi import test
import os
from random import random
import shutil
import json
from tracemalloc import start
from sklearn.model_selection import train_test_split

current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
root_folder = os.path.join(current_path, 'script/dataset/shapenet_segmentation')
ply2points = 'ply2points'
convert_tfrecords = os.path.join(current_path, 'util/convert_tfrecords.py')

txt_folder = os.path.join(root_folder, 'txt_reduced_10000_strict_byday')
ply_folder = os.path.join(root_folder, 'ply_reduced_10000_strict_byday')
points_folder = os.path.join(root_folder, 'points_reduced_10000_strict_byday')
dataset_folder = os.path.join(root_folder, 'datasets_reduced_10000_strict_byday')

categories= ['T01', 'T02', 'T03', 'T04', 'T05', 'T06', 'T07', 'M01', 'M02', 'M03', 'M04', 'M05', 'M06', 'M07']
seg_num   = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]


def ply_to_points():
  print('Convert ply files to points files ...')
  for c in categories:
    src_folder = os.path.join(ply_folder, c)
    des_folder = os.path.join(points_folder, c)
    list_folder = os.path.join(ply_folder, 'filelist')
    if not os.path.exists(des_folder): os.makedirs(des_folder)
    if not os.path.exists(list_folder): os.makedirs(list_folder)

    list_filename = os.path.join(list_folder, c + '.txt')
    filenames = [os.path.join(src_folder, filename) for filename in os.listdir(src_folder)]
    with open(list_filename, 'w') as fid:
      fid.write('\n'.join(filenames))

    cmds = [ply2points,
          '--filenames', list_filename,
          '--output_path', des_folder,
          '--verbose', '0']
    cmd = ' '.join(cmds)
    print(cmd + '\n')
    os.system(cmd)

def split_data_by_day(day):
  file_list = getListOfFilesByDay(points_folder,day)
  train, test = train_test_split(file_list, test_size=0.4, random_state = 42)
  return train,test

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
            allFiles.append(getSafeFileNameWithoutExt(fullPath))
                
    return allFiles

def getListOfFilesByDay(dirName, day):
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
        allFiles.append(getSafeFileNameWithoutExt(fullPath))
                
  return [file for file in allFiles if 'M'+day in file or 'T'+day in file]

def getSafeFileNameWithoutExt(file:str):
    start_index=-1
    
    for category in categories:
      start_index = safeFind(file,category)
      if start_index != -1:
        break
    end_index = file.rindex('.')
    return file[start_index:end_index]

def safeFind(string:str, substr:str):
  res = -1
  try:
    res = string.find(substr)
  except:
    pass
  return res

def points_to_tfrecords():
  print('Convert points files to tfrecords files ...')
  if not os.path.exists(dataset_folder): os.makedirs(dataset_folder)
  list_folder     = os.path.join(txt_folder, 'train_test_split')
  if not os.path.exists(list_folder): os.makedirs(list_folder)
  
  train_1, test_1 = split_data_by_day('01')
  train_2, test_2 = split_data_by_day('02')
  train_3, test_3 = split_data_by_day('03')
  train_4, test_4 = split_data_by_day('04')
  train_5, test_5 = split_data_by_day('05')
  train_6, test_6 = split_data_by_day('06')
  train_7, test_7 = split_data_by_day('07')

  for i, c in enumerate(categories):
    filelist_name = os.path.join(list_folder, c + '_train_val.txt')
    filelist = ['%s.points %d' % (line, i) for line in train_1 if c in line] + \
               ['%s.points %d' % (line, i) for line in train_2 if c in line] + \
               ['%s.points %d' % (line, i) for line in train_3 if c in line] + \
               ['%s.points %d' % (line, i) for line in train_4 if c in line] + \
               ['%s.points %d' % (line, i) for line in train_5 if c in line] + \
               ['%s.points %d' % (line, i) for line in train_6 if c in line] + \
               ['%s.points %d' % (line, i) for line in train_7 if c in line]
    print(filelist)
    with open(filelist_name, 'w') as fid:
      fid.write('\n'.join(filelist))

    dataset_name =  os.path.join(dataset_folder, c + '_train_val.tfrecords')
    cmds = ['python', convert_tfrecords,
            '--file_dir', points_folder,
            '--list_file', filelist_name,
            '--records_name', dataset_name]
    cmd = ' '.join(cmds)
    print(cmd + '\n')
    os.system(cmd)

    filelist_name = os.path.join(list_folder, c + '_test.txt')
    filelist = ['%s.points %d' % (line, i) for line in test_1 if c in line] + \
               ['%s.points %d' % (line, i) for line in test_2 if c in line] + \
               ['%s.points %d' % (line, i) for line in test_3 if c in line] + \
               ['%s.points %d' % (line, i) for line in test_4 if c in line] + \
               ['%s.points %d' % (line, i) for line in test_5 if c in line] + \
               ['%s.points %d' % (line, i) for line in test_6 if c in line] + \
               ['%s.points %d' % (line, i) for line in test_7 if c in line]
    with open(filelist_name, 'w') as fid:
      fid.write('\n'.join(filelist))

    dataset_name = os.path.join(dataset_folder, c + '_test.tfrecords')
    cmds = ['python', convert_tfrecords,
            '--file_dir', points_folder,
            '--list_file', filelist_name,
            '--records_name', dataset_name]
    cmd = ' '.join(cmds)
    print(cmd + '\n')
    os.system(cmd)
  des_folder = os.path.join(root_folder, 'train_test_split')
  if not os.path.exists(des_folder): 
    shutil.copytree(list_folder, des_folder)

if __name__ == '__main__':
  #ply_to_points()
  points_to_tfrecords()
  #split_data()
  #print(getListOfFiles(points_folder))