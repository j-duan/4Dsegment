import os
from multiprocessing import Pool
from functools import partial


def meshGeneration(subject_dir, template_dir, param_dir, tmps_dir, vtks_dir, dofs_dir): 
   
    os.system('rm {0}/*.txt'.format(subject_dir))  
    
    os.system('rm {0}/*'.format(vtks_dir))    
    
    os.system('rm {0}/*'.format(tmps_dir))    

    for fr in ['ED', 'ES']:
        
        ###########################################################################    
        # extract meshes of lvendo, lvepi, lvmyo, rv and rveip at ED and ES, respectively
        os.system('binarize '
                  '{0}/PHsegmentation_{2}.gipl '
                  '{1}/vtk_RV_{2}.nii.gz '
                  '4 4 255 0'
                  .format(subject_dir, tmps_dir, fr))
           
        os.system('mcubes '
                  '{0}/vtk_RV_{2}.nii.gz '
                  '{1}/RV_{2}.vtk '
                  '120 -blur 2'
                  .format(tmps_dir, vtks_dir, fr))
        
        os.system('binarize '
                  '{0}/PHsegmentation_{2}.gipl '
                  '{1}/vtk_RVepi_{2}.nii.gz '
                  '3 4 255 0'
                  .format(subject_dir, tmps_dir, fr))
        
        os.system('mcubes '
                  '{0}/vtk_RVepi_{2}.nii.gz '
                  '{1}/RVepi_{2}.vtk '
                  '120 -blur 2'
                  .format(tmps_dir, vtks_dir, fr))
        
        os.system('padding '
                  '{0}/PHsegmentation_{2}.gipl '
                  '{0}/PHsegmentation_{2}.gipl '
                  '{1}/vtk_LV_{2}.nii.gz '
                  '4 0'
                  .format(subject_dir, tmps_dir, fr))
        
        os.system('padding '
                  '{1}/vtk_LV_{2}.nii.gz '
                  '{0}/PHsegmentation_{2}.gipl '
                  '{1}/vtk_LV_{2}.nii.gz '
                  '3 0'
                  .format(subject_dir, tmps_dir, fr))
        
        os.system('binarize '
                  '{0}/PHsegmentation_{2}.gipl '
                  '{1}/vtk_LVendo_{2}.nii.gz '
                  '1 1 255 0'
                  .format(subject_dir, tmps_dir, fr))
        
        os.system('mcubes '
                  '{0}/vtk_LVendo_{2}.nii.gz '
                  '{1}/LVendo_{2}.vtk '
                  '120 -blur 2'
                  .format(tmps_dir, vtks_dir, fr))
        
        os.system('binarize '
                  '{0}/PHsegmentation_{2}.gipl '
                  '{1}/vtk_LVepi_{2}.nii.gz '
                  '1 2 255 0'
                  .format(subject_dir, tmps_dir, fr))
        
        os.system('mcubes '
                  '{0}/vtk_LVepi_{2}.nii.gz '
                  '{1}/LVepi_{2}.vtk '
                  '120 -blur 2'
                  .format(tmps_dir, vtks_dir, fr))
        
        os.system('binarize '
                  '{0}/PHsegmentation_{2}.gipl '
                  '{1}/vtk_LVmyo_{2}.nii.gz '
                  '2 2 255 0'
                  .format(subject_dir, tmps_dir, fr))
        
        os.system('mcubes '
                  '{0}/vtk_LVmyo_{2}.nii.gz '
                  '{1}/LVmyo_{2}.vtk '
                  '120 -blur 2'
                  .format(tmps_dir, vtks_dir, fr))
        
