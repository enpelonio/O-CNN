import os
import shutil
from pathlib import Path

def ply_change_header(new_header, filepath):
  header = new_header
  ply_header = False
  with open(filepath, 'r') as fid:
    lines = []
    for line in fid:
      if line == '\n': continue
      nums = line.split()
      if nums[0] == 'end_header':
        ply_header = True
        continue
      if(not(ply_header)): continue
      lines.append(' '.join(nums))

  ply_header = header % len(lines)
  ply_content = '\n'.join([ply_header] + lines)
  with open(filepath, 'w') as fid:
    fid.write(ply_content)

def ply_scalar2label(filepath):
  header = 'ply\nformat ascii 1.0\nelement vertex %d\n' + \
    'property float x\nproperty float y\nproperty float z\n' + \
    'property float nx\nproperty float ny\nproperty float nz\n' + \
    'property float label\nelement face 0\n' + \
    'property list uchar int vertex_indices\nend_header'
  ply_change_header(header, filepath)

def ply_label2scalar(filepath):
  header = 'ply\nformat ascii 1.0\nelement vertex %d\n' + \
    'property float x\nproperty float y\nproperty float z\n' + \
    'property float nx\nproperty float ny\nproperty float nz\n' + \
    'property float scalar_label\nelement face 0\n' + \
    'property list uchar int vertex_indices\nend_header'
  ply_change_header(header, filepath)

def ply_duplicate(filepath):
  filename, file_extension = os.path.splitext(filepath)
  duplicate = filename + '_copy' + file_extension
  return shutil.copy(filepath, duplicate)

def is_cloudcompare(filepath):
  return Path(filepath).is_file()

def get_cloudcompare():
  if os.name == 'nt':
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    cloudcompare_folder = os.path.join(project_root, 'cloudcompare')
    name = 'CloudCompare.exe'
    for root, dirs, files in os.walk(cloudcompare_folder):
      if name in files:
        return os.path.join(root, name)
    return project_root
  
  elif os.name == 'posix':
    return 'cloudcompare.CloudCompare'