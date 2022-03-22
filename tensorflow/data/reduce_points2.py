import argparse
import os
import re
import random
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--cloudcompare', type = str, required = True,
                    help = 'ex. --cloudcompare C:\CloudCompare\CloudCompare.exe')
parser.add_argument('--file', type = str, required = True,
                    help = 'ex. --file C:\models\\file.ply')
parser.add_argument('--target', type = int, required = False,
                    help = 'ex. --target 100000',
                    default = 100000)
args = parser.parse_args()

cloudcompare = args.cloudcompare.replace(os.sep, '/')
filename = args.file.replace(os.sep, '/')
current_path = os.path.dirname(filename)
base_filename = Path(filename).stem

def get_vertices_count(filename):
  with open(filename, 'r') as fid:
    for line in fid:
      if line == '\n': continue
      nums = line.split()
      if nums[0] == 'element' and nums[1] == 'vertex':
        return int(nums[2])

# Recursive Python program to find key closest to k in given Binary Search Tree. 
  
# Utility that allocates a new node with the given key and NULL left and right pointers. 
class newnode: 
  # Constructor to create a new node 
  def __init__(self, data): 
    self.key = data 
    self.left = None
    self.right = None
  
# Function to find node with minimum absolute difference with given K 
# min_diff --> minimum difference till now 
# min_diff_key --> node having minimum absolute difference with K 
def maxDiffUtil(ptr, k, min_diff, min_diff_key):
  if ptr == None: 
    return

  subsample_filename = os.path.join(current_path, base_filename + '_SPATIAL_SUBSAMPLED.ply')
  subsample_rename = os.path.join(current_path, base_filename + '_SPATIAL_SUBSAMPLED_%s.ply' % str(ptr.key))
  cmd = '%s -silent -c_export_fmt ply -ply_export_fmt ascii -no_timestamp -o %s -SS SPATIAL %s' % (cloudcompare, filename, str(ptr.key/1000))
  print(cmd)
  os.system(cmd)
  shutil.move(subsample_filename, subsample_rename)
  points = get_vertices_count(subsample_rename)
        
  # If k itself is present 
  if points == k:  # if ptr.key == k:
    min_diff_key[0] = k
    return

  # update min_diff and min_diff_key by checking current node value 
  if min_diff > abs(points - k): # if min_diff > abs(ptr.key - k):
    min_diff = abs(points - k) # min_diff = abs(ptr.key - k)
    min_diff_key[0] = ptr.key

  # default: if k is less than ptr->key then move in left subtree else in right subtree
  # in this case, if k(target) < points the space should be increased to further reduce points and vice versa
  if k < points: # if k < ptr.key:
    maxDiffUtil(ptr.right, k, min_diff, min_diff_key)
  else:
    maxDiffUtil(ptr.left, k, min_diff, min_diff_key)
  
# Wrapper over maxDiffUtil() 
def maxDiff(root, k):
  # Initialize minimum difference 
  min_diff, min_diff_key = 999999999999, [-1]

  # Find value of min_diff_key (Closest key in tree with k) 
  maxDiffUtil(root, k, min_diff, min_diff_key)

  return min_diff_key[0]

# A utility function to do inorder tree traversal
def inorder(root):
  if root:
    inorder(root.left)
    print(root.key)
    inorder(root.right)

# A utility function to insert a new node with the given key
def insert(root, key):
  if root is None:
    return newnode(key)
  else:
    if root.key == key:
      return root
    elif root.key < key:
      root.right = insert(root.right, key)
    else:
      root.left = insert(root.left, key)
  return root

if __name__ == '__main__':
  spaces = range(10,610,10) # where n will be n/1000
  root = newnode(spaces[int(len(spaces)/2)]) # set middle value as root
  spaces = list(spaces)
  random.shuffle(spaces) # randomize to balance the tree
  for space in spaces:
    insert(root, space)
  k = args.target
  closest_key = maxDiff(root, k)
  subsample_closest = os.path.join(current_path, base_filename + '_SPATIAL_SUBSAMPLED_%s.ply' % str(closest_key))
  filename_reduced = os.path.join(current_path, base_filename + '_REDUCED.ply')
  shutil.copy(subsample_closest, filename_reduced)

  # delete generated subsamples
  filenames = os.listdir(current_path)
  for _filename in filenames:
    subsample = '^' + base_filename + '_SPATIAL_SUBSAMPLED*'
    if re.search(subsample, _filename):
      filename_subsample = os.path.join(current_path, _filename)
      os.remove(filename_subsample)