#        os.system('binarize '
#                  '{0}/seg_lvsa_SR_{2}.nii.gz '
#                  '{1}/vtk_RV_{2}.nii.gz '
#                  '4 4 255 0'
#                  .format(subject_dir, tmps_dir, fr))
#           
#        os.system('mcubes '
#                  '{0}/vtk_RV_{2}.nii.gz '
#                  '{1}/RV_{2}.vtk '
#                  '120 -blur 2'
#                  .format(tmps_dir, vtks_dir, fr))
#        
#        os.system('binarize '
#                  '{0}/seg_lvsa_SR_{2}.nii.gz '
#                  '{1}/vtk_RVepi_{2}.nii.gz '
#                  '3 4 255 0'
#                  .format(subject_dir, tmps_dir, fr))
#        
#        os.system('mcubes '
#                  '{0}/vtk_RVepi_{2}.nii.gz '
#                  '{1}/RVepi_{2}.vtk '
#                  '120 -blur 2'
#                  .format(tmps_dir, vtks_dir, fr))
#        
#        os.system('padding '
#                  '{0}/seg_lvsa_SR_{2}.nii.gz '
#                  '{0}/seg_lvsa_SR_{2}.nii.gz '
#                  '{1}/vtk_LV_{2}.nii.gz '
#                  '4 0'
#                  .format(subject_dir, tmps_dir, fr))
#        
#        os.system('padding '
#                  '{1}/vtk_LV_{2}.nii.gz '
#                  '{0}/seg_lvsa_SR_{2}.nii.gz '
#                  '{1}/vtk_LV_{2}.nii.gz '
#                  '3 0'
#                  .format(subject_dir, tmps_dir, fr))
#        
#        os.system('binarize '
#                  '{0}/seg_lvsa_SR_{2}.nii.gz '
#                  '{1}/vtk_LVendo_{2}.nii.gz '
#                  '1 1 255 0'
#                  .format(subject_dir, tmps_dir, fr))
#        
#        os.system('mcubes '
#                  '{0}/vtk_LVendo_{2}.nii.gz '
#                  '{1}/LVendo_{2}.vtk '
#                  '120 -blur 2'
#                  .format(tmps_dir, vtks_dir, fr))
#        
#        os.system('binarize '
#                  '{0}/seg_lvsa_SR_{2}.nii.gz '
#                  '{1}/vtk_LVepi_{2}.nii.gz '
#                  '1 2 255 0'
#                  .format(subject_dir, tmps_dir, fr))
#        
#        os.system('mcubes '
#                  '{0}/vtk_LVepi_{2}.nii.gz '
#                  '{1}/LVepi_{2}.vtk '
#                  '120 -blur 2'
#                  .format(tmps_dir, vtks_dir, fr))
#        
#        os.system('binarize '
#                  '{0}/seg_lvsa_SR_{2}.nii.gz '
#                  '{1}/vtk_LVmyo_{2}.nii.gz '
#                  '2 2 255 0'
#                  .format(subject_dir, tmps_dir, fr))
#        
#        os.system('mcubes '
#                  '{0}/vtk_LVmyo_{2}.nii.gz '
#                  '{1}/LVmyo_{2}.vtk '
#                  '120 -blur 2'
#                  .format(tmps_dir, vtks_dir, fr))
    
    ###############################################################################
    #use landmark to initialise the registration
#    os.system('prreg '
#              '{0}/landmarks.vtk '
#              '{1}/landmarks.vtk '
#              '-dofout {2}/landmarks.dof.gz'
#              .format(subject_dir, template_dir, dofs_dir))
    
    ###############################################################################
    for fr in ['ED', 'ES']:
    
