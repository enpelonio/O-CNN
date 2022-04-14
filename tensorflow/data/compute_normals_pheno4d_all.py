import multiprocessing
from multiprocessing import Pool
import os
import shutil
from pathlib import Path
import time

start_time = time.time()

current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
root_folder = os.path.join(current_path, 'script/dataset/pheno4d_segmentation')
#root_folder = os.path.join(current_path, 'script/dataset/shapenet_segmentation')
dataset_folder = 'Pheno4D'
txt_folder = os.path.join(root_folder, dataset_folder)
ply_folder = os.path.join(root_folder, 'ply')

categories = ['Maize01', 'Maize02', 'Maize03', 'Maize04', 'Maize05', 'Maize06', 'Maize07',
              'Tomato01', 'Tomato02', 'Tomato03', 'Tomato04', 'Tomato05', 'Tomato06', 'Tomato07']

filepaths = []
unprocessed = []

def getFiles():
  for c in categories:
    src_folder = os.path.join(txt_folder, c)
    filenames = os.listdir(src_folder)
    for filename in filenames:
      if(Path(filename).stem.endswith('a')):  # file is labeled
        filepath = os.path.join(src_folder, filename)
        filepaths.append(str(filepath))

def process_filepaths(filepath):
  des_folder_maize = os.path.join(ply_folder, 'Maize')
  des_folder_tomato = os.path.join(ply_folder, 'Tomato')
  if not os.path.exists(des_folder_maize): os.makedirs(des_folder_maize)
  if not os.path.exists(des_folder_tomato): os.makedirs(des_folder_tomato)
  base_filename = os.path.basename(filepath)
  filename, file_extension = os.path.splitext(base_filename)
  des_folder = des_folder_maize if base_filename.startswith('M') else des_folder_tomato
  filepath_normals = os.path.join(filepath[:-4] + '_NORMALS.ply')
  filepath_move = os.path.join(des_folder, filename + '.ply')
  cmd = 'python compute_normals_pheno4d.py --file %s' % (filepath)
  print(cmd)
  os.system(cmd)
  if not(Path(filepath_normals).is_file()):
      unprocessed.append(base_filename)
  else:
    shutil.move(filepath_normals, filepath_move)

def pool_handler():
  cpu = multiprocessing.cpu_count()
  p = Pool(cpu)
  p.map(process_filepaths, filepaths)

def compute_stats():
  execution_time = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
  print(execution_time)

def log_unprocessed():
  if(len(unprocessed)):
    print('\nLog unprocesed ...')
    log_header = 'Unprocessed files: %s' % str(len(unprocessed))
    log_content = '\n'.join([log_header] + unprocessed)
    print(log_content)
    filename_log = os.path.join(ply_folder, 'log_unprocessed.txt')
    with open(filename_log, 'w') as fid:
      fid.write(log_content)

if __name__ == '__main__':
  getFiles()
  # for f in filepaths:
  #   print(f)
  pool_handler()
  compute_stats()
  log_unprocessed()