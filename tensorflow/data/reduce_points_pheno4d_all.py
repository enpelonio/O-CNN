import multiprocessing
from multiprocessing import Pool
import argparse
import os
import shutil
from pathlib import Path
import time

start_time = time.time()
parser = argparse.ArgumentParser()
parser.add_argument('--target', type = int, required = False,
                    help = 'ex. --target 10000',
                    default = 100000)
args = parser.parse_args()
target = args.target

current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
#root_folder = os.path.join(current_path, 'script/dataset/shapenet_segmentation')
root_folder = os.path.join(current_path, 'script/dataset/pheno4d_segmentation')
dataset_folder = 'ply'
ply_folder = os.path.join(root_folder, dataset_folder)
reduced_folder = os.path.join(root_folder, 'ply_reduced_' + str(target))

# categories = ['Maize01', 'Maize02', 'Maize03', 'Maize04', 'Maize05', 'Maize06', 'Maize07',
#               'Tomato01', 'Tomato02', 'Tomato03', 'Tomato04', 'Tomato05', 'Tomato06', 'Tomato07']
categories = ['Maize', 'Tomato']

filepaths = []
unprocessed = []

def getFiles():
  for c in categories:
    src_folder = os.path.join(ply_folder, c)
    filenames = os.listdir(src_folder)
    for filename in filenames:
      filepath = os.path.join(src_folder, filename)
      filepaths.append(str(filepath))

def process_filepaths(filepath):
  des_folder_maize = os.path.join(reduced_folder, 'Maize')
  des_folder_tomato = os.path.join(reduced_folder, 'Tomato')
  if not os.path.exists(des_folder_maize): os.makedirs(des_folder_maize)
  if not os.path.exists(des_folder_tomato): os.makedirs(des_folder_tomato)
  base_filename = os.path.basename(filepath)
  filename, file_extension = os.path.splitext(filepath)
  des_folder = des_folder_maize if base_filename.startswith('M') else des_folder_tomato
  filepath_reduced = filename + '_REDUCED' + file_extension
  filepath_move = os.path.join(des_folder, base_filename)
  cmd = 'python reduce_points_pheno4d.py --file %s --target %s' % (filepath, str(target))
  print(cmd)
  os.system(cmd)
  if not(Path(filepath_reduced).is_file()):
      unprocessed.append(base_filename)
  else:
    shutil.move(filepath_reduced, filepath_move)

def pool_handler():
  cpu = multiprocessing.cpu_count()
  p = Pool(cpu)
  p.map(process_filepaths, filepaths)

def compute_stats():
  print('\nCompute stats ...')
  max_points = 0
  min_points = 10**9
  avg_points = 0
  clouds = 0
  lines = []
  for i, c in enumerate(categories):
    src_folder = os.path.join(reduced_folder, c)

    filenames = os.listdir(src_folder)
    clouds += len(filenames)
    for filename in filenames:
      filename_ply = os.path.join(src_folder, filename)
      with open(filename_ply, 'r') as fid:
        for line in fid:
          if line == '\n': continue
          nums = line.split()
          if nums[0] == 'element' and nums[1] == 'vertex':
            points = int(nums[2])
            avg_points += points
            max_points = max(max_points, points)
            min_points = min(min_points, points)
            lines.append('%s %s' % (filename, nums[2]))
            break
  avg_points /= clouds
  execution_time = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
  log_header = 'Point clouds: ' + str(clouds) + \
    '\nMax points: ' + str(max_points) + \
    '\nMin points: ' + str(min_points) + \
    '\nAverage points: ' + str(avg_points) + \
    '\nExecution time: ' + str(execution_time)
  print(log_header)
  log_content = '\n'.join([log_header] + lines)
  filename_log = os.path.join(reduced_folder, 'log_reduced.txt')
  with open(filename_log, 'w') as fid:
    fid.write(log_content)

def log_unprocessed():
  if(len(unprocessed)):
    print('\nLog unprocesed ...')
    log_header = 'Unprocessed files: %s' % str(len(unprocessed))
    log_content = '\n'.join([log_header] + unprocessed)
    print(log_content)
    filename_log = os.path.join(reduced_folder, 'log_unprocessed.txt')
    with open(filename_log, 'w') as fid:
      fid.write(log_content)

if __name__ == '__main__':
  getFiles()
  pool_handler()
  compute_stats()
  log_unprocessed()
