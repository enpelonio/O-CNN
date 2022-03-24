import argparse
import os
import pheno4d_utils
import shutil
import atexit
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--file', type = str, required = True,
                    help = 'ex. --file /models/file.ply')
parser.add_argument('--target', type = int, required = False,
                    help = 'ex. --target 100000',
                    default = 100000)
args = parser.parse_args()

filepath = os.path.join(args.file)
target = args.target
cloudcompare = pheno4d_utils.get_cloudcompare()
filepath_copy = pheno4d_utils.ply_duplicate(filepath)

def on_exit():
  if Path(filepath_copy).is_file: os.remove(filepath_copy)
atexit.register(on_exit)

if __name__ == '__main__':
  pheno4d_utils.ply_label2scalar(filepath_copy)
  cmd = 'python reduce_points2.py --cloudcompare %s --file %s --target %s' % (cloudcompare, filepath_copy, str(target))
  print(cmd)
  os.system(cmd)
  filename, file_extension = os.path.splitext(filepath)
  filename_copy, file_extension_copy = os.path.splitext(filepath_copy)
  filepath_reduced = filename + '_REDUCED' + file_extension
  filepath_reduced_temp = filename_copy + '_REDUCED' + file_extension_copy
  shutil.move(filepath_reduced_temp, filepath_reduced)
  pheno4d_utils.ply_scalar2label(filepath_reduced)