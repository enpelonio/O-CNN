import os
import shutil
import re
from pathlib import Path

current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
root_folder = os.path.join(current_path, 'script/dataset/pheno4d_segmentation')
dataset_folder = 'Pheno4D'
cloudcompare = 'D:/Code/Research/O-CNN/cloudcompare/CloudCompare_v2.12.beta_bin_x64/CloudCompare.exe'

txt_folder = os.path.join(root_folder, dataset_folder)
txt_no_soil_folder = os.path.join(root_folder, 'ply_temp')
ply_folder = os.path.join(root_folder, 'ply')

categories = ['Maize01', 'Maize02', 'Maize03', 'Maize04', 'Maize05', 'Maize06', 'Maize07',
              'Tomato01', 'Tomato02', 'Tomato03', 'Tomato04', 'Tomato05', 'Tomato06', 'Tomato07']