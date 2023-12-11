from src import postprocessing #preprocessing #transformer #,
from sys import argv

script, startr, startc, patch_size, dataset = argv

prealigned = True
align=None
bin_size=5
ws_otsu_classes=4
ws_otsu_index=1
bg_th=100
n_neighbor=50
epochs=100
dia_estimate=20
min_sz=500
#preprocessing.preprocess(dataset, bin_file, image_file, prealigned, align, startr, startc, patch_size, bin_size, ws_otsu_classes, ws_otsu_index, bg_th, n_neighbor)
#transformer.train(dataset, startr, startc, patch_size, 100)
postprocessing.postprocess(dataset, startr, startc, patch_size, bin_size, dia_estimate, min_sz)