#        os.system('msrreg 3 '
#                  '{0}/RV_{4}.vtk '
#                  '{0}/LVendo_{4}.vtk '
#                  '{0}/LVepi_{4}.vtk '
#                  '{1}/RV_{4}.vtk '
#                  '{1}/LVendo_{4}.vtk '
#                  '{1}/LVepi_{4}.vtk '
#                  '-dofin {2}/landmarks.dof.gz '
#                  '-dofout {3}/{4}.dof.gz '
#                  '-symmetric'
#                  .format(vtks_dir, template_dir, dofs_dir, tmps_dir, fr))
        
        os.system('msrreg 3 '
                  '{0}/RV_{3}.vtk '
                  '{0}/LVendo_{3}.vtk '
                  '{0}/LVepi_{3}.vtk '
                  '{1}/RV_{3}.vtk '
                  '{1}/LVendo_{3}.vtk '
                  '{1}/LVepi_{3}.vtk '
                  '-dofout {2}/{3}.dof.gz '
                  '-symmetric'
                  .format(vtks_dir, template_dir, tmps_dir, fr))
        
        os.system('msrreg 2 '
                  '{0}/LVendo_{3}.vtk '
                  '{0}/LVepi_{3}.vtk '
                  '{1}/LVendo_{3}.vtk '
                  '{1}/LVepi_{3}.vtk '
                  '-dofin {2}/{3}.dof.gz '
                  '-dofout {2}/lv_{3}_rreg.dof.gz '
                  '-symmetric'
                  .format(vtks_dir, template_dir, tmps_dir, fr))
        
        os.system('srreg '
                  '{0}/RV_{3}.vtk '
                  '{1}/RV_{3}.vtk '
                  '-dofin {2}/{3}.dof.gz '
                  '-dofout {2}/rv_{3}_rreg.dof.gz '
                  '-symmetric'
                  .format(vtks_dir, template_dir, tmps_dir, fr))
        
        ###########################################################################     
        os.system('ptransformation '
                  '{0}/RV_{2}.vtk '
                  '{0}/N_RV_{2}.vtk '
                  '-dofin {1}/rv_{2}_rreg.dof.gz'
                  .format(vtks_dir, tmps_dir, fr))
        
        os.system('ptransformation '
                  '{0}/RVepi_{2}.vtk '
                  '{0}/N_RVepi_{2}.vtk '
                  '-dofin {1}/rv_{2}_rreg.dof.gz'
                  .format(vtks_dir, tmps_dir, fr))
        
        os.system('ptransformation '
                  '{0}/LVendo_{2}.vtk '
                  '{0}/N_LVendo_{2}.vtk '
                  '-dofin {1}/lv_{2}_rreg.dof.gz'
                  .format(vtks_dir, tmps_dir, fr))
        
        os.system('ptransformation '
                  '{0}/LVepi_{2}.vtk '
                  '{0}/N_LVepi_{2}.vtk '
                  '-dofin {1}/lv_{2}_rreg.dof.gz'
                  .format(vtks_dir, tmps_dir, fr))
        
        os.system('ptransformation '
                  '{0}/LVmyo_{2}.vtk '
                  '{0}/N_LVmyo_{2}.vtk '
                  '-dofin {1}/lv_{2}_rreg.dof.gz'
                  .format(vtks_dir, tmps_dir, fr))
        
        os.system('transformation '
                  '{0}/vtk_RV_{1}.nii.gz '
                  '{0}/N_vtk_RV_{1}.nii.gz '
                  '-dofin {0}/lv_{1}_rreg.dof.gz '
                  '-invert'
                  .format(tmps_dir, fr))
        
        os.system('transformation '
                  '{0}/vtk_LV_{1}.nii.gz '
                  '{0}/N_vtk_LV_{1}.nii.gz '
                  '-dofin {0}/lv_{1}_rreg.dof.gz '
                  '-invert'
                  .format(tmps_dir, fr))
        
        ###########################################################################
        #affine
        os.system('areg '
                  '{0}/vtk_RV_{3}.nii.gz '
                  '{1}/N_vtk_RV_{3}.nii.gz '
                  '-dofout {1}/rv_{3}_areg.dof.gz '
                  '-parin {2}/segareg.txt'
                  .format(template_dir, tmps_dir, param_dir, fr))
        
        os.system('areg '
                  '{0}/vtk_LV_{3}.nii.gz '
                  '{1}/N_vtk_LV_{3}.nii.gz '
                  '-dofout {1}/lv_{3}_areg.dof.gz '
                  '-parin {2}/segareg.txt'
                  .format(template_dir, tmps_dir, param_dir, fr))
        
        #non-rigid
        os.system('nreg '
                  '{0}/vtk_RV_{3}.nii.gz '
                  '{1}/N_vtk_RV_{3}.nii.gz '
                  '-dofin {1}/rv_{3}_areg.dof.gz '
                  '-dofout {1}/rv_{3}_nreg.dof.gz '
                  '-parin {2}/segreg.txt'
                  .format(template_dir, tmps_dir, param_dir, fr))
        
        os.system('snreg '
                  '{0}/RV_{3}.vtk '
                  '{1}/N_RV_{3}.vtk '
                  '-dofin {2}/rv_{3}_nreg.dof.gz '
                  '-dofout {2}/rv{3}ds8.dof.gz '
                  '-ds 8 -symmetric'
                  .format(template_dir, vtks_dir, tmps_dir, fr))
        
        os.system('nreg '
                  '{0}/vtk_LV_{3}.nii.gz '
                  '{1}/N_vtk_LV_{3}.nii.gz '
                  '-dofin {1}/lv_{3}_areg.dof.gz '
                  '-dofout {1}/lv_{3}_nreg.dof.gz '
                  '-parin {2}/segreg.txt'
                  .format(template_dir, tmps_dir, param_dir, fr))
        
        os.system('msnreg 2 '
                  '{0}/LVendo_{3}.vtk '
                  '{0}/LVepi_{3}.vtk '
                  '{1}/N_LVendo_{3}.vtk '
                  '{1}/N_LVepi_{3}.vtk '
                  '-dofin {2}/lv_{3}_nreg.dof.gz '
                  '-dofout {2}/lv{3}final.dof.gz '
                  '-ds 4 -symmetric'
                  .format(template_dir, vtks_dir, tmps_dir, fr))
    
        # same number of points    
        os.system('cardiacsurfacemap '
                  '{0}/LVendo_{3}.vtk '
                  '{1}/N_LVendo_{3}.vtk '
                  '{2}/lv{3}final.dof.gz '
                  '{1}/F_LVendo_{3}.vtk'
                  .format(template_dir, vtks_dir, tmps_dir, fr))
    
        os.system('cardiacsurfacemap '
                  '{0}/LVepi_{3}.vtk '
                  '{1}/N_LVepi_{3}.vtk '
                  '{2}/lv{3}final.dof.gz '
                  '{1}/F_LVepi_{3}.vtk'
                  .format(template_dir, vtks_dir, tmps_dir, fr))
    
        os.system('ptransformation '
                  '{0}/LVmyo_{3}.vtk '
                  '{1}/F_LVmyo_{3}.vtk '
                  '-dofin {2}/lv{3}final.dof.gz'
                  .format(template_dir, vtks_dir, tmps_dir, fr))
        
        os.system('cardiacsurfacemap '
                  '{0}/RV_{3}.vtk '
                  '{1}/N_RV_{3}.vtk '
                  '{2}/rv{3}ds8.dof.gz '
                  '{1}/C_RV_{3}.vtk'
                  .format(template_dir, vtks_dir, tmps_dir, fr))
     
        ###########################################################################
        os.system('cp {0}/F_LVendo_{1}.vtk {0}/S_LVendo_{1}.vtk'.format(vtks_dir, fr))
        os.system('cp {0}/F_LVepi_{1}.vtk {0}/S_LVepi_{1}.vtk'.format(vtks_dir, fr))
        os.system('cp {0}/F_LVmyo_{1}.vtk {0}/S_LVmyo_{1}.vtk'.format(vtks_dir, fr))
        os.system('cp {0}/F_LVmyo_{1}.vtk {0}/C_LVmyo_{1}.vtk'.format(vtks_dir, fr))
        os.system('cp {0}/F_LVmyo_{1}.vtk {0}/W_LVmyo_{1}.vtk'.format(vtks_dir, fr))
        os.system('cp {0}/C_RV_{1}.vtk {0}/S_RV_{1}.vtk'.format(vtks_dir, fr))
        os.system('cp {0}/C_RV_{1}.vtk {0}/W_RV_{1}.vtk'.format(vtks_dir, fr))
        
        ###########################################################################
        # compute the quantities of the heart with respect to template
        os.system('cardiacwallthickness '
                  '{0}/F_LVendo_{1}.vtk '
                  '{0}/F_LVepi_{1}.vtk '
                  '-myocardium '
                  '{0}/W_LVmyo_{1}.vtk'
                  .format(vtks_dir, fr))
    
        os.system('cardiacenlargedistance '
                  '{0}/S_LVendo_{2}.vtk '
                  '{0}/S_LVepi_{2}.vtk '
                  '{1}/LVendo_{2}.vtk '
                  '{1}/LVepi_{2}.vtk '
                  '-myocardium '
                  '{0}/S_LVmyo_{2}.vtk'
                  .format(vtks_dir, template_dir, fr))
        
        os.system('DiscreteCurvatureEstimator '
                  '{0}/C_LVmyo_{1}.vtk '
                  '{0}/FC_LVmyo_{1}.vtk'
                  .format(vtks_dir, fr))
        
        os.system('cardiaccurvature '
                  '{0}/FC_LVmyo_{1}.vtk '
                  '{0}/C_LVmyo_{1}.vtk '
                  '-smooth 64'
                  .format(vtks_dir, fr))
        
        os.system('DiscreteCurvatureEstimator '
                  '{0}/C_RV_{1}.vtk '
                  '{0}/FC_RV_{1}.vtk'
                  .format(vtks_dir, fr))
        
        os.system('cardiaccurvature '
                  '{0}/FC_RV_{1}.vtk '
                  '{0}/C_RV_{1}.vtk '
                  '-smooth 64'
                  .format(vtks_dir, fr))
        
        os.system('sevaluation '
                  '{0}/S_RV_{2}.vtk '
                  '{1}/RV_{2}.vtk '
                  '-scalar '
                  '-signed'
                  .format(vtks_dir, template_dir, fr))
        
        os.system('cardiacwallthickness '
                  '{0}/W_RV_{1}.vtk '
                  '{0}/N_RVepi_{1}.vtk'
                  .format(vtks_dir, fr))
        
        ###########################################################################
