import os
import numpy as np
from multiprocessing import Pool
from functools import partial
from image_utils import *  

def output3DRefinement(atlases, DLSeg, param_dir, tmps_dir, dofs_dir, subject_dir, savedInd, fr, mirtk):
   
    segstring = ''
    ind = 0
    atlasUsedNo = len(atlases)
        
    for i in range(atlasUsedNo):
         
        if mirtk:
            os.system('mirtk register '
                      '{0} '
                      '{1} '
                      '-parin {2}/ffd_label_1.cfg ' 
                      '-dofin {3}/shapelandmarks_{4}.dof.gz '
                      '-dofout {3}/shapeffd_{5}_{6}.dof.gz' 
                      .format(DLSeg, atlases[i], param_dir, dofs_dir, savedInd[i], i, fr))
            
            os.system('mirtk transform-image '
                      '{0} '
                      '{1}/seg_lvsa_SR_{4}_{5}.nii.gz ' 
                      '-dofin {2}/shapeffd_{4}_{5}.dof.gz '
                      '-target {3}/lvsa_SR_{5}.nii.gz -interp NN'  
                      .format(atlases[i], tmps_dir, dofs_dir, subject_dir, i, fr)) 

        else:
            os.system('nreg '
                      '{0} '
                      '{1} '
                      '-parin {2}/segreg.txt ' 
                      '-dofin {3}/shapelandmarks_{4}.dof.gz '
                      '-dofout {3}/shapeffd_{5}_{6}.dof.gz' 
                      .format(DLSeg, atlases[i], param_dir, dofs_dir, savedInd[i], i, fr))
                          
            os.system('transformation '
                      '{0} '
                      '{1}/seg_lvsa_SR_{4}_{5}.nii.gz ' 
                      '-dofin {2}/shapeffd_{4}_{5}.dof.gz '
                      '-target {3}/lvsa_SR_{5}.nii.gz -nn' 
                      .format(atlases[i], tmps_dir, dofs_dir, subject_dir, i, fr))    

        segstring += '{0}/seg_lvsa_SR_{1}_{2}.nii.gz '.format(tmps_dir, i, fr)
        
        ind += 1
        
    # apply label fusion    
    os.system('combineLabels {0}/seg_lvsa_SR_{1}.nii.gz {2} {3}'.format(subject_dir, fr, ind, segstring))
    
    
def apply_PC(subject, data_dir, param_dir, atlases_list, landmarks_list, mirtk):
       
    print('  registering {0}'.format(subject))    
    
    subject_dir = os.path.join(data_dir, subject)
        
    if os.path.isdir(subject_dir):
        
        tmps_dir = '{0}/tmps'.format(subject_dir)

        dofs_dir = '{0}/dofs'.format(subject_dir)
    
        segs_dir = '{0}/segs'.format(subject_dir)
        
        sizes_dir = '{0}/sizes'.format(subject_dir)
        
        subject_landmarks = '{0}/landmarks.vtk'.format(subject_dir)
                                  
        for fr in ['ED', 'ES']:
                
            DLSeg = '{0}/seg_lvsa_{1}.nii.gz'.format(segs_dir, fr)
            
            if not os.path.exists(DLSeg):
                
                print(' segmentation {0} does not exist. Skip.'.format(DLSeg))
                
                continue
                 
            topSimilarAtlases_list, savedInd = topSimilarAtlasShapeSelection(atlases_list[fr], landmarks_list[fr], 
                                               subject_landmarks, tmps_dir, dofs_dir, DLSeg, param_dir, 3) 
                      
            formHighResolutionImg(subject_dir, fr)
                
            output3DRefinement(topSimilarAtlases_list, DLSeg, param_dir, tmps_dir, dofs_dir, subject_dir, savedInd, fr, mirtk)
                   
            if mirtk:
                
                refineFusionResults(subject_dir, 'seg_lvsa_SR_{0}.nii.gz'.format(fr), 2)
            
