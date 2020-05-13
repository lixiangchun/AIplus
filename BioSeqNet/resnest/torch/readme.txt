Replace `2d` with `1d`.

resnet.py
Add `num_channels=4` as the an argument of `class ResNet` and replace `conv_layer(3,` with `conv_layer(num_channels,`

splat.py
Replace `stride=(1,1)` with `stride=1`, `padding=(0,0)` with `padding=0`, `dilation=(1,1)` with `dilation=1`

Replace `self.rectify = rectify and (padding[0] > 0 or padding[1] > 0)` with `self.rectify = rectify and (padding > 0)`

Replace `atten = self.rsoftmax(atten).view(batch, -1, 1, 1)` with `atten = self.rsoftmax(atten).view(batch, -1, 1)`

