PyTorch code used to train a deep learning model for the diagnosis of Hashimoto's thyroiditis from thyroid ultrasound images.

Code brought from https://github.com/pytorch/vision/tree/master/references/classification.

The example was tested with with PyTorch (v1.7.1+cu101) and TorchVision (v0.8.2) on Ubuntu 16.04.5 and 20.04.2 LTS.

To run the example `train.sh` for each task, you need to install `pytorch` and `torchvision`.
For detail installation procedure, please refer to https://pytorch.org.

The example can be run without GPU. GPU cards are recommended to use if training with large-scale image data.

## 1. Installation (5 min)
```bash
pip install torch==1.7.1 torchvision==0.8.2 sklearn pandas
```

## 2. Git clone (1 min)
```bash
git clone https://github.com/lixiangchun/AIplus
```

## 3. Run HTNet example 
```bash
cd AIplus/HTNet

cd image-modality
bash train.sh

cd ../multi-modality
bash train.sh
```

## 4. Expected output
Model checkpoint file.

