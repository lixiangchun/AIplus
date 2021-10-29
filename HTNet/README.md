PyTorch code used to train a deep learning model for diagnosis of Hashimoto's thyroiditis.

Code brought from https://github.com/pytorch/vision/tree/master/references/classification.

Input images of the training and validation sets should formatted as:

```
"image_name","label"
"/path/007.JPG.jpg","0"
"/path/008.JPG.jpg","1"
"/path/009.JPG.jpg","0"
```

Input serologic markers should be formatted as:
```
"Tg","Anti-TG","Anti-TPO","T3","T4","TSH","hashimoto_thyroiditis"
-0.26380272762554,-0.238465658062414,-0.374412141392311,0.0643314308658453,-0.0465540940528935,-0.0410740731720667,"0"
-0.397043270425712,-0.15253655393608,-0.328088481454276,0.137256299621006,-0.0100594855956962,0.027140818668468,"1"
```

