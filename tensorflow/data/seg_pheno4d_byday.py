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

txt_folder = os.path.join(root_folder, 'txt_reduced_10000_byday')
ply_folder = os.path.join(root_folder, 'ply_reduced_10000_byday')
points_folder = os.path.join(root_folder, 'points_reduced_10000_byday')
dataset_folder = os.path.join(root_folder, 'datasets_reduced_10000_byday')

categories= ['T0315', 'T0325', 'T0321', 'T0305', 'T0311', 'T0324', 'T0313', 'T0317', 'T0307', 'T0319', 'T0309', 
'M0315', 'M0325', 'M0321', 'M0324', 'M0313', 'M0317', 'M0319',]
seg_num   = [2] * len(categories)


def create_ply_folder_byday():
  not_byday_ply = os.path.join(root_folder, 'ply_reduced_10000')
  files = getListOfFiles(not_byday_ply)
  if not os.path.isdir(ply_folder):
    os.mkdir(ply_folder)
  for cat in categories:
    cat_path = os.path.join(ply_folder,cat)
    if not os.path.isdir(cat_path):
      os.mkdir(cat_path)
    kind = 'Tomato' if cat[0] == 'T' else 'Maize'
    week = cat[1:]
    for file in files:
      if kind in file and week in file:
        shutil.copy2(file,cat_path)


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

def points_to_tfrecords():
  print('Convert points files to tfrecords files ...')
  if not os.path.exists(dataset_folder): os.makedirs(dataset_folder)
  list_folder     = os.path.join(txt_folder, 'train_test_split')
  if not os.path.exists(list_folder): os.makedirs(list_folder)

  for i, c in enumerate(categories):
    filelist_name = os.path.join(list_folder, c + '_train_val.txt')
    class_files = getListOfFiles(os.path.join(points_folder,c))
    train,test = train_test_split(class_files, test_size=0.4, random_state = 42)
    filelist = ['%s %d' % (line, i) for line in train]
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
    filelist = ['%s %d' % (line, i) for line in test]
    
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
  create_ply_folder_byday()
  ply_to_points()
  points_to_tfrecords()
