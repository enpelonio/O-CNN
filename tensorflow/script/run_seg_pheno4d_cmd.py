import os
import csv
import math
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--alias', type=str, required=False,
                    default='0204_shapenet_randinit')
parser.add_argument('--gpu', type=int, required=False, default=0)
parser.add_argument('--mode', type=str, required=False, default='randinit')
parser.add_argument('--ckpt', type=str, required=False,
                    default='/home/ervin/Desktop/Thesis/O-CNN/tensorflow/script/logs/hrnet/plant3D/256.fixed/iter_080000.ckpt_renamed.ckpt')

args = parser.parse_args()
alias = args.alias
gpu = args.gpu
mode = args.mode

factor = 2
batch_size = 8
ckpt = args.ckpt if mode != 'randinit' else '\'\''
module = 'run_seg_pheno4d_finetune.py' if mode != 'randinit' else 'run_seg_shapenet.py'
script = 'python %s --config configs/seg_hrnet_pheno4d_pts.yaml' % module
if mode != 'randinit': script += ' SOLVER.mode %s ' % mode
data = 'dataset/shapenet_segmentation/datasets_reduced_10000_strict_byday'


categories= ['T01', 'T02', 'T03', 'T04', 'T05', 'T06', 'T07', 'M01', 'M02', 'M03', 'M04', 'M05', 'M06', 'M07']
seg_num   = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
train_num = [6, 6, 6, 6, 7, 7, 7, 4, 4, 4, 4, 3, 3, 3]
test_num =  [5, 5, 5, 5, 4, 4, 4, 3, 3, 3, 3, 4, 4, 4]
max_iters = [500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500]
#           [22012,  581,  412,  6722, 28612,  516,  5869, 2925, 
#            11822, 3441, 1416,  1369,  2194,  506,  1134, 41447] 
test_iters= [100, 100]
ratios = [0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.00]
# longer iterations when data < 10%
muls   = [   2,    2,    2,    1,    1,    1,    1]


for i in range(len(ratios)):
  for k in range(len(categories)):
    ratio, cat = ratios[i], categories[k]
    max_iter = int(max_iters[k] * ratio * muls[i])
    step_size1, step_size2 = int(0.5 * max_iter), int(0.25 * max_iter)
    #test_every_iter = int(test_iters[k] * ratio * muls[i])
    test_every_iter = 2
    take = int(math.ceil(train_num[k] * ratio))

    cmds = [
      script,
      'SOLVER.gpu {},'.format(gpu),
      'SOLVER.logdir logs/seg/{}/{}/ratio_{:.2f}'.format(alias, cat, ratio),
      'SOLVER.max_iter {}'.format(max_iter),
      'SOLVER.step_size {},{}'.format(step_size1, step_size2),
      'SOLVER.test_every_iter {}'.format(test_every_iter),
      'SOLVER.test_iter {}'.format(test_num[k]),
      'SOLVER.ckpt {}'.format(ckpt),
      'DATA.train.location {}/{}_train_val.tfrecords'.format(data, cat),
      'DATA.train.take {}'.format(take),
      'DATA.test.location {}/{}_test.tfrecords'.format(data, cat),
      'MODEL.nout {}'.format(seg_num[k]),
      'MODEL.factor {}'.format(factor),
      'LOSS.num_class {}'.format(seg_num[k])]

    cmd = ' '.join(cmds)
    print('\n', cmd, '\n')
    os.system(cmd)

summary = []
summary.append('names, ' + ', '.join(categories))
summary.append('train_num, ' + ', '.join([str(x) for x in train_num]))
summary.append('test_num, ' + ', '.join([str(x) for x in test_num]))
for i in range(len(ratios)-1, -1, -1):
  ious = [None] * len(categories)  
  for j in range(len(categories)):
    cat, ratio = categories[j], ratios[i]
    filename = 'logs/seg/{}/{}/ratio_{:.2f}/test_summaries.csv'.format(alias, cat, ratio)
    with open(filename, newline='') as fid:
      reader = csv.reader(fid)
      for k, row in enumerate(reader):
        if k == 0: idx = row.index(' iou')
    ious[j] = row[idx]
  summary.append('Ratio:{:.2f}, '.format(ratios[i]) + ', '.join(ious))

with open('logs/seg/{}/summaries.csv'.format(alias), 'w') as fid:
  summ = '\n'.join(summary)
  fid.write(summ)
  # print(summ)