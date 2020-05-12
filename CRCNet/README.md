PyTorch code used to train CRCNet.

Code brought from https://github.com/pytorch/vision/tree/master/references/classification.

To use focal loss for training, you need to install `pytorch_toolbelt`:
```
pip install pytorch_toolbelt
```

See `train.sh` for how to train on your own data sets. An example of `trn.csv` and `val.csv`
looks like:

```
"image_name","tags"
"/path/007.JPG.jpg","benign"
"/path/008.JPG.jpg","malignant"
"/path/009.JPG.jpg","benign"
```

