#!/usr/bin/python
import os, glob
from multiprocessing import Pool
from functools import partial


# Perform motion tracking for cine MR
def track_cine(data_dir, par_dir, tamplate_dir):
    
    motion_dir = os.path.join(data_dir, 'motion')
    if os.path.exists(motion_dir):
       os.system('rm -r {0}'.format(motion_dir))
       os.mkdir(motion_dir)
    else:
       os.mkdir(motion_dir)

    # Split 4D nifti into time phases
    os.system('splitvolume '
              '{0}/lvsa_.nii.gz '
              '{1}/lvsa_ '
              '-sequence'
              .format(data_dir, motion_dir))

    n_frame = len(glob.glob('{0}/lvsa_??.nii.gz'.format(motion_dir)))

    # Inter-frame motion estimation
    for fr in range(1, n_frame):
        target = '{0}/lvsa_{1:02d}.nii.gz'.format(motion_dir, fr-1)
        source = '{0}/lvsa_{1:02d}.nii.gz'.format(motion_dir, fr)
        par = '{0}/ffd_motion.cfg'.format(par_dir)
        dof = '{0}/ffd_{1:02d}_to_{2:02d}.dof.gz'.format(motion_dir, fr-1, fr)

        if not os.path.exists(dof):
            os.system('mirtk register '
                      '{0} '
                      '{1} '
                      '-parin {2} '
                      '-dofout {3}'
                      .format(target, source, par, dof))

    # Compose inter-frame transformation fields
    for fr in range(2, n_frame):
        dofs = ''
        for k in range(1, fr+1):
            dof = '{0}/ffd_{1:02d}_to_{2:02d}.dof.gz'.format(motion_dir, k-1, k)
            dofs += dof + ' '
            dof_out = '{0}/ffd_comp_00_to_{1:02d}.dof.gz'.format(motion_dir, fr)
            if not os.path.exists(dof_out):
                os.system('mirtk compose-dofs '
                          '{0} '
                          '{1}'
                          .format(dofs, dof_out))

    # Refine motion fields
    # Composition of inter-frame motion fields can lead to accumulative errors. At this step, we refine the motion fields
    # by re-registering the n-th frame with the ED frame.
    for fr in range(2, n_frame):
        target = '{0}/lvsa_00.nii.gz'.format(motion_dir)
        source = '{0}/lvsa_{1:02d}.nii.gz'.format(motion_dir, fr)
        par = '{0}/ffd_refine.cfg'.format(par_dir)
        dofin = '{0}/ffd_comp_00_to_{1:02d}.dof.gz'.format(motion_dir, fr)
        dof = '{0}/ffd_00_to_{1:02d}.dof.gz'.format(motion_dir, fr)
        if not os.path.exists(dof):
            os.system('mirtk register '
                      '{0} '
                      '{1} '
                      '-parin {2} '
                      '-dofin {3} '
                      '-dofout {4}'
                      .format(target, source, par, dofin, dof))

    # Obtain the RV mesh with the same number of points as the template mesh
    os.system('srreg '
              '{2}/vtks/RV_ED.vtk '
              '{0}/RVendo_ED.vtk '
              '-dofout {1}/RV_srreg.dof.gz '
              '-symmetric'
              .format(tamplate_dir, motion_dir, data_dir))
    
    os.system('mirtk transform-points '
              '{0}/RVendo_ED.vtk '
              '{1}/RV_ED_srreg.vtk '
              '-dofin {1}/RV_srreg.dof.gz '
              '-invert'
              .format(tamplate_dir, motion_dir))
    
    os.system('sareg '
              '{0}/RV_ED_srreg.vtk '
              '{1}/vtks/RV_ED.vtk '
              '-dofout {0}/RV_sareg.dof.gz '
              '-symmetric'
              .format(motion_dir, data_dir))
    
    os.system('snreg '
              '{0}/RV_ED_srreg.vtk '
              '{1}/vtks/RV_ED.vtk '
              '-dofin {0}/RV_sareg.dof.gz '
              '-dofout {0}/RV_snreg.dof.gz '
              '-ds 20 -symmetric'
              .format(motion_dir, data_dir))
    
    os.system('mirtk transform-points '
              '{0}/RV_ED_srreg.vtk '
              '{0}/RV_fr00.vtk '
              '-dofin {0}/RV_snreg.dof.gz'
              .format(motion_dir))

    # Transform the mesh
    for fr in range(1, n_frame):
        os.system('mirtk transform-points '
                  '{0}/RV_fr00.vtk '
                  '{0}/RV_fr{1:02d}.vtk '
                  '-dofin {0}/ffd_00_to_{1:02d}.dof.gz'
                  .format(motion_dir, fr))
     
    # Convert vtks to text files
    for fr in range(0, n_frame):
        os.system('vtk2txt '
                  '{0}/RV_fr{1:02d}.vtk '
                  '{0}/RV_fr{1:02d}.txt'
                  .format(motion_dir, fr))


