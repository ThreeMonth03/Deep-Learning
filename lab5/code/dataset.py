import torch
import os
import numpy as np
import csv
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image

default_transform = transforms.Compose([
    transforms.ToTensor(),
    ])
'''
class bair_robot_pushing_dataset(Dataset):
    def __init__(self, args, mode='train', transform=default_transform):
        assert mode == 'train' or mode == 'test' or mode == 'validate'
        self.mode = mode
        self.transform = default_transform
        self.root_path = args.data_root
        self.seq_len = args.n_past + args.n_future
        self.dir_list=[]
        for d1 in os.listdir('%s/%s' % (self.root_path, mode)):
            for d2 in os.listdir('%s/%s/%s' % (self.root_path, mode, d1)):
                self.dir_list.append('%s/%s/%s/%s' % (self.root_path, mode, d1, d2))
        self.count=0
        self.getitem_dir=''
        
    def set_seed(self,seed):
        if not self.seed_is_set:
            self.seed_is_set = True
            np.random.seed(seed)
            
    def __len__(self):
        return len(self.dir_list)
        
    def get_seq(self):
        img_list = []
        if (mode== 'test') or  (mode=='validate'):
            self.getitem_dir = self.dir_list[count]
            self.count = (self.count+1)%len(self.png_csv_path)
        else:
            self.getitem_dir = dir_list[np.random.randint(len(self.png_csv_path))]
        for i in range (self.seq_len):
            pre_img = Image.open('%s/%d.png'% (self.getitem_dir, i))
            img = self.transform(pre_img)
            img_list.append(img)
        img_list = torch.stack(img_list,0)
        return img_list                     
    
    def get_csv(self):
        csv_list=[]
        with open("%s/%s.csv" % (self.getitem_dir, 'actions'), newline='') as csv_file:
            actions_rows = csv.reader(csv_file)
            actions_rows = list(actions_rows)
        with open("%s/%s.csv" % (self.getitem_dir, 'endeffector_positions'), newline='') as csvfile:
            endeffector_positions_rows = csv.reader(csvfile)
            endeffector_positions_rows = list(endeffector_positions_rows)
        for i in range(self.seq_len):
            a_float = [float(a) for a in actions_rows[i]]
            e_float = [float(e) for e in endeffector_positions_rows[i]]
            cond = torch.Tensor(a_float + e_float)
            csv_list.append(cond)
        csv_list = torch.stack(csv_list,0)
        return csv_list
    
    def __getitem__(self, index):
        self.set_seed(index)
        seq = self.get_seq()
        cond =  self.get_csv()
        return seq, cond
'''
class bair_robot_pushing_dataset(Dataset):
    def __init__(self, args, mode='train', transform=default_transform):
        assert mode == 'train' or mode == 'test' or mode == 'validate'
        self.root_path = args.data_root
        if mode == "train":
            self.data_path = os.path.join(self.root_path, "train")
            self.ordered = False
        elif mode == "validate":
            self.data_path = os.path.join(self.root_path, "validate")
            self.ordered = True
        elif mode == "test":
            self.data_path = os.path.join(self.root_path, "test")
            self.ordered = True
        self.png_csv_path = []
        for dir1 in os.listdir(self.data_path):
            for dir2 in os.listdir(os.path.join(self.data_path, dir1)):
                    self.png_csv_path.append(os.path.join(self.data_path, dir1, dir2))
        self.seq_len = args.n_past + args.n_future
        self.csv_len = 2
        self.img_size = 64
        self.seed_is_set = False
        self.dir_num = 0
        self.transform = transform
        self.dir_name = ''
        
    def set_seed(self, seed):
        if not self.seed_is_set:
            self.seed_is_set = True
            np.random.seed(seed)
            
    def __len__(self):
        return len(self.png_csv_path)
        
    def get_seq(self):
        if self.ordered == True:
            self.dir_name = self.png_csv_path[self.dir_num]
            if self.dir_num == len(self.png_csv_path) - 1:
                self.dir_num = 0
            else:
                self.dir_num += 1
        else:
            self.dir_name = self.png_csv_path[np.random.randint(len(self.png_csv_path))]
        imgs = []
        for i in range(self.seq_len):
            png_name = "%s/%d.png" % (self.dir_name, i)
            image = Image.open(png_name)
            img = self.transform(image)
            imgs.append(img)
        imgs = torch.stack((imgs))
        return imgs
    
    def get_csv(self):
        csvs = []
        csv_name = "%s/%s.csv" % (self.dir_name, 'actions')
        with open(csv_name, newline='') as csvfile:
            a_rows = csv.reader(csvfile)
            a_rows = list(a_rows)
        csv_name = "%s/%s.csv" % (self.dir_name, 'endeffector_positions')
        with open(csv_name, newline='') as csvfile:
            e_rows = csv.reader(csvfile)
            e_rows = list(e_rows)
        for i in range(self.seq_len):
            af = [float(a) for a in a_rows[i]]
            ef = [float(e) for e in e_rows[i]]
            cond = torch.Tensor(af + ef)
            csvs.append(cond)
        csvs = torch.stack((csvs))
        return csvs
    
    def __getitem__(self, index):
        self.set_seed(index)
        seq = self.get_seq()
        cond = self.get_csv()
        return seq, cond
