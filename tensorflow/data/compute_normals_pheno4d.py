import argparse
import os
import pheno4d_utils
import shutil
import atexit
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--file', type = str, required = True,
                    help = 'ex. --file /models/file.ply')
args = parser.parse_args()

filepath = os.path.join(args.file)
cloudcompare = pheno4d_utils.get_cloudcompare()
filepath_copy = pheno4d_utils.ply_duplicate(filepath)

def on_exit():
  if Path(filepath_copy).is_file: os.remove(filepath_copy)
atexit.register(on_exit)

if __name__ == '__main__':
  pheno4d_utils.remove_soil(filepath_copy)
  cmd = 'python compute_normals.py --cloudcompare %s --file %s' % (cloudcompare, filepath_copy)
  print(cmd)
  os.system(cmd)
  filename, file_extension = os.path.splitext(filepath)
  filename_copy, file_extension_copy = os.path.splitext(filepath_copy)
  filepath_normals = filename + '_NORMALS.ply'
  filepath_normals_temp = filename_copy + '_NORMALS.ply'
  shutil.move(filepath_normals_temp, filepath_normals)
  pheno4d_utils.ply_scalar2label(filepath_normals)