#        os.system('vtk2txt {0}/C_RV_{1}.vtk {2}/rv_{1}_curvature.txt'.format(vtks_dir, fr, subject_dir))
#        os.system('vtk2txt {0}/W_RV_{1}.vtk {2}/rv_{1}_wallthickness.txt'.format(vtks_dir, fr, subject_dir))
#        os.system('vtk2txt {0}/S_RV_{1}.vtk {2}/rv_{1}_signeddistances.txt'.format(vtks_dir, fr, subject_dir))
#        os.system('vtk2txt {0}/W_LVmyo_{1}.vtk {2}/lv_myo{1}_wallthickness.txt'.format(vtks_dir, fr, subject_dir))
#        os.system('vtk2txt {0}/C_LVmyo_{1}.vtk {2}/lv_myo{1}_curvature.txt'.format(vtks_dir, fr, subject_dir))
#        os.system('vtk2txt {0}/S_LVmyo_{1}.vtk {2}/lv_myo{1}_signeddistances.txt'.format(vtks_dir, fr, subject_dir))
        if fr == 'ED':
            fr_ = 'ed'
            os.system('vtk2txt {0}/C_RV_{1}.vtk {2}/rv_{3}_curvature.txt'.format(vtks_dir, fr, subject_dir, fr_))
            os.system('vtk2txt {0}/W_RV_{1}.vtk {2}/rv_{3}_wallthickness.txt'.format(vtks_dir, fr, subject_dir, fr_))
            os.system('vtk2txt {0}/S_RV_{1}.vtk {2}/rv_{3}_signeddistances.txt'.format(vtks_dir, fr, subject_dir, fr_))
            os.system('vtk2txt {0}/W_LVmyo_{1}.vtk {2}/lv_myo{3}_wallthickness.txt'.format(vtks_dir, fr, subject_dir, fr_))
            os.system('vtk2txt {0}/C_LVmyo_{1}.vtk {2}/lv_myo{3}_curvature.txt'.format(vtks_dir, fr, subject_dir, fr_))
            os.system('vtk2txt {0}/S_LVmyo_{1}.vtk {2}/lv_myo{3}_signeddistances.txt'.format(vtks_dir, fr, subject_dir, fr_))
        if fr == 'ES':
            fr_ = 'es'
            os.system('vtk2txt {0}/C_RV_{1}.vtk {2}/rv_{3}_curvature.txt'.format(vtks_dir, fr, subject_dir, fr_))
            os.system('vtk2txt {0}/W_RV_{1}.vtk {2}/rv_{3}_wallthickness.txt'.format(vtks_dir, fr, subject_dir, fr_))
            os.system('vtk2txt {0}/S_RV_{1}.vtk {2}/rv_{3}_signeddistances.txt'.format(vtks_dir, fr, subject_dir, fr_))
            os.system('vtk2txt {0}/W_LVmyo_{1}.vtk {2}/lv_myo{3}_wallthickness.txt'.format(vtks_dir, fr, subject_dir, fr_))
            os.system('vtk2txt {0}/C_LVmyo_{1}.vtk {2}/lv_myo{3}_curvature.txt'.format(vtks_dir, fr, subject_dir, fr_))
            os.system('vtk2txt {0}/S_LVmyo_{1}.vtk {2}/lv_myo{3}_signeddistances.txt'.format(vtks_dir, fr, subject_dir, fr_))
  
      
