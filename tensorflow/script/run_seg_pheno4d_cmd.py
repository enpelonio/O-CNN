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
                    default='dataset/midnet_data/mid_d6_o6/model/iter_800000.ckpt') #TODO

args = parser.parse_args()
alias = args.alias
gpu = args.gpu
mode = args.mode

factor = 2
batch_size = 32
##TODO
ckpt = args.ckpt if mode != 'randinit' else '\'\''
module = 'run_seg_pheno4d_finetune.py' if mode != 'randinit' else 'run_seg_shapenet.py'
script = 'python %s --config configs/seg_hrnet_pheno4d_pts.yaml' % module
if mode != 'randinit': script += ' SOLVER.mode %s ' % mode
data = 'dataset/shapenet_segmentation/datasets' # parent folder of the training and testing tfrecords
##TODO

categories= ['001']
names     = ['Tomato']
seg_num   = [3] # number of labels
train_num = [77] # number of instances
test_num =  [341, 14, 11, 153, 693, 14, 159, 80,
             285, 78, 51, 38, 41, 12, 31, 842] # test_num unsa ni?
max_iters = [20000]
#           [22012,  581,  412,  6722, 28612,  516,  5869, 2925, 
#            11822, 3441, 1416,  1369,  2194,  506,  1134, 41447] 
test_iters= [800] #test every iter
ratios = [0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.00]
# longer iterations when data < 10%
muls   = [   2,    2,    2,    1,    1,    1,    1]


for i in range(len(ratios)):
  for k in range(len(categories)):
    ratio, cat = ratios[i], categories[k]
    max_iter = int(max_iters[k] * ratio * muls[i])
    step_size1, step_size2 = int(0.5 * max_iter), int(0.25 * max_iter)
    test_every_iter = int(test_iters[k] * ratio * muls[i])
    take = int(math.ceil(train_num[k] * ratio))

    cmds = [
      script,
      'SOLVER.gpu {},'.format(gpu),
      'SOLVER.logdir logs/seg/{}/{}_{}/ratio_{:.2f}'.format(alias, cat, names[k], ratio),
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
summary.append('names, ' + ', '.join(names))
summary.append('train_num, ' + ', '.join([str(x) for x in train_num]))
summary.append('test_num, ' + ', '.join([str(x) for x in test_num]))
for i in range(len(ratios)-1, -1, -1):
  ious = [None] * len(categories)  
  for j in range(len(categories)):
    name, cat, ratio = names[j], categories[j], ratios[i]
    filename = 'logs/seg/{}/{}_{}/ratio_{:.2f}/test_summaries.csv'.format(alias, cat, name, ratio)
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