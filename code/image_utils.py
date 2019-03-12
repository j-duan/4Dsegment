import os
import numpy as np
import nibabel as nib
from numpy.linalg import inv

def rescale_intensity(image, thres=(1.0, 99.0)):
    """ Rescale the image intensity to the range of [0, 1] """
    val_l, val_h = np.percentile(image, thres)
    image2 = image
    image2[image < val_l] = val_l
    image2[image > val_h] = val_h
    image2 = (image2.astype(np.float32) - val_l) / (val_h - val_l + 1e-6)
    return image2


def imagePreprocessing(originalNii, data_dir, atlas_dir):
     
    os.system('headertool '
              '{0} '
              '{1}/lvsa_.nii.gz '
              '-reset'
              .format(originalNii, data_dir))

    os.system('temporalalign '
              '{0}/temporal.gipl '
              '{1}/lvsa_.nii.gz '
              '{1}/lvsa_.nii.gz ' 
              '-St1 0 '
              '-St2 0 '
              '-Et1 1 '
              '-Et2 1'
              .format(atlas_dir, data_dir))

    os.system('autocontrast '
              '{0}/lvsa_.nii.gz '
              '{0}/lvsa_.nii.gz'
              .format(data_dir))
        
    os.system('cardiacphasedetection '
              '{0}/lvsa_.nii.gz '
              '{0}/lvsa_ED.nii.gz '
              '{0}/lvsa_ES.nii.gz'
              .format(data_dir))
    
    print('  Image preprocessing is done ...')


def clearBaseManbrance(data_dir, output_name):

    nim = nib.load('{0}/{1}'.format(data_dir, output_name))
    seg = nim.get_data()
    if seg.ndim == 4:
        seg = np.squeeze(seg, axis=-1).astype(np.int16)
        
    # find the last slice that has RV component 
    rv = (seg == 4).astype(np.int16)   
    for i in reversed(range(seg.shape[2])):
        if np.sum(rv[:,:,i]) > 0: 
            break
    lastAppearSlice = i 
    
    # create a 2D mask that average the last 12 slice of RV which is robust to noise
    slicesUsed = 12
    tmp = np.zeros((seg.shape[0], seg.shape[1]), dtype=np.int16)
    for j in range(slicesUsed):
        tmp = tmp + rv[:,:,lastAppearSlice-j]
    tmp = (tmp > 0).astype(np.int16)   
    
    # create a volume mask used to remove the base manbrance caused by RV myocardium
    mask = np.ones((seg.shape[2], seg.shape[0], seg.shape[1]), dtype=np.int16)
    mask[lastAppearSlice-slicesUsed:,:,:] = 1 - tmp
    mask = np.transpose(mask, axes=(1, 2, 0))
    seg = np.multiply(seg, mask)
    
    # fill the gap/hole of RV 
    flat = False
    if flat:
        seg = np.transpose(seg, axes=(2, 0, 1))
        seg[lastAppearSlice-slicesUsed:lastAppearSlice-3,:,:] = seg[lastAppearSlice-slicesUsed:lastAppearSlice-3,:,:] + 4*tmp
        seg = np.transpose(seg, axes=(1, 2, 0))
    else:
        seg[:,:,lastAppearSlice-slicesUsed:] = seg[:,:,lastAppearSlice-slicesUsed:] + 4*rv[:,:,lastAppearSlice-slicesUsed:]
    
    ###############################################################################
    # find the last slice that has LV component 
    lv = (seg == 1).astype(np.int16)   
    for i in reversed(range(seg.shape[2])):
        if np.sum(lv[:,:,i]) > 0: 
            break
    lastAppearSlice = i 
    
    # create a 2D mask that average the last 5 slice of RV which is robust to noise
    slicesUsed = 10
    tmp = np.zeros((seg.shape[0], seg.shape[1]), dtype=np.int16)
    for j in range(slicesUsed):
        tmp = tmp + lv[:,:,lastAppearSlice-j]
    tmp = (tmp > 0).astype(np.int16)   
    
    # create a volume mask used to remove the manbrance caused by LV myocardium
    mask = np.ones((seg.shape[2], seg.shape[0], seg.shape[1]), dtype=np.int16)
    mask[lastAppearSlice-slicesUsed:,:,:] = 1 - tmp
    mask = np.transpose(mask, axes=(1, 2, 0))
    seg = np.multiply(seg, mask)
    
    # fill the gap/hole of LV 
    flat = True
    if flat:
        seg = np.transpose(seg, axes=(2, 0, 1))
        seg[lastAppearSlice-slicesUsed:lastAppearSlice-1,:,:] = seg[lastAppearSlice-slicesUsed:lastAppearSlice-1,:,:] + tmp
        seg = np.transpose(seg, axes=(1, 2, 0))
    else:
        seg[:,:,lastAppearSlice-slicesUsed:] = seg[:,:,lastAppearSlice-slicesUsed:] + lv[:,:,lastAppearSlice-slicesUsed:]

    # save the result
    nim2 = nib.Nifti1Image(seg, nim.affine)
    nim2.header['pixdim'] = nim.header['pixdim']
    nib.save(nim2, '{0}/{1}'.format(data_dir, output_name))


