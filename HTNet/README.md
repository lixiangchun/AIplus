PyTorch code used to train a deep learning model for diagnosis of Hashimoto's thyroiditis.

Code brought from https://github.com/pytorch/vision/tree/master/references/classification.

Input images of the training and validation sets should formatted as:

To run the example `train.sh` in for each task, you need to install pytorch (https://pytorch.org).

The example was tested with with PyTorch (v1.7.1+cu101) and TorchVision (v0.8.2) on Ubuntu 16.04.5 and 20.04.2 LTS.


```
"image_name","label"
"/path/007.JPG.jpg","0"
"/path/008.JPG.jpg","1"
"/path/009.JPG.jpg","0"
```

Input serologic markers should be formatted as:
```
"Tg","Anti-TG","Anti-TPO","T3","T4","TSH","hashimoto_thyroiditis"
-0.2638,-0.2384,-0.374,0.064,-0.046,-0.04,"0"
-0.3970,-0.1525,-0.328,0.137,-0.010,0.027,"1"
```

