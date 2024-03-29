import numpy as np
import json


import torch
from pycocotools.coco import COCO
import cv2
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader, TensorDataset

IMAGE_HEIGHT, IMAGE_WIDTH = 1280, 768

def extend_image(img, channels=None):
    height, width = img.shape[0], img.shape[1]
    delta = IMAGE_WIDTH - width
    if channels:
        padding = np.zeros((height, int(delta / 2), channels), np.uint8)
    else:
        padding = np.zeros((height, int(delta / 2)), np.uint8)
    img = np.concatenate((padding, img, padding), axis=1)
    return img


ann_dir = "Ingredients-11/train/_annotations.coco.json"
images_folder_path = "Ingredients-11/train/"

val_ann_dir = "Ingredients-11/valid/_annotations.coco.json"
val_images_folder_path = "Ingredients-11/valid/"






def load_data(ann_dir,images_folder_path):

    coco = COCO(ann_dir)

    image_ids = coco.getImgIds(imgIds=coco.getImgIds())

    images = []
    masks = []

    for img_id in image_ids:
        img_info = coco.loadImgs(ids=img_id)[0]
        image_path = f"{images_folder_path}/{img_info['file_name']}"
        image = plt.imread(image_path)

        ann_ids = coco.getAnnIds(imgIds=img_info['id'])
        annotations = coco.loadAnns(ann_ids)


        mask = np.zeros((img_info['height'], img_info['width']), dtype=np.uint8)
        for ann in annotations:
            if 'segmentation' not in ann or not ann['segmentation']:
                # Skip annotations with empty segmentations
                continue
            coco_mask = coco.annToMask(ann)
            mask = np.maximum(mask, coco_mask * ann['category_id'])

        image = extend_image(image, 3)
        mask = extend_image(mask)

        target_height = 448
        target_width = 448
        resized_img = cv2.resize(image, (target_width, target_height))
        resized_mask = cv2.resize(mask, (target_width, target_height))

        resized_mask = (resized_mask > 0).astype(np.uint8)

        images.append(resized_img)
        masks.append(resized_mask)
        #print(img_id)
    return images,masks


#training images and masks
tr_images,tr_masks = load_data(ann_dir,images_folder_path)

#Validation images and maks
val_images,val_masks = load_data(val_ann_dir,val_images_folder_path)




#Convert images and masks into numpy array
images_tr_np = np.array(tr_images)
masks_tr_np = np.array(tr_masks)
images_val_np = np.array(val_images)
masks_val_np = np.array(val_masks)


batch_size = 5

#load data
data_tr = DataLoader(TensorDataset(torch.tensor(np.rollaxis(images_tr_np, 3, 1)), torch.tensor(masks_tr_np[:, np.newaxis])),
                     batch_size=batch_size, shuffle=True)
data_val = DataLoader(TensorDataset(torch.tensor(np.rollaxis(images_val_np, 3, 1)), torch.tensor(masks_val_np[:, np.newaxis])),
                      batch_size=batch_size, shuffle=False)