def removeSegsAboveBase(data_dir, output_name):

    # Read segmentations
    nim = nib.load('{0}/{1}'.format(data_dir, output_name))
    seg = nim.get_data()
    if seg.ndim == 4:
        seg = np.squeeze(seg, axis=-1).astype(np.int16)
    os.system('vtk2txt {0}/landmarks.vtk {0}/landmarks.txt'.format(data_dir)) 
    
    # convert txt file into matrix
    file = open('{0}/landmarks.txt'.format(data_dir), 'r') 
    A = file.read()
    tmp = np.zeros(18)  
    i, c = 0, 0
    for p in range(len(A)):
        if A[p] == ' ' or A[p] == '\n':
            tmp[i] = np.float32(A[c:p])
            i = i + 1
            c = p + 1;
    tmp = np.reshape(tmp,(6,3))        
    landmarks = np.ones((6,4)) 
    landmarks[:,:-1] = tmp
    landmarks = np.transpose(landmarks).astype(np.float32)           
    os.system('rm {0}/landmarks.txt'.format(data_dir))    
       
    # map world coordinate system to image pixel position
    pixelsPositions = np.ceil(np.dot(inv(nim.affine),landmarks)).astype(np.int16) 
    pixelsPositions = np.delete(pixelsPositions, (-1), axis=0)
    pixelsPositions = np.transpose(pixelsPositions).astype(np.int16) 
    
    if output_name[9:11]=='ED':
        seg[:,:,pixelsPositions[5,2]+1:] = 0
    else:
        seg[:,:,pixelsPositions[5,2]:] = 0
    
    nim2 = nib.Nifti1Image(seg, nim.affine)
    nim2.header['pixdim'] = nim.header['pixdim']
    nib.save(nim2, '{0}/{1}'.format(data_dir, output_name))
    

def formHighResolutionImg(subject_dir, fr): 
    
    os.system('resample ' 
              '{0}/lvsa_{1}.nii.gz '
              '{0}/lvsa_SR_{1}.nii.gz '
              '-size 1.25 1.25 2'
              .format(subject_dir, fr))
        
#    os.system('enlarge_image '
#              '{0}/lvsa_SR_{1}.nii.gz '
#              '{0}/lvsa_SR_{1}.nii.gz '
#              '-z 20 '
#              '-value 0'
#              .format(subject_dir, fr))

    
def convertImageSegment(data_dir, fr):
   
    os.system('convert '
              '{0}/seg_lvsa_SR_{1}.nii.gz '
              '{0}/PHsegmentation_{1}.gipl'
              .format(data_dir, fr))
    
    os.system('cp '
              '{0}/lvsa_SR_{1}.nii.gz '
              '{0}/lvsa_{1}_enlarged_SR.nii.gz'
              .format(data_dir, fr))
    
    
def outputVolumes(subject_dir, data_dir, subject, fr):
     
    os.system('rm '
              '{0}/{1}_{2}.txt'
              .format(data_dir, subject, fr))
    
    os.system('cardiacvolumecount '
              '{0}/PHsegmentation_{3}.gipl 1 '
              '-output '
              '{1}/{2}_{3}.txt'
              .format(subject_dir, data_dir, subject, fr))
    
    os.system('cardiacvolumecount '
              '{0}/PHsegmentation_{3}.gipl 2 '
              '-output '
              '{1}/{2}_{3}.txt '
              '-scale 1.05'
              .format(subject_dir, data_dir, subject, fr))
    
    os.system('cardiacvolumecount '
              '{0}/PHsegmentation_{3}.gipl 4 '
              '-output '
              '{1}/{2}_{3}.txt'
              .format(subject_dir, data_dir, subject, fr))
    
    os.system('cardiacvolumecount '
              '{0}/PHsegmentation_{3}.gipl 3 '
              '-output '
              '{1}/{2}_{3}.txt '
              '-scale 1.05'
              .format(subject_dir, data_dir, subject, fr))
    
    
