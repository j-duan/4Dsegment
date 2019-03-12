import os, time, math
import nibabel as nib, numpy as np
import tensorflow as tf
import glob
from image_utils import *

def deeplearningseg(model_path, test_dir, atlas_dir):           
     
   with tf.Session() as sess:
       
        sess.run(tf.global_variables_initializer())

        # Import the computation graph and restore the variable values
        saver = tf.train.import_meta_graph('{0}.meta'.format(model_path))
        saver.restore(sess, '{0}'.format(model_path))
        
        # Process each subject subdirectory
        table_time = []


        if os.path.exists('{0}/subjnames.txt'.format(test_dir)):
            os.system('rm {0}/*.txt'.format(test_dir))
        os.system('touch {0}/subjnames.txt'.format(test_dir))
        for data in sorted(os.listdir(test_dir)):
            
            print(data)
            
            data_dir = os.path.join(test_dir, data)
            
            if not os.path.isdir(data_dir):
                print('  {0} is not a valid directory, Skip'.format(data_dir))
                continue
            
            file = open('{0}/subjnames.txt'.format(test_dir),'a')
            file.write('{0}\n'.format(data))
            file.close()
            
            if os.path.exists('{0}/PHsegmentation_ED.gipl'.format(data_dir)):
                os.system('rm {0}/*.gipl'.format(data_dir))
            if os.path.exists('{0}/lvsa_.nii.gz'.format(data_dir)):
                os.system('rm {0}/lvsa_*.nii.gz'.format(data_dir))
                os.system('rm {0}/seg_*.nii.gz'.format(data_dir))
            
            originalnii = glob.glob('{0}/*.nii'.format(data_dir))     
            if not originalnii:
                print('  original nifit image does not exist, use lvsa.nii.gz')
                originalnii = glob.glob('{0}/*.nii.gz'.format(data_dir))  
                imagePreprocessing(originalnii[0], data_dir, atlas_dir) 
            else:
                print('  start image preprocessing ...')
                imagePreprocessing(originalnii[0], data_dir, atlas_dir)
            
            # Process ED and ES time frames
            image_ED_name = '{0}/lvsa_{1}.nii.gz'.format(data_dir, 'ED')
            image_ES_name = '{0}/lvsa_{1}.nii.gz'.format(data_dir, 'ES')
   
            if not os.path.exists(image_ED_name) or not os.path.exists(image_ES_name):
                print(' Image {0} or {1} does not exist. Skip.'.format(image_ED_name, image_ES_name))
                continue
                               
            if os.path.exists('{0}/{1}'.format(data_dir, 'dofs')) or \
               os.path.exists('{0}/{1}'.format(data_dir, 'segs')) or \
               os.path.exists('{0}/{1}'.format(data_dir, 'tmps')) or \
               os.path.exists('{0}/{1}'.format(data_dir, 'sizes')) or \
               os.path.exists('{0}/{1}'.format(data_dir, 'motion')) or \
               os.path.exists('{0}/{1}'.format(data_dir, 'vtks')):
                    
                os.system('rm -rf {0}/{1}'.format(data_dir, 'dofs'))
                os.system('rm -rf {0}/{1}'.format(data_dir, 'segs'))
                os.system('rm -rf {0}/{1}'.format(data_dir, 'tmps'))
                os.system('rm -rf {0}/{1}'.format(data_dir, 'sizes'))
                os.system('rm -rf {0}/{1}'.format(data_dir, 'motion'))
                os.system('rm -rf {0}/{1}'.format(data_dir, 'vtks'))
                
                os.mkdir('{0}/{1}'.format(data_dir, 'dofs'))
                os.mkdir('{0}/{1}'.format(data_dir, 'segs'))
                os.mkdir('{0}/{1}'.format(data_dir, 'tmps'))
                os.mkdir('{0}/{1}'.format(data_dir, 'sizes'))
                os.mkdir('{0}/{1}'.format(data_dir, 'motion'))
                os.mkdir('{0}/{1}'.format(data_dir, 'vtks'))
                
            else: 
                
                os.mkdir('{0}/{1}'.format(data_dir, 'dofs'))
                os.mkdir('{0}/{1}'.format(data_dir, 'segs'))
                os.mkdir('{0}/{1}'.format(data_dir, 'tmps'))
                os.mkdir('{0}/{1}'.format(data_dir, 'sizes'))
                os.mkdir('{0}/{1}'.format(data_dir, 'motion'))
                os.mkdir('{0}/{1}'.format(data_dir, 'vtks'))

            for fr in ['ED', 'ES']:
       
                image_name = '{0}/lvsa_{1}.nii.gz'.format(data_dir, fr)

                # Read the image
                print('  Reading {} ...'.format(image_name))
                nim = nib.load(image_name)
                image = nim.get_data()

                imageOrg = np.squeeze(image, axis=-1).astype(np.int16)
                tmp = imageOrg

                X, Y, Z = image.shape[:3]
                
                print('  Segmenting {0} frame ...'.format(fr))
              
                # print('  Segmenting {0} frame {1} ...'.format(fr, slice))
                start_seg_time = time.time()
                
                for slice in range(Z):
                    
                    image = imageOrg[:,:,slice]
                    
                    if image.ndim == 2:
                        image = np.expand_dims(image, axis=2)
                        
                        # Intensity rescaling
                        image = rescale_intensity(image, (1, 99))
                        # Pad the image size to be a factor of 16 so that the downsample and upsample procedures
                        # in the network will result in the same image size at each resolution level.
                        X2, Y2 = int(math.ceil(X / 16.0)) * 16, int(math.ceil(Y / 16.0)) * 16
                        x_pre, y_pre = int((X2 - X) / 2), int((Y2 - Y) / 2)
                        x_post, y_post = (X2 - X) - x_pre, (Y2 - Y) - y_pre
                        image = np.pad(image, ((x_pre, x_post), (y_pre, y_post), (0, 0)), 'constant')
                        
                        # Transpose the shape to NXYC
                        image = np.transpose(image, axes=(2, 0, 1)).astype(np.float32)
                        image = np.expand_dims(image, axis=-1)
                        
                        # Evaluate the networ
                        prob, pred = sess.run(['probE:0', 'predR:0'], feed_dict={'image:0': image, 'training:0': False})
                        
                        # Transpose and crop the segmentation to recover the original size
                        pred = np.transpose(pred, axes=(1, 2, 0))
                        
                        pred = pred[x_pre:x_pre + X, y_pre:y_pre + Y]
                        pred = np.squeeze(pred, axis=-1).astype(np.int16)
                        tmp[:,:,slice] = pred
                    
                seg_time = time.time() - start_seg_time
                print('  Segmentation time = {:3f}s'.format(seg_time))
                table_time += [seg_time]

                pred = tmp
        
                nim2 = nib.Nifti1Image(pred, nim.affine)
                nim2.header['pixdim'] = nim.header['pixdim']
                nib.save(nim2, '{0}/segs/seg_lvsa_{1}.nii.gz'.format(data_dir, fr))

        print('Average segmentation time = {:.3f}s per frame'.format(np.mean(table_time)))
