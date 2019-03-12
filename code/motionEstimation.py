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


def apply_PC(subject, data_dir, param_dir, template_dir):
    
    print('  co-registering {0}'.format(subject))    
    
    subject_dir = os.path.join(data_dir, subject)
        
    if os.path.isdir(subject_dir):
        
        track_cine(subject_dir, param_dir, template_dir)
        
        print('  finish motion tracking in subject {0}'.format(subject))
        
    else:  
        print('  {0} is not a valid directory, do nothing'.format(subject_dir))


def motionTracking(dir_0, dir_2, dir_3, coreNo, parallel):
               
    if parallel:
    
        print('Motion tracking running on {0} cores'.format(coreNo))
        
        pool = Pool(processes = coreNo) 
        
        # partial only in Python 2.7+
        pool.map(partial(apply_PC, 
                         data_dir=dir_0,  
                         param_dir=dir_2, 
                         template_dir=dir_3), 
                         sorted(os.listdir(dir_0)))       
                
    else:
        
        print('Motion tracking from segmentations running subsequently')
                
        data_dir, param_dir, template_dir = dir_0, dir_2, dir_3
                                     
        for subject in sorted(os.listdir(data_dir)):
            
            subject_dir = os.path.join(data_dir, subject)

            if not os.path.isdir(subject_dir):
                
                print('  {0} is not a valid folder, Skip'.format(subject_dir))
                
                continue 
                   
            print('  motion tracking {0}'.format(subject))  
            
            track_cine(subject_dir, param_dir, template_dir)
            
            print('  finish motion tracking in {0}'.format(subject))
