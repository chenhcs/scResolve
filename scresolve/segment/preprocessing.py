from src import preprocessing #preprocessing #transformer #,
from sys import argv
from PIL import Image, ImageOps

script, startr, startc, patch_size, dataset = argv

if dataset == 'bc1_4x4_03':
    bin_file = '../xfuse/sec1-run3/patches/section1_5_0:9980_0:10045_s0_e3475.tsv'
    image_file = '../xfuse/section1_ori/section1_resized_0:9980_0:10045_shift.jpg'
elif dataset == 'bc2_4x4_03':
    bin_file = '../xfuse/sec2-run3/patches/section2_5_0:9760_0:10030_s0_e3368.tsv'
    image_file = '../xfuse/section2_ori/section2_resized_0:9760_0:10030_shift.jpg'
elif dataset == 'bc3_4x4_03':
    bin_file = '../xfuse/sec3-run3/patches/section3_5_0:10100_0:10005_s0_e3190.tsv'
    image_file = '../xfuse/section3_ori/section3_resized_0:10100_0:10005_shift.jpg'
elif dataset == 'bc4_4x4_03':
    bin_file = '../xfuse/sec4-run3/patches/section4_5_0:10125_0:9925_s0_e3413.tsv'
    image_file = '../xfuse/section4_ori/section4_resized_0:10125_0:9925_shift.jpg'
elif dataset == 'STB01S4_14x14':
    bin_file = '../xfuse/sennet_STB01S4_run1/patches/STB01S4_5_0:18215_0:16415_s0_e12537.tsv'
    image_file = '../xfuse/sennet_STB01S4_rotate/STB01S4_resized_0:18215_0:16415_shift.jpg'
elif dataset == 'STB01S2_14x14':
    bin_file = '../xfuse/sennet_STB01S2_run1/patches/STB01S2_5_0:16530_0:17690_s0_e15536.tsv'
    image_file = '../xfuse/sennet_STB01S2_rotate/STB01S2_resized_0:16530_0:17690_shift.jpg'
elif dataset == 'STB01S1_14x14':
    bin_file = '../xfuse/sennet_STB01S1_run1/patches/STB01S1_5_0:17210_0:18300_s0_e14326.tsv'
    image_file = '../xfuse/sennet_STB01S1_rotate/STB01S1_resized_0:17210_0:18300_shift.jpg'
elif dataset == 'STB01S3_14x14':
    bin_file = '../xfuse/sennet_STB01S3_run1/patches/STB01S3_5_0:17975_0:18270_s0_e14307.tsv'
    image_file = '../xfuse/sennet_STB01S3_rotate/STB01S3_resized_0:17975_0:18270_shift.jpg'
prealigned = True
align=None
bin_size=5
ws_otsu_classes=4
ws_otsu_index=1
bg_th=100
n_neighbor=50
epochs=100
dia_estimate=10
min_sz=500
preprocessing.preprocess(dataset, bin_file, image_file, prealigned, align, startr, startc, patch_size, bin_size, ws_otsu_classes, ws_otsu_index, bg_th, n_neighbor)
#transformer.train(dataset, startr, startc, patch_size, 100)
#postprocessing.postprocess(dataset, startr, startc, patch_size, bin_size, dia_estimate, min_sz)
