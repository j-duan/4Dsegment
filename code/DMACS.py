import time
import numpy as np, nibabel as nib, pandas as pd
import tensorflow as tf
from deepseg import *
from p1processing import *
from p2processing import *
from meshfitting import *
from motionEstimation import *
from decimation import *

""" Deployment parameters """
FLAGS = tf.app.flags.FLAGS
#tf.app.flags.DEFINE_integer('coreNo', 3, 'Number of CPUs.')
#tf.app.flags.DEFINE_string('test_dir', '/vol/medic02/users/jduan/New_BRIDGE_Cases4',
#                           'Path to the test set directory, under which images are organised in '
#                           'subdirectories for each subject.')
#tf.app.flags.DEFINE_string('model_path', '/vol/medic02/users/jduan/HHData/tensorflowFCNCodes/DeepRegionEdgeSegmentation'
#                           '/saver/model/vgg_RE_network/vgg_RE_network.ckpt-50000', 'Path to the saved trained model.')
#tf.app.flags.DEFINE_string('atlas_dir', '/vol/medic02/users/jduan/HHData/3Dshapes_new', 'Path to the atlas.')
#tf.app.flags.DEFINE_string('param_dir', '/vol/medic02/users/jduan/myPatchMatch/par', 'Path to the registration parameters.')
#tf.app.flags.DEFINE_string('template_dir', '/vol/medic02/users/jduan/myPatchMatch/template_wenzhe', 'Path to the template.')
#tf.app.flags.DEFINE_string('template_PH', '/vol/medic02/users/jduan/myPatchMatch/vtks', 'Path to the template.')



tf.app.flags.DEFINE_integer('coreNo', 8, 'Number of CPUs.')
tf.app.flags.DEFINE_string('test_dir', '/data',
                           'Path to the test set directory, under which images are organised in '
                           'subdirectories for each subject.')
tf.app.flags.DEFINE_string('model_path',  '/code/model/vgg_RE_network.ckpt-50000', 'Path to the saved trained model.')
tf.app.flags.DEFINE_string('atlas_dir',  '/refs', 'Path to the atlas.')
tf.app.flags.DEFINE_string('param_dir', '/par', 'Path to the registration parameters.')
tf.app.flags.DEFINE_string('template_dir', '/vtks/1', 'Path to the template.')
tf.app.flags.DEFINE_string('template_PH', '/vtks/2', 'Path to the template.')
tf.app.flags.DEFINE_boolean('irtk', True, 'use irtk or not')

if __name__ == '__main__':
    
        print('Start evaluating on the test set ...')
        table_time = []
        start_time = time.time()

        deeplearningseg(FLAGS.model_path, FLAGS.test_dir, FLAGS.atlas_dir)
                 
        # multiatlasreg2D(FLAGS.test_dir, FLAGS.atlas_dir, FLAGS.param_dir, FLAGS.coreNo, True, FLAGS.irtk) # parallel, irtk

        multiatlasreg3D(FLAGS.test_dir, FLAGS.atlas_dir, FLAGS.param_dir, FLAGS.coreNo, True, FLAGS.irtk) # parallel, irtk

        meshCoregstration(FLAGS.test_dir, FLAGS.param_dir, FLAGS.template_dir, FLAGS.coreNo, True, False) # parallel, irtk

        motionTracking(FLAGS.test_dir, FLAGS.param_dir, FLAGS.template_PH, FLAGS.coreNo, True) # parallel
        
        decimate(FLAGS.test_dir, FLAGS.coreNo, False) 

        process_time = time.time() - start_time 
        print('Including image I/O, CUDA resource allocation, '
              'it took {:.3f}s in total for processing all the subjects).'.format(process_time))
