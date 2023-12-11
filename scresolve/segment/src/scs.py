import math
import numpy as np
from src import preprocessing, transformer, postprocessing

def segment_cells(bin_file, image_file, prealigned=False, align=None, patch_size=0, bin_size=3, ws_otsu_classes=4, ws_otsu_index=1, bg_th=10, n_neighbor=50, epochs=100, dia_estimate=15, min_sz=200):
    if patch_size == 0:
        preprocessing.preprocess(bin_file, image_file, prealigned, align, 0, 0, patch_size, bin_size, ws_otsu_classes, ws_otsu_index, bg_th, n_neighbor)
        transformer.train(0, 0, patch_size, epochs)
        postprocessing.postprocess(0, 0, patch_size, bin_size, dia_estimate, min_sz)
    else:
        r_all = []
        c_all = []
        with open(bin_file) as fr:
            header = fr.readline()
            for line in fr:
                _, r, c, _ = line.split()
                r_all.append(int(r))
                c_all.append(int(c))
        rmax = np.max(r_all) - np.min(r_all)
        cmax = np.max(c_all) - np.min(c_all)
        n_patches = math.ceil(rmax / patch_size) * math.ceil(cmax / patch_size)
        print(str(n_patches) + ' patches will be processed.')
        for startr in range(0, rmax, patch_size):
            for startc in range(0, cmax, patch_size):
                try:
                    print('Processing the patch ' + str(startr) + ':' + str(startc) + '...')
                    if startr <= 4000 or startc == 8000:
                        continue
                    preprocessing.preprocess(bin_file, image_file, prealigned, align, startr, startc, patch_size, bin_size, ws_otsu_classes, ws_otsu_index, bg_th, n_neighbor)
                    transformer.train(startr, startc, patch_size, epochs)
                    postprocessing.postprocess(startr, startc, patch_size, bin_size, dia_estimate, min_sz)
                except Exception as e:
                    print(e)
                    print('Patch ' + str(startr) + ':' + str(startc) + ' failed. This could be due to no nuclei detected by Watershed or too few RNAs in the patch.')
