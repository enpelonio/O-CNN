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

def remove_soil(filepath):
  filename, file_extension = os.path.splitext(os.path.basename(filepath))
  label_0_2 = ['M02_0313_a', 'M02_0315_a', 'M02_0317_a', 'M02_0319_a', 'M02_0321_a', 'M02_0324_a', 'M02_0325_a']
  label_0_3 = ['M03_0321_a']
  label_0_4 = ['M03_0324_a']
  with open(filepath, 'r') as fid:
        lines = []
        for line in fid:
            if line == '\n': continue
            nums = line.split()
            if filename.startswith('M'): nums = nums[:-1]                 # ignore maize 2nd label standard
            soil, stem = '0', '1'                                         # default labels
            for s in label_0_2:
              if filename.startswith(s): soil, stem = '0', '2'
            for s in label_0_3:
              if filename.startswith(s): soil, stem = '0', '3'
            for s in label_0_4:
              if filename.startswith(s): soil, stem = '0', '4'
            if filename.startswith('T02_0325_a') : soil, stem = '1', '0'  # special case
            if nums[-1] == soil: continue                                 # ignore soil
            if nums[-1] == stem: nums[-1] = '0'                           # set stem label
            else: nums[-1] = '1'                                          # set all leaves to same label
            nums[1], nums[2] = nums[2], nums[1]                           # swap y and z axis
            nums[0] = str(float(nums[0]) * -1)                            # inverse x axis
            lines.append(' '.join(nums))

  content = '\n'.join(lines)
  with open(filepath, 'w') as fid:
      fid.write(content)