def apply_PC(subject, data_dir):
    
    print('  decimateing {0}'.format(subject))    
    
    subject_dir = os.path.join(data_dir, subject)
        
    motion_dir = os.path.join(subject_dir, 'motion')
            
    os.system('mirtk decimate-surface '
              '{0}/RV_fr00.vtk '
              '{0}/RV_fr00_new.vtk '
              '-reduceby 98.9 '
              '-preservetopology on'
              .format(motion_dir))
    
    os.system('snreg '
              '{0}/RV_fr00_new.vtk '
              '{0}/RV_fr00.vtk '
              '-dofout {0}/transformation.vtk '
              '-epsilon 0.0001'
              .format(motion_dir))
   
    os.system('mirtk transform-points '
              '{0}/RV_fr00_new.vtk '
              '{0}/RV_fr00_new_new.vtk '
              '-dofin {0}/transformation.vtk'
              .format(motion_dir))
    
    os.system('mirtk match-points '
              '{0}/RV_fr00_new_new.vtk '
              '{0}/RV_fr00.vtk '
              '-corout {0}/matchedpointsnew.txt'
              .format(motion_dir))


def decimate(dir_0, coreNo, parallel):
               
    if parallel:
    
        print('decimationg running on {0} cores'.format(coreNo))
        
        pool = Pool(processes = coreNo) 
        
        # partial only in Python 2.7+
#        pool.map(partial(apply_PC, sorted(os.listdir(dir_0))))
        
        pool.map(partial(apply_PC, data_dir=dir_0), sorted(os.listdir(dir_0)))    
                
    else:
        
        print('decimation running subsequently')
                
        data_dir = dir_0
         
        i = 0
                                     
        for subject in sorted(os.listdir(data_dir)):
            
            if i == 0:
            
                subject_dir = os.path.join(data_dir, subject)
    
                if not os.path.isdir(subject_dir):
                    
                    print('  {0} is not a valid folder, Skip'.format(subject_dir))
                    
                    continue 
                       
                print('  decimating {0}'.format(subject))  
                
                motion_dir = os.path.join(subject_dir, 'motion')
                
                os.system('mirtk decimate-surface '
                          '{0}/RV_fr00.vtk '
                          '{0}/RV_fr00_new.vtk '
                          '-reduceby 98.9 '
                          '-preservetopology on'
                          .format(motion_dir))
                
                os.system('snreg '
                          '{0}/RV_fr00_new.vtk '
                          '{0}/RV_fr00.vtk '
                          '-dofout {0}/transformation.vtk '
                          '-epsilon 0.0001'
                          .format(motion_dir))
           
                os.system('mirtk transform-points '
                          '{0}/RV_fr00_new.vtk '
                          '{0}/RV_fr00_new_new.vtk '
                          '-dofin {0}/transformation.vtk'
                          .format(motion_dir))
                
                os.system('mirtk match-points '
                          '{0}/RV_fr00_new_new.vtk '
                          '{0}/RV_fr00.vtk '
                          '-corout {1}/matchedpointsnew.txt'
                          .format(motion_dir, data_dir))
             
                i = 1 
                
            print('  finish decimation in {0}'.format(subject))