def moveVolumes(subject_dir, sizes_dir, fr):
     
    os.system('cp '
              '{0}/lvsa_{2}.nii.gz '
              '{1}/lvsa_{2}.nii.gz'
              .format(subject_dir, sizes_dir, fr))
    
    os.system('rm '
              '{0}/lvsa_{1}.nii.gz '
              .format(subject_dir, fr))
    
    os.system('cp '
              '{0}/seg_lvsa_{2}.nii.gz '
              '{1}/2D_segmentation_{2}.nii.gz'
              .format(subject_dir, sizes_dir, fr))
    
    os.system('rm '
              '{0}/seg_lvsa_{1}.nii.gz '
              .format(subject_dir, fr))
    
    os.system('cp '
              '{0}/lvsa_SR_{2}.nii.gz '
              '{1}/lvsa_{2}_SR.nii.gz'
              .format(subject_dir, sizes_dir, fr))
    
    os.system('rm '
              '{0}/lvsa_SR_{1}.nii.gz '
              .format(subject_dir, fr))
    
    os.system('cp '
              '{0}/seg_lvsa_SR_{2}.nii.gz '
              '{1}/3D_segmentation_{2}.nii.gz'
              .format(subject_dir, sizes_dir, fr))
    
    os.system('rm '
              '{0}/seg_lvsa_SR_{1}.nii.gz '
              .format(subject_dir, fr))

    
def refineFusionResults(data_dir, output_name, alfa): 
    
    ##########################################
    os.system('binarize '
              '{0}/{1} '
              '{0}/tmps/hrt.nii.gz '
              '1 4 255 0'
              .format(data_dir, output_name))
    
    os.system('blur '
              '{0}/tmps/hrt.nii.gz '
              '{0}/tmps/hrt.nii.gz '
              '{1}'
              .format(data_dir, alfa))
    
    os.system('threshold '
              '{0}/tmps/hrt.nii.gz '
              '{0}/tmps/hrt.nii.gz '
              '130'
              .format(data_dir))
    
    ##########################################
    os.system('binarize '
              '{0}/{1} '
              '{0}/tmps/rvendo.nii.gz '
              '4 4 255 0'
              .format(data_dir, output_name))
    
    os.system('blur '
              '{0}/tmps/rvendo.nii.gz '
              '{0}/tmps/rvendo.nii.gz '
              '{1}'
              .format(data_dir, alfa))
    
    os.system('threshold '
              '{0}/tmps/rvendo.nii.gz '
              '{0}/tmps/rvendo.nii.gz '
              '130'
              .format(data_dir))
    
    ##########################################
    os.system('binarize '
              '{0}/{1} '
              '{0}/tmps/lvepi.nii.gz '
              '1 2 255 0'
              .format(data_dir, output_name))
       
    os.system('blur '
              '{0}/tmps/lvepi.nii.gz '
              '{0}/tmps/lvepi.nii.gz '
              '{1}'
              .format(data_dir, alfa))
    
    os.system('threshold '
              '{0}/tmps/lvepi.nii.gz '
              '{0}/tmps/lvepi.nii.gz '
              '115'
              .format(data_dir))
    
    ##########################################
    os.system('binarize '
              '{0}/{1} '
              '{0}/tmps/lvendo.nii.gz '
              '1 1 255 0'
              .format(data_dir, output_name))
    
    os.system('blur '
              '{0}/tmps/lvendo.nii.gz '
              '{0}/tmps/lvendo.nii.gz '
              '{1}'
              .format(data_dir, alfa))
    
    os.system('threshold '
              '{0}/tmps/lvendo.nii.gz '
              '{0}/tmps/lvendo.nii.gz '
              '130'
              .format(data_dir))
       
    ##########################################
    os.system('padding '
              '{0}/tmps/hrt.nii.gz '
              '{0}/tmps/hrt.nii.gz '
              '{0}/tmps/hrt.nii.gz '
              '1 3'
              .format(data_dir))
    
    os.system('padding '
              '{0}/tmps/hrt.nii.gz '
              '{0}/tmps/rvendo.nii.gz '
              '{0}/tmps/rvendo.nii.gz '
              '1 4'
              .format(data_dir))
    
    os.system('padding '
              '{0}/tmps/rvendo.nii.gz '
              '{0}/tmps/lvepi.nii.gz '
              '{0}/tmps/lvepi.nii.gz '
              '1 2'
              .format(data_dir))
    
    os.system('padding '
              '{0}/tmps/lvepi.nii.gz '
              '{0}/tmps/lvendo.nii.gz '
              '{0}/{1} '
              '1 1'
              .format(data_dir, output_name))
    
    
