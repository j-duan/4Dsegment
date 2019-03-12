# Deep learning cardiac segmentation and motion tracking (4D*segment*)

![](data/screen.gif)
:--:
*Motion tracking using our pipeline. Left: without shape refinement; Right: with shape refinement*

The code in this repository implements 4D*segment*, a deep learning approach for carrying out segmentation, co-registration, mesh generation and motion tracking using raw grey-scale cardiac MRI data in a nifti format. The implementation was first trained using manual annotations and then deployed on pulmonary hypertension (PH) patients to produce segmentation labels and computational meshes. The whole process is fully automated without any manual inputs. 

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
* [data](data) : data download address, which contains three real PH raw data (4D nifti) on which functions from the `code` directory can be run. You should download the data and place them into this folder.

To run the code in the [code](code) directory, we provide a [Docker](https://www.docker.com) image with all the necessary dependencies pre-compiled. So you do not need to worry about installing or pre-compiling correct versions of dependencies, which sometimes can be a very daunting process. Morever, with Docker you will have no problem to run the code under different systems, such as Linux, MacOS, and Windows. Below are usage instructions:

## 1. Installation/Usage Guide for Docker Image
A Docker image is available on dockerhub https://hub.docker.com/r/jinmingduan/segmentationcoregistration. This image contains a base Ubuntu linux operating system image set up with all the libraries required to run the code (e.g. *Tensorflow*, *nibabel*, *opencv*, etc.). The image also contains pre-compiled IRTK (https://github.com/BioMedIA/IRTK) and MIRTK (https://github.com/BioMedIA/MIRTK) for image registration, as well as external data on which the code can be run. 

### Install Docker
Running our 4D*segment* Docker image requires installation of the Docker software, instructions are available at https://docs.docker.com/install/ 

### Download 4D*segment* Docker image
Once the Docker software has been installed, our 4D*segment* Docker image can be pulled from the Docker hub using the following command:
    
    docker pull jinmingduan/segmentationcoregistration:latest

Once the image download is complete, open up a command-line terminal. On Windows operating systems, this would be the *Command Prompt* (cmd.exe), accessible by opening the [Run Command utility](https://en.wikipedia.org/wiki/Run_command) using the shortcut key `Win`+`R` and then typing `cmd`. On Mac OS, the terminal is accessible via (Finder > Applications > Utilities > Terminal). On Linux systems, any terminal can be used.
Once a terminal is open, running the following command:

    docker images

should show `jinmingduan/segmentationcoregistration` on the list of images on your local system

### Run 4D*segment* Docker image
    
    docker run -it --rm -v /Users/jinmingduan/Desktop/4Dsegment/data/:/data -v /Users/jinmingduan/Desktop/4Dsegment/code/:/code -v /Users/jinmingduan/Desktop/4Dsegment/model/:/model jinmingduan/segmentationmeshmotion /bin/bash
    
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

Finally do  
```
python DMACS.py --coreNo 8 --irtk True
```
will run the code using 8 CPU cores on your local computer (change the number to fit your machine) with irtk registration toolbox. 

## 2. Citation
If you find this software is useful for your project or research. Please give some credits to authors who developed it by citing some of the following papers. We really appreciate that. 

[1] Duan J, Bello G, Schlemper J, Bai W, Dawes TJ, Biffi C, de Marvao A, Doumou G, O’Regan DP, Rueckert D. Automatic 3D bi-ventricular segmentation of cardiac images by a shape-refined multi-task deep learning approach IEEE transactions on medical imaging, 2019. 

[2] Bello GA,  Dawes TJW, Duan J, Biffi C, de Marvao A, Howard LSGE, Gibbs JSR, Wilkins MR, Cook SA, Rueckert D, O'Regan DP. Deep learning cardiac motion analysis for human survival prediction. Nature Machine Intelligence, 1 (2) 95, 2019.

