import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--cloudcompare', type = str, required = True,
                    help = 'ex. --cloudcompare C:\CloudCompare\CloudCompare.exe')
parser.add_argument('--file', type = str, required = True,
                    help = 'ex. --file C:\models\\file.ply')
args = parser.parse_args()

cloudcompare = os.path.join(args.cloudcompare)
filename = os.path.join(args.file)
current_path = os.path.dirname(filename)

cmd = '%s -silent -c_export_fmt ply -ply_export_fmt ascii -no_timestamp -o %s -octree_normals auto -orient plus_y -model quadric' % (cloudcompare, filename)
print(cmd)
os.system(cmd)