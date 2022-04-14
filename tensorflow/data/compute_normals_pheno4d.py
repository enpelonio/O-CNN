import os
import shutil
from pathlib import Path

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
root_folder = os.path.join(current_path, 'script/dataset/pheno4d_segmentation')
dataset_folder = 'Pheno4D'
txt_folder = os.path.join(root_folder, dataset_folder)
ply_folder = os.path.join(root_folder, 'ply')
cloudcompare = os.path.join(project_root, 'cloudcompare/CloudCompare_v2.12.beta_bin_x64/CloudCompare.exe')

categories = ['Maize01', 'Maize02', 'Maize03', 'Maize04', 'Maize05', 'Maize06', 'Maize07',
              'Tomato01', 'Tomato02', 'Tomato03', 'Tomato04', 'Tomato05', 'Tomato06', 'Tomato07']

def process_pheno4d():
    for c in categories:
        src_folder = os.path.join(txt_folder, c)
        des_folder_maize = os.path.join(ply_folder, 'Maize')
        des_folder_tomato = os.path.join(ply_folder, 'Tomato')
        if not os.path.exists(des_folder_maize): os.makedirs(des_folder_maize)
        if not os.path.exists(des_folder_tomato): os.makedirs(des_folder_tomato)

        filenames = os.listdir(src_folder)
        for filename in filenames:
            if(Path(filename).stem.endswith('a')):  # file is labeled
                print(filename)
                des_folder = des_folder_maize if filename.startswith('M') else des_folder_tomato
                filename_ply = filename[:-4] + '.ply'
                remove_txt_soil(filename, src_folder, des_folder)
                compute_txt_normals(filename, des_folder, des_folder)
                delete_txt_normals(filename, des_folder)
                modify_ply_header(filename_ply, des_folder)

def remove_txt_soil(filename, src_folder, des_folder):
    filename_txt = os.path.join(src_folder, filename)
    filename_txt_no_soil = os.path.join(des_folder, filename)
    with open(filename_txt, 'r') as fid:
        lines = []
        for line in fid:
            if line == '\n': continue
            nums = line.split()
            if filename.startswith('M'): nums = nums[:-1]           # ignore maize 2nd label standard
            soil, stem = '0', '1'                                   # default labels
            if filename.startswith('M02'): soil, stem = '0', '2'    # M02s default labels
            if filename == 'T02_0325_a' : soil, stem = '1', '0'     # special case
            if nums[-1] == soil: continue                           # ignore soil
            if nums[-1] == stem: nums[-1] = '0'                     # set stem label
            else: nums[-1] = '1'                                    # set all leaves to same label
            nums[1], nums[2] = nums[2], nums[1]                     # swap y and z axis
            nums[0] = str(float(nums[0]) * -1)                      # inverse x axis
            lines.append(' '.join(nums))
        
    ply_content = '\n'.join(lines)
    with open(filename_txt_no_soil, 'w') as fid:
        fid.write(ply_content)

def compute_txt_normals(filename, src_folder, des_folder):
    filename_txt = os.path.join(src_folder, filename)
    filename_normals_ply = os.path.join(src_folder, filename[:-4] + '_OCTREE_NORMALS.ply')
    filename_ply = os.path.join(des_folder, filename[:-4] + '.ply')
    cmd = 'python compute_normals.py --cloudcompare %s --file %s' % (cloudcompare, filename_txt)
    print(cmd)
    os.system(cmd)
    shutil.move(filename_normals_ply, filename_ply)

def modify_ply_header(filename, src_folder):
    filename_ply = os.path.join(src_folder, filename[:-4] + '.ply')
    header = 'ply\nformat ascii 1.0\nelement vertex %d\n' + \
            'property float x\nproperty float y\nproperty float z\n' + \
            'property float nx\nproperty float ny\nproperty float nz\n' + \
            'property float label\nelement face 0\n' + \
            'property list uchar int vertex_indices\nend_header'
    ply_header = False
    with open(filename_ply, 'r') as fid:
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
    with open(filename_ply, 'w') as fid:
        fid.write(ply_content)

def delete_txt_normals(filename, src_folder):
    filename_txt = os.path.join(src_folder, filename)
    os.remove(filename_txt)

if __name__ == '__main__':
  process_pheno4d()