def allAtlasShapeSelection(dataset_dir):
   
    atlases_list, landmarks_list = {}, {}
    
    for fr in ['ED', 'ES']:
            
        atlases_list[fr], landmarks_list[fr] = [], [] 
        i = 0
        for atlas in sorted(os.listdir(dataset_dir)): 
            
            atlas_dir = os.path.join(dataset_dir, atlas)
            
            if not os.path.isdir(atlas_dir):
                
                print('  {0} is not a valid atlas directory, Discard'.format(atlas_dir))
                
                continue 
            
            atlas_3D_shape = '{0}/PHsegmentation_{1}.nii.gz'.format(atlas_dir, fr)
           
            landmarks = '{0}/landmarks.vtk'.format(atlas_dir)
        
            if i < 400:
                if os.path.exists(atlas_3D_shape) or os.path.exists(landmarks):
                    
                    atlases_list[fr] += [atlas_3D_shape]
                
                    landmarks_list[fr] += [landmarks]
            else:
                print(atlases_list)
                break
            
            i = i + 1
                 
    return atlases_list, landmarks_list


def topSimilarAtlasShapeSelection(atlases, atlas_landmarks, subject_landmarks, tmps_dir, dofs_dir, DLSeg, param_dir, topSimilarAltasNo):            
    
    landmarks = False
    
    nmi = []
    
    topSimilarAtlases_list = []
    
    atlasNo = len(atlases)
    
    os.system('rm {0}/shapenmi*.txt'.format(tmps_dir))
    
    for i in range(atlasNo):
        
        if landmarks:
            
            os.system('pareg '
                      '{0} '
                      '{1} '
                      '-dofout {2}/shapelandmarks_{3}.dof.gz'
                      .format(subject_landmarks, atlas_landmarks[i], dofs_dir, i))
        else: 
            
            os.system('areg '
                      '{0} '
                      '{1} '
                      '-dofout {2}/shapelandmarks_{4}.dof.gz '
                      '-parin {3}/segareg.txt'
                      .format(DLSeg, atlases[i], dofs_dir, param_dir, i))
                      
        os.system('cardiacimageevaluation '
                  '{0} '
                  '{1} '
                  '-nbins_x 64 '
                  '-nbins_y 64 '
                  '-dofin {2}/shapelandmarks_{4}.dof.gz '
                  '-output {3}/shapenmi_{4}.txt'
                  .format(DLSeg, atlases[i], dofs_dir, tmps_dir, i))
                        
        if os.path.exists('{0}/shapenmi_{1}.txt'.format(tmps_dir, i)):

            similarities = np.genfromtxt('{0}/shapenmi_{1}.txt'.format(tmps_dir, i))
            nmi += [similarities[3]]
            
        else:
            nmi += [0]
    
    if topSimilarAltasNo < atlasNo:
        
        sortedIndexes = np.array(nmi).argsort()[::-1]  
        
        savedInd = np.zeros(topSimilarAltasNo, dtype=int)
        
        for i in range(topSimilarAltasNo):
            
            topSimilarAtlases_list += [atlases[sortedIndexes[i]]]
            
            savedInd[i] = sortedIndexes[i]
    else:
        
        savedInd = np.zeros(atlasNo, dtype=int)
        
        topSimilarAtlases_list = atlases
        
        savedInd = np.arange(atlasNo)
        
    return topSimilarAtlases_list, savedInd    
 
