# scResolve

**scResolve: Recovering single cell expression profiles from multi-cellular spatial transcriptomics**


<p align="center">
<img src=assets/scresolve.png width="500" height="500">
</p>


scResolve is a deep learning based pipeline that recovers single cells from low-resolution spatial transcriptomics.  
It's easy to use: with below 3 command lines, you can recover single cell level gene expression from low-resolution ST data!  
``scresolve convert`` - preprocess your data  
``scresolve super-resolution `` - run super-resolution model  
``scresolve segment`` - get single cells

# Contents
- [Install](https://github.com/chenhcs/scResolve/blob/main/README.md#install)
- Tutorial: Running scResolve on Breast cancer ST data
    - [Quick version with running one breast cancer section](https://github.com/chenhcs/scResolve/blob/main/README.md#quick-version-running-one-slide-of-breast-cancer)
    - [Running all 4 breast cancer sections](https://github.com/chenhcs/scResolve/blob/main/README.md#running-all-4-breast-cancer-sections)
- [Configuration](https://github.com/chenhcs/scResolve/blob/main/README.md#configuration)
- [Running scResolve on your Visium data](https://github.com/chenhcs/scResolve/blob/main/README.md#running-scresolve-on-your-visium-data)
- Acknowledgment




# Install
scResolve is developed with Python 3.9
````
conda create -n scresolve python=3.9
conda activate scresolve
pip install git@git
````
This will take time. Once installation is completed, verify the installation by ``scresolve``
scResolve is tested under NVIDIA RTX3080 and torch=1.11.1. If you face an issue with installation, see Install a different version of torch in scResolve

# Tutorial: Running scResolve on Breast cancer ST data
Here we provide 2 tutorials  
    - First tutorial is quick version, where you can get the idea of how to use scResolve quickly.  
    - Second tutorial is how to replicate our work.

In our work, we used data from [Patrick et al](https://www.science.org/doi/10.1126/science.aaf2403)
## Quick version: Running one slide of Breast cancer
In this tutorial, we will recover single cells in one of the slides in the breast cancer section.

The link to the dataset is: [https://www.spatialresearch.org/resources-published-datasets/doi-10-1126science-aaf2403/](https://www.spatialresearch.org/resources-published-datasets/doi-10-1126science-aaf2403/)  
Or simply you can download with below codes. This will download H&E image, gene expression count and alignment data

````
curl -Lo section1.jpg https://www.spatialresearch.org/wp-content/uploads/2016/07/HE_layer1_BC.jpg
curl -Lo section1.tsv https://www.spatialresearch.org/wp-content/uploads/2016/07/Layer1_BC_count_matrix-1.tsv
curl -Lo section1-alignment.txt https://www.spatialresearch.org/wp-content/uploads/2016/07/Layer1_BC_transformation.txt
````

Below code will generate the formatted input for super-resolution model

````
scresolve convert st --counts section1.tsv --image section1.jpg --transformation-matrix section1-alignment.txt --scale 0.3 --save-path section1
````
We save settings in *.toml file. For the setting of this tutorial, you can see in [link].
Download the toml file.
[link Download toml file]


Now we can run super-resolution model.

````
scresolve super-resolution tutorial_quick.toml --save-path tutorial_quick
````

This process will generate output of the super-resolution model, then preprocess the output to generate the formatted input for the segmentation model.
In detail, you will see a tsv file and a grey-scaled jpg file in ``segment_input`` directory.

Finally, we run segmentation model
````
scresolve segment tutorial.toml --count ./segment_input/section1.tsv --image ./segment_input/section1.jpg
````

This command generates the coordinates of cells in spot2cell.txt and visualized map as cell_masks.png


## Running all 4 breast cancer sections
This is replicating our work. In summary, we apply the quick version tutorial to all 4 sections.  
We run each sections separately, due to high computational resource requirement of using all 4sections at once, and running each sections separately allows us to utilize cluster environment.  

First we download H&E image, gene expression count and alignment data of all 4 sections.  
````
# Image data
curl -Lo section1.jpg https://www.spatialresearch.org/wp-content/uploads/2016/07/HE_layer1_BC.jpg
curl -Lo section2.jpg https://www.spatialresearch.org/wp-content/uploads/2016/07/HE_layer2_BC.jpg
curl -Lo section3.jpg https://www.spatialresearch.org/wp-content/uploads/2016/07/HE_layer3_BC.jpg
curl -Lo section4.jpg https://www.spatialresearch.org/wp-content/uploads/2016/07/HE_layer4_BC.jpg

# Gene expression count data
curl -Lo section1.tsv https://www.spatialresearch.org/wp-content/uploads/2016/07/Layer1_BC_count_matrix-1.tsv
curl -Lo section2.tsv https://www.spatialresearch.org/wp-content/uploads/2016/07/Layer2_BC_count_matrix-1.tsv
curl -Lo section3.tsv https://www.spatialresearch.org/wp-content/uploads/2016/07/Layer3_BC_count_matrix-1.tsv
curl -Lo section4.tsv https://www.spatialresearch.org/wp-content/uploads/2016/07/Layer4_BC_count_matrix-1.tsv

# Alignment data
curl -Lo section1-alignment.txt https://www.spatialresearch.org/wp-content/uploads/2016/07/Layer1_BC_transformation.txt
curl -Lo section2-alignment.txt https://www.spatialresearch.org/wp-content/uploads/2016/07/Layer2_BC_transformation.txt
curl -Lo section3-alignment.txt https://www.spatialresearch.org/wp-content/uploads/2016/07/Layer3_BC_transformation.txt
curl -Lo section4-alignment.txt https://www.spatialresearch.org/wp-content/uploads/2016/07/Layer4_BC_transformation.txt

````

Prepare formatted input for super-resolution model  

````
scresolve convert st --counts section1.tsv --image section1.jpg --transformation-matrix section1-alignment.txt --scale 0.3 --save-path section1
scresolve convert st --counts section2.tsv --image section2.jpg --transformation-matrix section2-alignment.txt --scale 0.3 --save-path section2
scresolve convert st --counts section3.tsv --image section3.jpg --transformation-matrix section3-alignment.txt --scale 0.3 --save-path section3
scresolve convert st --counts section4.tsv --image section4.jpg --transformation-matrix section4-alignment.txt --scale 0.3 --save-path section4
````
Now, for each prepared formatted input section, run super-resolution and segmentation. We highly recommend running below commands in cluster environment, so you can utilize parallelization.  
We prepared configuration files for each section for you. The differences between configuration files are unique naming to prevent overwriting.  

section 1  
````
scresolve super-resolution tutorial_section1.toml --save-path section1
scresolve segment tutorial_section1.toml --count ./segment_input/section1.tsv --image ./segment_input/section1.jpg
````
  
section 2  
````
scresolve super-resolution tutorial_section2.toml --save-path section2
scresolve segment tutorial_section2.toml --count ./segment_input/section2.tsv --image ./segment_input/section2.jpg
````
  
section 3  
````
scresolve super-resolution tutorial_section3.toml --save-path section3
scresolve segment tutorial_section3.toml --count ./segment_input/section3.tsv --image ./segment_input/section3.jpg
````
  
section 4  
````
scresolve super-resolution tutorial_section4.toml --save-path section4
scresolve segment tutorial_section4.toml --count ./segment_input/section4.tsv --image ./segment_input/section4.jpg
````


# Configuration

scResolve uses below configuration, saved as toml file.

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
min_num_metagenes = 4

[super_resolution_to_segment]
scale_factor = 10

[segment]
prealigned = false
bin_size = 10
ws_otsu_classes = 4
bg_th = 10
epochs = 100
patch_size = 0

[slides]
[slides.section1]
data = "path_to_h5"
image= "path_to_img"
[slides.section1.covariates]
section = 1

[slides.section2]
data = "path_to_h5"
image= "path_to_img"
[slides.section2.covariates]
section = 2
````
There are several important parameters you need to consider.  

**Super-resolution model**  
    1. Backtrack  
    We noticed that if number of metagenes is lower than number of the cell types, the model confuses and super-resolution might be inaccurate.  
    Therefore, you might need to use recent session that satisfies the minimum number of metagene threshold.   
    You can control this in toml setting file.  
    - ``backtrack``: true if you want to use backtrack.  
    - ``min_num_metagenes``: Minimum number of metagenes. Ignored if backtrack == false  
    2. ``scale_factor``  
    This parameter controls mataching gene expression matrix with image. We recommend using default value, which is 10  
    Other parameters detail can be found in this [link](https://github.com/ludvb/xfuse#configuring-and-starting-the-run)   

**Segment model**   
    - bg_th: Determines which pixels will be treated as background.  
    - ws_otsu_classes: Decides how large the detected nuclei by Watershed will be.We recommend using a value of 3 or 4.  
    




# Running scResolve on your Visium data
Before you run your Visium data, please read the configuration!!!  

To run with Visium data, you need to provide paths of below files  
``bc-matrix``: bc-matrix provided by Visium platform(e.g filtered_feature_bc_matrix.h5).   
``image``: H&E image. We recommend using high resolution image.  
``tissue-position``: Tissue position provided by Visium platform. It has name of tissue_positios_list.csv. Make sure it has a header.  
``scale-factors``: Scale factor provided by Visium platform. A Json format file.  
``mask-file``: We recommend providing a custom mask for super-resolution model. The each pixel in the mask file should be 0 if background, 1 if foreground, 2 if likely background and 4 if likely foreground.  

It is recommended using higher ``scale`` as possible. However, increasing this value requires high GPU resource and will take longer time.  

For the configuration file, you can download default here  

Once you determine above considerations, simply run  

````
scresolve convert visium --bc-matrix PATH --image PATH --tissue-positions PATH --scale-factors PATH --mask-file PATH --scale INT --save-path PATH
````
where each PATH corresponds to the input file.

Then run  
````
scresolve super-resolution CONFIGURATION_FILE --save-path SAVE_PATH
````

Finally, run  
````
scresolve segment CONFIGURATION_FILE --count PATH_TO_SUPER_RESOLUTION_OUTPUT--image PATH_TO_IMAGE_OUTPUT
````



# Acknowledgment
We specially appreciate authors of Xfuse for their generous usage of their model.

