from ctypes import util
from unicodedata import name
import tensorflow as tf

from config import parse_args, FLAGS
from dataset import DatasetFactory
from tfsolver import TFSolver
from ocnn import get_variables_with_name, Optimizer
from run_seg_shapenet import *
import numpy as np

from tensorflow.python import pywrap_tensorflow

class FinetuneOptimizer:
  def __init__(self, flags):
    self.flags = flags.SOLVER

  # build the solver: two different learning rate,
  # the learning rate of backbone is 0.1x smaller
  def __call__(self, total_loss, learning_rate):
    FLAGS = self.flags
    var_list = get_variables_with_name(
        name='ocnn', without='seg_header', verbose=FLAGS.verbose)
    optim_backbone = Optimizer(var_list=var_list, mul=0.1)
    solver1, lr1 = optim_backbone(total_loss, learning_rate)

    var_list = get_variables_with_name(
        name='seg_header', verbose=FLAGS.verbose)
    optim_header = Optimizer(var_list=var_list, mul=1.0)
    solver2, lr2 = optim_header(total_loss, learning_rate)

    solver = tf.group([solver1, solver2])
    return solver, lr2


class FC2Optimizer:
  def __init__(self, flags):
    self.flags = flags.SOLVER

  def __call__(self, total_loss, learning_rate):
    var_list = get_variables_with_name(
        name='seg_header', verbose=self.flags.verbose)
    optim_header = Optimizer(var_list=var_list, mul=1.0)
    solver2, lr2 = optim_header(total_loss, learning_rate)
    return solver2, lr2


class ShapeNetFinetune(TFSolver):
  def __init__(self, flags, compute_graph, build_solver):
    super(ShapeNetFinetune, self).__init__(flags, compute_graph, build_solver)

  def restore(self, sess, ckpt):
    # !!! Restore the trainable/untrainable variables under the name scope `ocnn`
    # Note the variables added by solvers are filtered out since they are not
    # under the scope of `ocnn`
    print('Restore from: ' + ckpt)
    var_restore = get_variables_with_name(
        'ocnn', without='predict_6/conv2', verbose=0, train_only=False)
    
    tf_saver = tf.train.Saver(var_list=var_restore)
    tf_saver.restore(sess, ckpt)

    print("Partial Restore")
  
  def evaluate(self):

    flags_data = FLAGS.DATA.test #just use test for now
    batch = DatasetFactory(flags_data)()
    octree = batch[0]
    pts, label = get_point_info(batch[2], flags_data.mask_ratio)
    logit = seg_network(octree, FLAGS.MODEL, False, False, pts=pts)
    #losses = loss_functions_seg(logit, label, FLAGS.LOSS.num_class,
    #                             FLAGS.LOSS.weight_decay, 'ocnn', mask=-1)

    # self.test_tensors, self.test_names = tensors,names
    #tf_saver = tf.train.Saver(max_to_keep = 10)
    #restore the model
    assert(self.flags.ckpt)   # the self.flags.ckpt should be provided
    #get predictions
    #print predictions
    config = tf.ConfigProto(allow_soft_placement=True)
    config.gpu_options.allow_growth = True
    tf_saver = tf.train.Saver(max_to_keep = 10)
    with tf.Session(config=config) as sess:
      # restore and initialize
      self.initialize(sess)
      print('Restore from checkpoint: %s' % self.flags.ckpt)
      tf_saver.restore(sess, self.flags.ckpt)

      preds = sess.run(logit)
      #labels_np = sess.run(label)
      print(preds)
      preds = np.argmax(preds, axis = 1)
      print(preds)
      #print('Shapes: ', len(labels_np.shape), len(preds.shape))
      #print('Length: ',len(labels_np),len(preds))
      #print(labels_np)
     #save labels
    
      # np.savetxt('sample_labels.txt', labels_np, delimiter='\n', newline='\n')
      np.savetxt('evals/preds.txt', preds, delimiter='\n', newline='\n')
  

# run the experiments
if __name__ == '__main__':
  FLAGS.SOLVER.mode = 'finetune'
  FLAGS = parse_args()
  compute_graph = ComputeGraphSeg(FLAGS)
  optimizer = FinetuneOptimizer if FLAGS.SOLVER.mode == 'finetune' else FC2Optimizer
  build_solver = optimizer(FLAGS)
  solver = ShapeNetFinetune(FLAGS, compute_graph, build_solver)
  solver.run()
