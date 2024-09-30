import math
import numpy as np
import pandas as pd
import glob
import anndata as ad
from .src import preprocessing, transformer, postprocessing

def write_to_anndata(save_path, bin_file):
    df = pd.read_table(bin_file)
    minx = df['x'].min()
    miny = df['y'].min()

    genes = list(set(df['geneID'].values.tolist()))
    genes.sort()
    geneid = {}
    for i,gene in enumerate(genes):
        geneid[gene] = i
    print('# of genes:', len(genes))

    pos2cell = {}
    cell2pos_x = {}
    cell2pos_y = {}
    all_cells = set()
    numcells = 0
    files = glob.glob(save_path + '/results/spot2cell*.txt')
    files.sort()
    for file in files:
        print('processing:', file)
        fr = open(file)
        startx = int(file.split('_')[-1].split(':')[0])
        starty = int(file.split('_')[-1].split(':')[1])
        for line in fr:
            pos, cell = line.split()
            posx, posy = pos.split(':')
            pos = str(int(posx) + startx) + ':' + str(int(posy) + starty)
            pos2cell[pos] = int(cell.split('.')[0]) + numcells
            cell = int(cell.split('.')[0]) + numcells
            all_cells.add(cell)
            cell = 'cell_' + str(cell)
            if cell not in cell2pos_x:
                cell2pos_x[cell] = [int(pos.split(':')[0])]
                cell2pos_y[cell] = [int(pos.split(':')[1])]
            else:
                cell2pos_x[cell].append(int(pos.split(':')[0]))
                cell2pos_y[cell].append(int(pos.split(':')[1]))
        numcells = np.max(list(all_cells))

    genecnt = len(genes)
    cellexp = np.zeros((numcells + 1, genecnt))
    with open(bin_file) as fr:
        header = fr.readline()
        line_cnt = 0
        for line in fr:
            line_cnt += 1
            gene, x, y, count = line.split()
            x = str(int(x) - minx)
            y = str(int(y) - miny)
            if gene not in geneid:
                continue
            if x + ':' + y in pos2cell:
                cellexp[pos2cell[x + ':' + y], geneid[gene]] += int(count)

    cellidx = np.where(np.sum(cellexp, axis=1) > 0)[0]
    cellexp = cellexp[cellidx]

    adata = ad.AnnData(
        cellexp,
        obs=pd.DataFrame(index=['cell_' + str(i) for i in range(cellexp.shape[0])]),
        var=pd.DataFrame(index=genes),
    )

    posx = []
    posy = []
    for idx in cellidx:
        if 'cell_' + str(idx) in cell2pos_x:
            posx.append(np.mean(cell2pos_x['cell_' + str(idx)]))
            posy.append(np.mean(cell2pos_y['cell_' + str(idx)]))
        else:
            posx.append(0)
            posy.append(0)
    adata.obs['x'] = posx
    adata.obs['y'] = posy

    adata.write_h5ad(save_path + '/scresolve_output.h5ad')

def segment_cells(save_path, bin_file, image_file, patch_size=0, ws_otsu_classes=4, ws_otsu_index=1, bg_th=100, n_neighbor=50, epochs=100, dia_estimate=20, min_sz=500,cluster_index='-1'):
    prealigned=True
    align=None
    bin_size=5
    n_neighbor=50
    if patch_size == 0:
        preprocessing.preprocess(save_path, bin_file, image_file, prealigned, align, 0, 0, patch_size, bin_size, ws_otsu_classes, ws_otsu_index, bg_th, n_neighbor)
        transformer.train(save_path, 0, 0, patch_size, epochs)
        postprocessing.postprocess(save_path, 0, 0, patch_size, bin_size, dia_estimate, min_sz)
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
        if cluster_index=='-1':
            print(str(n_patches) + ' patches will be processed.')
            for startr in range(0, rmax, patch_size):
                for startc in range(0, cmax, patch_size):
                    try:
                        print('Processing the patch ' + str(startr) + ':' + str(startc) + '...')
                        preprocessing.preprocess(save_path, bin_file, image_file, prealigned, align, startr, startc, patch_size, bin_size, ws_otsu_classes, ws_otsu_index, bg_th, n_neighbor)
                        transformer.train(save_path, startr, startc, patch_size, epochs)
                        postprocessing.postprocess(save_path, startr, startc, patch_size, bin_size, dia_estimate, min_sz)
                    except Exception as e:
                        print(e)
                        print('Patch ' + str(startr) + ':' + str(startc) + ' failed. This could be due to no nuclei detected by Watershed or too few RNAs in the patch.')
            write_to_anndata(save_path,bin_file)

        elif cluster_index=='print':
            print(str(n_patches) + ' patches need to be processed.')
            print('Array index 0-'+str(n_patches-1))
        elif cluster_index=='merge':
            write_to_anndata(save_path,bin_file)
        else:
            cluster_index=int(cluster_index)
            index=0
            for startr in range(0, rmax, patch_size):
                for startc in range(0, cmax, patch_size):
                    if index==cluster_index:
                        try:
                            print('Processing the patch ' + str(startr) + ':' + str(startc) + '...')
                            preprocessing.preprocess(save_path, bin_file, image_file, prealigned, align, startr, startc, patch_size, bin_size, ws_otsu_classes, ws_otsu_index, bg_th, n_neighbor)
                            transformer.train(save_path, startr, startc, patch_size, epochs)
                            postprocessing.postprocess(save_path, startr, startc, patch_size, bin_size, dia_estimate, min_sz)
                        except Exception as e:
                            print(e)
                            print('Patch ' + str(startr) + ':' + str(startc) + ' failed. This could be due to no nuclei detected by Watershed or too few RNAs in the patch.')
                    index+=1

