from __future__ import print_function
import torch
import torch.nn.functional as F
from torchvision import datasets, transforms, models
import torch.utils.data.dataset
import numpy as np
from tqdm import tqdm

import pandas as pd
import utils


def predict(checkpoint, test_file, gpu_id=0):
    
    torch.cuda.set_device(gpu_id)
    
    model = models.densenet169(num_classes = 2).cuda()
    # Load the pretrained model
    model.load_state_dict(torch.load(checkpoint, map_location='cpu'))
    # Set the model in evaluation mode. In this case this is for the Dropout layers
    model.eval()
    
    normalize = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    dataset_test = utils.CSVDataset(
            test_file,
            transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                normalize,
            ]))
    test_loader = torch.utils.data.DataLoader(dataset_test, batch_size=32, shuffle=False, num_workers=4)
    
    probs = []
    targets = []
    
    for data, target in tqdm(test_loader):
        # Send the data and label to the device
        data, target = data.half().cuda(), target.cuda()

        # Forward pass the data through the model
        output = model(data)
        output = F.softmax(output, dim=1)
        
        probs.extend(output.detach().cpu().numpy())
        targets.extend(target.detach().cpu().numpy())
        
    return probs, targets
        
if __name__ == '__main__':
    pass