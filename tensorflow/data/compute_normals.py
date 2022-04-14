import argparse
import os
import re
import shutil
import atexit
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--cloudcompare', type = str, required = True,
                    help = 'ex. --cloudcompare C:\CloudCompare\CloudCompare.exe')
parser.add_argument('--file', type = str, required = True,
                    help = 'ex. --file C:\models\\file.ply')
args = parser.parse_args()

cloudcompare = os.path.join(args.cloudcompare)
filename = os.path.join(args.file)
current_path = os.path.dirname(filename)
base_filename = Path(filename).stem

def on_exit():
  # delete normals
  octree_normals = os.path.join(current_path, base_filename + '_OCTREE_NORMALS.ply')
  if Path(octree_normals).is_file: os.remove(octree_normals)
atexit.register(on_exit)

cmd = '%s -silent -c_export_fmt ply -ply_export_fmt ascii -no_timestamp -o %s -octree_normals auto -orient plus_y -model quadric' % (cloudcompare, filename)
print(cmd)
os.system(cmd)
octree_normals = os.path.join(current_path, base_filename + '_OCTREE_NORMALS.ply')
filename_normals = os.path.join(current_path, base_filename + '_NORMALS.ply')
shutil.copy(octree_normals, filename_normals)