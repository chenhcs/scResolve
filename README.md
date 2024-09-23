# scResolve

**scResolve: Recovering single cell expression profiles from multi-cellular spatial transcriptomics**


<p align="center">
<img src=assets/scresolve.png width="500" height="500">
</p>


scResolve is a deep learning based method that recovers spatially resolved single cell expression profiles from low-resolution spatial transcriptomics and the paired histology image.  

It's easy to use. With below 3 command lines, you can obtain an [anndata](https://anndata.readthedocs.io/en/latest/) object storing single-cell gene expression and cell locations in tissue from low-resolution spatial transcriptomics data, like Visium.</br>
``scresolve convert`` - preprocess your data</br>
``scresolve super-resolution `` - run super-resolution to obtain pixel-level expression</br>
``scresolve segmentation`` - run cell segmentation to obtain expression profiles of single cells and their locations</br>

# Contents
- [Installation](https://github.com/chenhcs/scResolve/tree/main?tab=readme-ov-file#installation)
- [Tutorial: Run scResolve on the breast cancer dataset from ST platform](https://github.com/chenhcs/scResolve/tree/main?tab=readme-ov-file#tutorial-run-scresolve-on-the-breast-cancer-dataset-from-st-platform)
- [Configuration](https://github.com/chenhcs/scResolve/tree/main?tab=readme-ov-file#configuration)
- [Running scResolve on Visium data](https://github.com/chenhcs/scResolve/tree/main?tab=readme-ov-file#running-scresolve-on-visium-data)
- [Contact](https://github.com/chenhcs/scResolve/tree/main?tab=readme-ov-file#contact)



# Installation
scResolve is developed and tested under Python 3.9. Run the following command to install scResolve.
Update: We noticed possible runtime error depending on the configuration of the machine. So here we provide stable version with Python=3.8. In addition, Pytorch=1.11 should be mannually installed. 
````
conda create -n scresolve python=3.8
conda activate scresolve
pip install git+https://github.com/chenhcs/scResolve@main
````
After above commands, install Pytorch=1.11 that suits to your machine configuration(Window/Linux and CUDA).
For CUDA 11.3, you can use below command:
''''
pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu113
'''
For other configuration of Pytorch=1.11, please check below webpage:
[https://pytorch.org/get-started/previous-versions/]

Installation takes around 4 minutes and 30 seconds.
Once installation is completed, verify the installation by command ``scresolve``.

# Tutorial: Run scResolve on the breast cancer dataset from ST platform
Here we provide a tutorial on applying scResolve to the breast cancer dataset generated from the ST platform and reproducing the results from our work.

There are four ST sections in the dataset. Download the data from the link [https://www.spatialresearch.org/resources-published-datasets/doi-10-1126science-aaf2403/](https://www.spatialresearch.org/resources-published-datasets/doi-10-1126science-aaf2403/), or simply use the commands below. We will first use one section as an example, and the same steps can be repeated on the other three sections.

````
curl -Lo section1.jpg https://www.spatialresearch.org/wp-content/uploads/2016/07/HE_layer1_BC.jpg
curl -Lo section1.tsv https://www.spatialresearch.org/wp-content/uploads/2016/07/Layer1_BC_count_matrix-1.tsv
curl -Lo section1-alignment.txt https://www.spatialresearch.org/wp-content/uploads/2016/07/Layer1_BC_transformation.txt
````

The command below will generate the formatted input for the model.

````
scresolve convert st --counts section1.tsv --image section1.jpg --transformation-matrix section1-alignment.txt --scale 0.3 --save-path section1
````
The `scale` parameter controls the resizing of the original histology image. The height and width of the image will be adjusted to the percentage specified by the `scale` parameter. A larger value of the parameter can lead to more accurate cell segmentation in the following steps while will require more computing resources. A HDF5 file will be saved in the directory specified by `--save-path`.

Next we run super-resolution on the low-resolution spatial transcriptomics and the histology image.

````
scresolve super-resolution tutorial.toml --save-path tutorial
````

The location of the HDF5 file and model parameters are set in the [*.toml file](https://github.com/chenhcs/scResolve/raw/main/configurations/tutorial.toml), which will be discussed in the next section. This process will generate pixel-level gene expression maps, which will be stored in a tsv file within the directory specified by `--save-path`.

Finally, run cell segmentation on the super-resolution gene expression maps using the command below.
````
scresolve segmentation tutorial.toml --count ./tutorial/segment_input/section1.tsv --image ./tutorial/segment_input/section1.jpg --output_path ./results
````

An anndata object storing the expression profiles and locations of cells will be saved in the directory specified by `--output_path`.

Results for the other three sections in this dataset can be generated by repeating the same steps. The data can be downloaded using the commands in `get_data.sh`.


# Configuration

scResolve uses below configuration, saved as a toml file.

````
[super_resolution_model]
network_depth = 6
network_width = 16
min_counts = 50

[super_resolution_expansion_strategy]
type = "DropAndSplit"
[super_resolution_expansion_strategy.DropAndSplit]
max_metagenes = 50

[super_resolution_optimization]
batch_size = 3
epochs = 100000
learning_rate = 0.0003
patch_size = 768

[super_resolution_analyses]
[super_resolution_analyses.metagenes]
type = "metagenes"
[super_resolution_analyses.metagenes.options]
method = "pca"

[super_resolution_analyses.gene_maps]
type = "gene_maps"
[super_resolution_analyses.gene_maps.options]
gene_regex = ".*"
predict_mean = false
writer = "tensor"

[super_resolution_backtrack]
backtrack = true
min_num_metagenes = 20

[segmentation]
ws_otsu_classes = 4
bg_th = 100
epochs = 100
patch_size = 1000

[slides]
[slides.section1]
data = "path_to_h5"
[slides.section1.covariates]
section = 1
````
There are several important parameters to be considered.  

**Super-resolution model**  
    1. ``backtrack``: this is used for model selection. Set to `true` if you want to backtrack to select a model checkpoint with at least a minimum number of metagenes set by `min_num_metagenes`.  
    2. ``min_num_metagenes``: minimum number of metagenes. Ignored if backtrack is `false`.
    Detailed explanations for other parameters can be found [here](https://github.com/ludvb/xfuse#configuring-and-starting-the-run).

**Cell segmentation model**   
    1. `bg_th`: threshold for background pixels. Pixels with values smaller than this threshold will be treated as background.  
    2. `ws_otsu_classes`: controls the sizes of detected nuclei by watershed. A higher value results in larger nuclei being detected through watershed.  
    3. `patch_size`: the size of the patches the section will be split into (pixels x pixels). Cell segmentation will be performed patch by patch.

# Running scResolve on Visium data
To run scResolve on Visium data, paths for the files below need to be provided:  
``bc-matrix``: bc-matrix provided by Visium platform (e.g., filtered_feature_bc_matrix.h5).   
``image``: high resolution H&E image.
``tissue-position``: tissue position provided by Visium platform (e.g., tissue_positios_list.csv). Make sure it has a header line.  
``scale-factors``: scale factor provided by Visium platform in a Json format.  
``mask-file``: a tissue mask for the super-resolution step. Each pixel in the mask file should be either 0 (background) or 1 (tissue).  

Run the following command to generate the formatted input.

````
scresolve convert visium --bc-matrix PATH --image PATH --tissue-positions PATH --scale-factors PATH --mask-file PATH --scale INT --save-path PATH
````
where each PATH specifies each input file.

For the configuration file, you can download the default one from [here](https://github.com/chenhcs/scResolve/blob/main/configurations/configurations.toml).
Then use the following command to run super resolution.
````
scresolve super-resolution CONFIGURATION_FILE --save-path SAVE_PATH
````

Finally, use the following command to run cell segmentation.  
````
scresolve segmentation CONFIGURATION_FILE --count PATH_TO_SUPER_RESOLUTION_OUTPUT --image PATH_TO_IMAGE_OUTPUT --output_path PATH_TO_SAVE_RESULTS
````

# Contact
Contact us if you have any questions:</br>
Hao Chen: hchen4 at andrew.cmu.edu</br>
Young Je Lee: youngjel at cs.cmu.edu</br>
Jose Lugo-Martinez: jlugomar at andrew.cmu.edu
