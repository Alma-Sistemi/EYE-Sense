_base_ = './faster_rcnn_orpn_r50_fpn_1x_ms_rr_dota10.py'

# model
model = dict(pretrained='torchvision://resnet101', backbone=dict(depth=101))

config = './OBBDetection/configs/obb/oriented_rcnn/faster_rcnn_orpn_r101_fpn_1x_ms_rr_dota10.py'
checkpoint = './resources/model/faster_rcnn_orpn_r101_fpn_1x_mssplit_rr_dota10_epoch12.pth'