from params import *
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
import time
import datetime


ch = 128

class ConvBlock(nn.Module):
    def __init__(self, in_ch):
        super(ConvBlock, self).__init__()
        self.conv = nn.Conv2d(in_ch, ch, kernel_size=3, stride=1, padding=1)
        self.bn = nn.BatchNorm2d(ch)
        self.actv = nn.ReLU()

    def forward(self, x):
        x = self.actv(self.bn(self.conv(x)))
        return x


class ResidualBlock(nn.Module):
    def __init__(self):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(ch, ch, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(ch)
        self.conv2 = nn.Conv2d(ch, ch, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(ch)
        self.actv = nn.ReLU()
    
    def forward(self, x):
        h = self.actv(self.bn1(self.conv1(x)))
        h = self.bn2(self.conv2(h))
        x = x + h
        x = self.actv(x)
        return x


class PolicyHead(nn.Module):
    def __init__(self, board_size, output_size):
        super(PolicyHead, self).__init__()
        self.conv = nn.Conv2d(ch, 2, kernel_size=1, stride=1)
        self.bn = nn.BatchNorm2d(2)
        self.actv = nn.ReLU()
        self.fc = nn.Linear(2*(board_size**2), output_size)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = self.actv(self.bn(self.conv(x)))
        x = x.view(x.shape[0], -1)
        x = self.fc(x)
        x = self.softmax(x)
        return x


class ValueHead(nn.Module):
    def __init__(self, board_size):
        super(ValueHead, self).__init__()
        self.conv = nn.Conv2d(ch, 1, kernel_size=1, stride=1)
        self.bn = nn.BatchNorm2d(1)
        self.actv = nn.ReLU()
        self.fc1 = nn.Linear(board_size**2, ch)
        self.fc2 = nn.Linear(ch, 1)
        self.tanh = nn.Tanh()

    def forward(self, x):
        x = self.actv(self.bn(self.conv(x)))
        x = x.view(x.shape[0], -1)
        x = self.actv(self.fc1(x))
        x = self.tanh(self.fc2(x))
        return x


class PlayDataset(Dataset):
    def __init__(self, X, pi, Z):
        self.X = X
        self.pi = pi
        self.Z = Z
        #print('??',len(X), len(pi), len(Z))
    
    def __getitem__(self, index):
        return self.X[index], self.pi[index], self.Z[index]

    def __len__(self):
        return len(self.X)


class Network(nn.Module):
    def __init__(self, board_size, input_frame_num, residual_num, is_trainable):
        super(Network, self).__init__()
        
        self.board_size = board_size
        self.input_frame_num = input_frame_num
        self.residual_num = residual_num
         
        self.conv = ConvBlock(input_frame_num)
        self.res_blocks = nn.ModuleList()
        for i in range(self.residual_num):
            self.res_blocks += [ResidualBlock()]
        self.P = PolicyHead(board_size, board_size**2)
        self.V = ValueHead(board_size)

        def SoftCrossEntopyLoss(predicted, target):
            return -(target * torch.log(predicted)).sum(dim=1).mean()
        self.policy_loss = SoftCrossEntopyLoss
        self.value_loss = nn.MSELoss()

        
        self.is_trainable = is_trainable
        if is_trainable != True:
            #self.saver.restore(self.sess,"./AlphaGomoku.ckpt")
            pass

    def forward(self, x):
        x = self.conv(x)
        for res_block in self.res_blocks:
            x = res_block(x)
        P = self.P(x)
        V = self.V(x)
        return P, V

    def train_model(self, X_, pi_, Z_, TOTAL_EPOCH, it):
        if self.is_trainable:
            dataset = PlayDataset(X_, pi_, Z_)
            loader = DataLoader(dataset=dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
            
            self.train()
            opt = torch.optim.Adam(self.parameters(), lr=0.000001, weight_decay=1e-4)
            for epoch in range(TOTAL_EPOCH):
                for X, pi, Z in loader:
                    X = X.cuda()
                    pi = pi.cuda()
                    Z = Z.cuda()
                    P, V = self(X)
                    p_loss = self.policy_loss(P, pi)
                    v_loss = self.value_loss(V, Z)
                    loss = p_loss + v_loss
                    opt.zero_grad()
                    loss.backward()
                    opt.step()
                    
                print('epoch: ', epoch, ' loss: ' , loss.item(), ' policy loss: ', p_loss.item(), ' value loss: ', v_loss.item(), flush=True)

            if True: #it % 10 == 0:
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
                #save_path = self.saver.save(self.sess,"./AlphaGomoku_"+st+".ckpt")
                save_path = ('./%5d' % it) + st + '.ckpt'
                torch.save({
                    'model': self.state_dict(),
                    'optimizer': opt.state_dict(),
                    'it': it,
                }, save_path)

    def get_output(self, X):
        #X = torch.tensor(X).float().cuda()
        P, V = self(X)
        #P = P.cpu().detach().numpy() 
        #V = V.cpu().detach().numpy() 
        return P, V