def apply_PC(subject, data_dir, param_dir, template_dir, mirtk):
    
    print('  co-registering {0}'.format(subject))    
    
    subject_dir = os.path.join(data_dir, subject)
        
    if os.path.isdir(subject_dir):
        
        tmps_dir = '{0}/tmps'.format(subject_dir)

        vtks_dir = '{0}/vtks'.format(subject_dir)

        dofs_dir = '{0}/dofs'.format(subject_dir)

        meshGeneration(subject_dir, template_dir, param_dir, tmps_dir, vtks_dir, dofs_dir)
        
        print('  finish generating meshes from segmentations in {0}'.format(subject))
        
    else:  
        print('  {0} is not a valid directory, do nothing'.format(subject_dir))


def meshCoregstration(dir_0, dir_2, dir_3, coreNo, parallel, mirtk):
               
    if parallel:
    
        print('Generate meshes from segmentations running on {0} cores'.format(coreNo))
        
        pool = Pool(processes = coreNo) 
        
        # partial only in Python 2.7+
        pool.map(partial(apply_PC, 
                         data_dir=dir_0,  
                         param_dir=dir_2, 
                         template_dir=dir_3,
                         mirtk=mirtk), 
                         sorted(os.listdir(dir_0)))       
                
    else:
        
        print('Generate meshes from segmentations running subsequently')
                
        data_dir, param_dir, template_dir = dir_0, dir_2, dir_3
                                     
        for subject in sorted(os.listdir(data_dir)):
            
            print('  co-registering {0}'.format(subject))    
            
            subject_dir = os.path.join(data_dir, subject)

            if not os.path.isdir(subject_dir):
                
                print('  {0} is not a valid folder, Skip'.format(subject_dir))
                
                continue 
                   
            tmps_dir = '{0}/tmps'.format(subject_dir)

            vtks_dir = '{0}/vtks'.format(subject_dir)

            dofs_dir = '{0}/dofs'.format(subject_dir)

            meshGeneration(subject_dir, template_dir, param_dir, tmps_dir, vtks_dir, dofs_dir)
            
            print('  finish generating meshes from segmentations in {0}'.format(subject))