#                clearBaseManbrance(subject_dir, 'seg_lvsa_SR_{0}.nii.gz'.format(fr)) 
#            
#                refineFusionResults(subject_dir, 'seg_lvsa_SR_{0}.nii.gz'.format(fr), 2) 
                
            else:
                
                refineFusionResults(subject_dir, 'seg_lvsa_SR_{0}.nii.gz'.format(fr), 2) 
            
            convertImageSegment(subject_dir, fr)
            
            outputVolumes(subject_dir, data_dir, subject, fr)
            
            moveVolumes(subject_dir, sizes_dir, fr)
                
        print('  finish 3D nonrigid-registering one subject {}'.format(subject))
    
    else:  
        print('  {0} is not a valid directory, do nothing'.format(subject_dir))
        
       
def multiatlasreg3D(dir_0, dir_1, dir_2, coreNo, parallel, mirtk):
               
    print('Select all the shape atlases for 3D multi-atlas registration')
    
    atlases_list, landmarks_list = allAtlasShapeSelection(dir_1)

    if parallel:
    
        print('Start 3D multi-atlas registration and program running on {0} cores'.format(coreNo))
        
        pool = Pool(processes = coreNo) 
        
        # partial only in Python 2.7+
        pool.map(partial(apply_PC, 
                         data_dir=dir_0,  
                         param_dir=dir_2, 
                         atlases_list=atlases_list, 
                         landmarks_list=landmarks_list,
                         mirtk=mirtk), 
                         sorted(os.listdir(dir_0)))       
                
    else:
        
        print('Start 3D multi-atlas registration and program running subsequently')
                
        data_dir, param_dir = dir_0, dir_2
                                     
        for subject in sorted(os.listdir(data_dir)):
            
            print('  registering {0}'.format(subject))   
            
            subject_dir = os.path.join(data_dir, subject)

            if not os.path.isdir(subject_dir):
                
                print('  {0} is not a valid folder, Skip'.format(subject_dir))
                
                continue 
                   
            tmps_dir = '{0}/tmps'.format(subject_dir)

            dofs_dir = '{0}/dofs'.format(subject_dir)
    
            segs_dir = '{0}/segs'.format(subject_dir)
            
            sizes_dir = '{0}/sizes'.format(subject_dir)
            
            subject_landmarks = '{0}/landmarks.vtk'.format(subject_dir)
            
            for fr in ['ED', 'ES']:
                    
                DLSeg = '{0}/seg_lvsa_{1}.nii.gz'.format(segs_dir, fr)
                
                if not os.path.exists(DLSeg):
                
                    print(' segmentation {0} does not exist. Skip.'.format(DLSeg))
                
                    continue
                 
                topSimilarAtlases_list, savedInd = topSimilarAtlasShapeSelection(atlases_list[fr], landmarks_list[fr], 
                                                   subject_landmarks, tmps_dir, dofs_dir, DLSeg, param_dir, 3) 
                      
                formHighResolutionImg(subject_dir, fr)
                
                output3DRefinement(topSimilarAtlases_list, DLSeg, param_dir, tmps_dir, dofs_dir, subject_dir, savedInd, fr, mirtk)
                
                if mirtk:
                    
                    refineFusionResults(subject_dir, 'seg_lvsa_SR_{0}.nii.gz'.format(fr), 2) 
            
#                    clearBaseManbrance(subject_dir, 'seg_lvsa_SR_{0}.nii.gz'.format(fr)) 
#            
#                    refineFusionResults(subject_dir, 'seg_lvsa_SR_{0}.nii.gz'.format(fr), 2) 
                else:
                    
                    refineFusionResults(subject_dir, 'seg_lvsa_SR_{0}.nii.gz'.format(fr), 2) 
            
                convertImageSegment(subject_dir, fr)
            
                outputVolumes(subject_dir, data_dir, subject, fr)
                
                moveVolumes(subject_dir, sizes_dir, fr)
                                
            print('  finish 3D nonrigid-registering one subject {}'.format(subject))
