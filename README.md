# Deep learning cardiac segmentation and motion tracking (4D*segment*)

![](data/screen.gif)
:--:
*Motion tracking using our pipeline. Left: without shape refinement; Right: with shape refinement*

The code in this repository implements 4D*segment*, a pipeline for carrying out deep learning segmentation, non-rigid co-registration, mesh generation and motion tracking using raw grey-scale cardiac MRI data in NIfTI format. The implementation was first trained using manual annotations and then deployed on pulmonary hypertension (PH) patients to produce segmentation labels and computational meshes. The whole process is fully automated without any manual input. 

# Overview
The files in this repository are organized into 3 directories:
* [code](code) : contains base functions for segmentation, co-registration, mesh generation, and motion tracking:
  * code entrance - [code/DMACS.py](code/DMACS.py)
  * deep learning segmentation with the pre-trained model - [code/deepseg.py](code/deepseg.py)
  * co-registration to fit a high-resolution model - [code/p1&2processing.py](demo/p1&2processing.py)
  * fitting meshes to high-resolution model - [code/meshfitting.py](code/meshfitting.py)
  * useful image processing functions used in the pipeline - [code/image_utils.py](code/image_utils.py)
  * downsample mesh resolution while remain its geometry - [code/decimation.py](code/decimation.py)
* [model](model) : contains a tensorflow model pre-trained on ~400 manual annotations on PH patients
* [data](data) : data download address, which contains three sample datasets (4D NIfTI) on which functions from the `code` directory can be run. You should download the data and place them into this folder.

To run the code in the [code](code) directory, we provide a [Docker](https://www.docker.com) image with all the necessary dependencies pre-compiled. 

## 1. Installation/Usage Guide for Docker Image
A Docker image is available on dockerhub https://hub.docker.com/r/jinmingduan/segmentationcoregistration. This image contains a base Ubuntu linux operating system image set up with all the libraries required to run the code (e.g. *Tensorflow*, *nibabel*, *opencv*, etc.). The image also contains pre-compiled IRTK (https://github.com/BioMedIA/IRTK) and MIRTK (https://github.com/BioMedIA/MIRTK) for image registration, as well as external data on which the code can be run. 

### Download the repo
Click the download button, unzip to your desktop and name the top-level folder `4Dsegment`.
Go to /data and download the sample images from the URL in the text file.

### Install Docker
For Windows 10 Pro first install [Docker](https://www.docker.com/docker-windows). Windows 10 Home users will require [Docker toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/).

Ensure you have the C drive selected as a [shared drive](https://docs.docker.com/docker-for-windows/) in Docker settings (or in VirtualBox on W10 Home).

To visualise the segmentations download [ITKsnap](http://www.itksnap.org/pmwiki/pmwiki.php).

### Download 4D*segment* Docker image
In W10 open _PowerShell_ from the Windows search box (`Win` + `X` then `I`), in macOS navigate Finder > Applications > Utilities > Terminal, or in Linux any terminal can be used. Then download the pre-compiled image:
    
    docker pull jinmingduan/segmentationcoregistration:latest

    docker images

should show `jinmingduan/segmentationcoregistration` on the list of images on your local system

### Run 4D*segment* Docker image

Note the path to the folder on your desktop eg /c/Users/home/Desktop/4Dsegment and substitute \<folder-path\> within this command:   
    
    docker run -it --rm -v <folder-path>/data/:/data -v <folder-path>/code/:/code -v <folder-path>/model/:/model jinmingduan/segmentationmeshmotion /bin/bash
    
launches an interactive linux shell terminal that gives users access to the image's internal file system. Note /Users/jinmingduan/Desktop/4Dsegment is where the downloaded github repository is unzipped. In addition, the command passes the [code](code), [model](model) and [data](data) into the docker container such that the code can be run within the container

Typing next
```
ls -l
```
will list all the folders in the working directory of the Docker image. You should see the 3 main folders `code`, `data` and `model`, which contain the same files as the corresponding folders with the same name in this github repository.

Typing next 
```
export LD_LIBRARY_PATH=/lib64 
```
will point you where the compiled libraries are

Typing next 
```
cd /code
```
will bring you to the directory where the code is saved

Finally doing  
```
python DMACS.py --coreNo 8 --irtk True
```
will run the code using 8 CPU cores on your local computer (change the number to fit your machine) with irtk registration toolbox. 

## 2. Outputs from the pipeline

Once the pipeline is finished, under the root directory of each subject, you have three nifti files, i.e., `lvsa_.nii.gz`, `lvsa_ED_enlarged_SR.nii.gz` and `lvsa_ES_enlarged_SR.nii.gz`, and two segmentations, i.e., `PHsegmentation_ED.gipl` and `PHsegmentation_ES.gipl`. `lvsa_.nii.gz` is the original 4D raw data and `PHsegmentation_ED.gipl` and `PHPHsegmentation_ES.gipl` are segmentations of `lvsa_ED_enlarged_SR.nii.gz` and `lvsa_ES_enlarged_SR.nii.gz`. Note that these segmentations are smooth, high-resolution bi-ventricular three-dimensional models. 

You also have meshes (txt files) for left and right ventricles at ED and ES under the root directory. For example, `lv_myoed_curvature.txt` records the curvature of each vertex on myocardium of left ventricle at ED. `lv_myoed_wallthickness.txt` records the wall thickness of each vertex on epicardium of left ventricle at ED. `lv_myoed_signeddistances.txt` records the sign distance of each vertex on epicardium of left ventricle at ED, by referring to a template. `lv_myoed_curvature.txt`, `lv_myoes_wallthickness.txt` and `lv_myoes_signeddistances.txt` have the same meanings for left ventricle at ES. There are also counterparts for right ventricle at ED and ES. 

In addition, the pipeline also produces the folders of [dofs](dofs), [segs](segs), [sizes](sizes), [tmps](tmps), [vtks](vtks) and [motion](motion) under the root directory. Apart from [motion](motion) folder, the files in other folders are intermediate results, which may not be useful for sequential analysis. In [motion](motion) folder, you have 20 computational meshes (both vtk and txt files) for a complete cardiac cycle. In each of 20 meshes, only spatial locations of vertices are recorded. Vertex spatial position (x, y and z) on the same row in the txt files corresponds to the same anatomical location across the cardiac cycle.    


## 3. Citation
If you find this software useful for your project or research. Please give some credits to authors who developed it by citing some of the following papers. We really appreciate that. 

[1] Duan J, Bello G, Schlemper J, Bai W, Dawes TJ, Biffi C, de Marvao A, Doumou G, O’Regan DP, Rueckert D. Automatic 3D bi-ventricular segmentation of cardiac images by a shape-refined multi-task deep learning approach. *[IEEE Transactions on Medical Imaging](https://doi.org/10.1109/TMI.2019.2894322)* (2019). 

[2] Bello GA, Dawes TJW, Duan J, Biffi C, de Marvao A, Howard LSGE, Gibbs JSR, Wilkins MR, Cook SA, Rueckert D, O'Regan DP. Deep learning cardiac motion analysis for human survival prediction. *[Nature Machine Intelligence](https://doi.org/10.1038/s42256-019-0019-2)* 1, 95–104 (2019).

