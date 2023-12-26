# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 21:47:56 2023

@author: Young Je Lee
"""
import os
import torch
import pandas as pd
import cv2
import numpy as np
from multiprocessing import Pool
from itertools import repeat
import argparse
from pathlib import Path
import time
import logging
from datetime import datetime
from PIL import Image, ImageOps
import h5py
import pandas as pd
Image.MAX_IMAGE_PIXELS = None
'''
Updates

Jan 30 Coordinate fixed
'''

def super_resolution_to_segment_converter(current_path,config):
    startTime= time.process_time()
    segment_input_path=os.path.join(current_path,'segment_input')
    Path(segment_input_path).mkdir(parents=True, exist_ok=True)


    ##Initialize logging
    # logging.basicConfig(filename=datetime.now().strftime('./Generate_TSV_'+'%b_%d_%y_%H:%M:%S.log'),
    #                     filemode='w',
    #                     format='%(asctime)s:%(msecs)d %(name)s %(levelname)s %(message)s',
    #                     level=logging.INFO)

    logging.info('start time:'+str(startTime))

    scale_factor=5
    convert_grey=config["super_resolution_to_segment"].value["convert_grey"]
    x_start,y_start = 0,0
    x_end,y_end=None,None
    pt_start,pt_end = 0, None



    ##Check number of .pt files
    all_sections=[]
    for name in config["slides"].items():
        all_sections.append(name[0])

    # all_sections=[os.path.join(os.path.join(current_path,'analyses/final/gene_maps',section)) for section in all_sections]

    print(all_sections)
    for section in all_sections:
        current_pt_path = os.path.join(current_path,'analyses/final/gene_maps',section)
        all_files=os.listdir(current_pt_path)
        img_path=config["slides"].value[section].value["data"]
        print('img path:',img_path)

        logging.info('Number of total files: '+str(len(all_files)))
        print('Number of total files: ',len(all_files))
        pt_files=[current_pt_path+'/'+f for f in all_files if f[-2:]=='pt']
        pt_files.sort()
        logging.info('Number of total .pt files: '+str(len(pt_files)))
        print('Number of total .pt files: ',len(pt_files))

        #Define Upsample function
        upSampleFunc=torch.nn.Upsample(scale_factor=scale_factor, mode='nearest')


        if x_end ==None or y_end==None:
            pt_file=torch.load(pt_files[0])
            print(np.shape(pt_file))
            pt_max=np.max(pt_file,axis=0)#Use max along 0th axis instead of avg
            # pt_max_tensor=torch.tensor(pt_max).view(1,1,pt_max.shape[0],pt_max.shape[1])#For some reason, torch.load() returns numpy array
            # pt_upsampled=upSampleFunc(pt_max_tensor)
            if x_end==None:
                x_end=np.shape(pt_max)[1]
            if y_end==None:
                y_end=np.shape(pt_max)[0]

        if pt_end==None:
            pt_end=len(pt_files)
        logging.info('pt files from '+str(pt_start)+' to '+str(pt_end)+' are considered')

        # tsv_name=args.main_name+'_'+str(args.scale_factor)+'_'+str(args.scale_factor*args.y_start)+':'+str(args.scale_factor*args.y_end)+'_'+str(args.scale_factor*args.x_start)+':'+str(args.scale_factor*args.x_end)+'_s'+str(args.pt_start)+'_e'+str(args.pt_end)
        tsv_name=os.path.join(segment_input_path,section)
        #Initialize with header
        with open(tsv_name+'.tsv','w') as f:
            f.write('geneID' + '\t' + 'x' + '\t' + 'y' + '\t' + 'MIDCounts' + '\n')
        f.close()


        with open(tsv_name+'.tsv','a') as f:

            for idx, fname in enumerate(pt_files):
                if idx<pt_start:
                    continue
                if idx>pt_end:
                    break

                # print(fname)
                pt_file=torch.load(fname)
                gene_name=fname.split('/')[-1].split('.')[0]
                pt_max=np.mean(pt_file,axis=0)
                print(gene_name, pt_max.shape)
                idx_x, idx_y = np.where(pt_max > 0)
                for i in range(len(idx_x)):
                    cur_x = idx_x[i]
                    cur_y = idx_y[i]
                    count = pt_max[cur_x, cur_y]
                    f.write(str(gene_name)+ '\t' +str(int(cur_x * scale_factor))+ '\t' +str(int(cur_y * scale_factor))+ '\t' +str(int(np.ceil(count)))+ '\n')

                logging.info(str(idx)+' '+str(fname)+' finished')
                print(str(idx)+' '+str(fname)+' finished')

        if img_path != None:
            bin_file = tsv_name+'.tsv'
            df = pd.read_table(bin_file)
            minx = df['x'].min()
            miny = df['y'].min()
            with h5py.File(img_path, "r") as data:
                img = (data["image"][()] + 1) / 2
                mask = data["label"][()] == 1
                img[mask] = 0.25 * img[mask]
                img = img * 255
                img = img.astype(np.uint8)

                print(img.shape)
                print(img)
                im = Image.fromarray(img)
            width, height = im.size
            width, height = width*5, height*5
            im = im.resize((width, height))
            if convert_grey==True:
                im = ImageOps.grayscale(im)
                im = ImageOps.invert(im)
            img2save = im.crop((miny, minx, width, height))

            img2save.save(os.path.join(segment_input_path,section+'.jpg'))
            logging.info(os.path.join(segment_input_path,section+'.jpg')+' saved')
            print(os.path.join(segment_input_path,section+'.jpg')+' saved')


    # logging.info('It took '+str(time.process_time()-startTime))
    # print('It took ',time.process_time()-startTime)

    # logging.info('Total time: '+str(time.process_time()))
    # print('Total time: ',time.process_time())

    # logging.info(args.pt_save_path+tsv_name+'.tsv' +' generated')
    # print(args.pt_save_path+tsv_name+'.tsv' +' generated')

    # logging.info('Completed')
    # print('Completed')
