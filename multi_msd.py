import os
import imutils
import cv2
import numpy as np
import json
import matplotlib.pyplot as plt
import glob
import os
from PIL import Image
import concurrent.futures
import cv2

crop_root='/home/hana/Desktop/msd/crop/'
image_root='/home/hana/Desktop/msd/images/'
image_crop={}
image_crop['na']=[]

def find_image(image_file,crop_file):
    image_file_path=image_root+image_file
    crop_file_path=crop_root+crop_file
    main_image = cv2.imread(image_file_path)
    gray_image = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
    
    template = cv2.imread(crop_file_path)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template = cv2.Canny(template, 10, 25)
    (height, width) = template.shape[:2]
    
    temp_found = None
        #print(height,main_image.shape[0],width,main_image.shape[1])

    if(height<main_image.shape[0] and width<main_image.shape[1]):
        edge = cv2.Canny(gray_image, 10, 25)
        res=cv2.matchTemplate(edge,template,cv2.TM_CCOEFF_NORMED)
        loc=np.where(res>=0.5)
        if(np.array(loc).size==0):
            return 0                             #No match
        else:
            for scale in np.linspace(0.2, 1.0, 20)[::-1]:
                   #resize the image and store the ratio
                resized_img = imutils.resize(gray_image, width = int(gray_image.shape[1] * scale))
                ratio = gray_image.shape[1] / float(resized_img.shape[1])
                if resized_img.shape[0] < height or resized_img.shape[1] < width:
                    break
                   #Convert to edged image for checking
                edge = cv2.Canny(resized_img, 10, 25)
                match = cv2.matchTemplate(edge, template, cv2.TM_CCOEFF)
                (_, val_max, _, loc_max) = cv2.minMaxLoc(match)
                if temp_found is None or val_max>temp_found[0]:
                    temp_found = (val_max, loc_max, ratio)
                #Get information from temp_found to compute x,y coordinate
            (_, loc_max, r) = temp_found
            (x_start, y_start) = (int(loc_max[0]), int(loc_max[1]))
            (x_end, y_end) = (int((loc_max[0] + width)), int((loc_max[1] + height)))
                #Draw rectangle around the template
            cv2.rectangle(main_image, (x_start, y_start), (x_end, y_end), (153, 22, 0), 5)
            #plt.imshow(main_image)
            #print('SUCCESSFUL!!!')
            cv2.imwrite('/home/hana/Desktop/msd/assoc_full2/'+image_file.strip('.jpg')+'_'+crop_file.strip('.jpg')+'.jpg',main_image)
                #print((x_start, y_start),(x_end, y_end))
            value_dic=(crop_file,list((x_start, y_start))+list((x_end, y_end)))
                #if value_dic not in image_crop2[f]:
            #image_crop2[f].append(value_dic)
            return value_dic
    else:
        return -1

with concurrent.futures.ProcessPoolExecutor() as executor:
    crop_files = os.listdir(crop_root)
    for crop_file in crop_files:
        flag=True
        image_files=os.listdir(image_root)
        for image_file in image_files:
            if(image_file not in image_crop):
                image_crop[image_file]=[]
            results=executor.submit(find_image,image_file,crop_file)
            result=results.result()
            if(type(result)==tuple):
                image_crop[image_file].append(result)
                flag=False
        if flag==True:
            image_crop['na'].append(crop_file)
    print(image_crop)
