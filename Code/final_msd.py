#Import all the necessary packages installed using: pip install -r requirements.txt
import numpy as np
import os		
import cv2
import json
import matplotlib.pyplot as plt
#%matplotlib inline	#Remove hash when the code is run in Interactive Notebook
import imutils		#library to resize images

def find_association(crop_root,image_root):
	"""Summary or Description of the Function find_association
		Function to associate images with crops
		Parameters:
			crop_root (string): Root folder of the crops
			image_root (string): Root folder of the images


		Returns:
			dictionary: Images associated with crops
	"""
	image_crop_dictionary={}
	image_crop_dictionary['na']=[]
	#Add the path of the required target folder to store the associated images-crops
	associated_images_target='/home/hana/Desktop/msd_task_folder/images_crops_associated/'
	
	for crop_file in os.listdir(crop_root):
		#Open crop as template, convert into grayscale and get edge using canny edge detection	
		template = cv2.imread(crop_root+crop_file)
		template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
		template = cv2.Canny(template, 10, 25)
		(height, width) = template.shape[:2]
		flag=True	#flag to check if a crop is associated with any image or not

		for image_file in os.listdir(image_root):
			if image_file not in image_crop_dictionary:
				image_crop_dictionary[image_file]=[]
				
			#Open image as main_image,convert into grayscale
			main_image = cv2.imread(image_root+image_file)
			gray_image = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
			temp_found = None
			
			#Check for association only if template's width and height are smaller than that of the image
			if(height<main_image.shape[0] and width<main_image.shape[1]):
				edge_main_image = cv2.Canny(gray_image, 10, 25)
			    #Match the template on main_image using Opencv's Template Matching Algorithm
				match=cv2.matchTemplate(edge_main_image,template,cv2.TM_CCOEFF_NORMED)
				location=np.where(match>=0.5)		
			    #0.5 is the threshold value
			    
				if(np.array(location).size!=0):
				#This part is executed is when match is found with given threshold value
				#This implements Multi-scale Template Matching to get accurate location of the template in the main image
					for scale in np.linspace(0.2, 1.0, 20)[::-1]:
						#resize the image and store the ratio
						resized_img = imutils.resize(gray_image, width = int(gray_image.shape[1] * scale))
						ratio = gray_image.shape[1] / float(resized_img.shape[1])
						
						#If resized image becomes smaller than the template then break
						if resized_img.shape[0] < height or resized_img.shape[1] < width:
							break
						#Convert to edged image for checking
						edge_main_image = cv2.Canny(resized_img, 10, 25)
						match = cv2.matchTemplate(edge_main_image, template, cv2.TM_CCOEFF)
						(_, val_max, _, loc_max) = cv2.minMaxLoc(match)
						if temp_found is None or val_max>temp_found[0]:
							temp_found = (val_max, loc_max, ratio)
							
						#Get information from temp_found to compute x,y coordinate
						(_, loc_max, ratio) = temp_found
						(left_top_x, left_top_y) = (int(loc_max[0]), int(loc_max[1]))
						(right_bottom_x, right_bottom_y) = (int((loc_max[0] + width)), int((loc_max[1] + height)))
						#Draw rectangle around the template
						cv2.rectangle(main_image, (left_top_x, left_top_y), (right_bottom_x, right_bottom_y), (255, 0, 0), 5)
						#plt.imshow(main_image)
						#Uncomment the following statement to write the associated image to the target folder
						#cv2.imwrite(associated_images_target+image_file.strip('.jpg')+'-'+crop_file.strip('.jpg')+'.jpg',main_image)
						value_tuple=(crop_file,list((left_top_x, left_top_y))+list((right_bottom_x, right_bottom_y)))
						image_crop_dictionary[image_file].append(value_tuple)
						flag=False
						
		if flag==True:
			#If the crop does not get matched with any image,append it to 'na'
			image_crop_dictionary['na'].append((crop_file,[]))
		
	return image_crop_dictionary
	
def visualise(image_crop_dictionary):
	"""Summary or Description of the Function visualise
		Function to visualise the obtained results
		Parameters:
			image_crop_dictionary(dictionary): dictionary that has images associated with crops
		Returns:
			None
	"""
	dict_stats={}
	destination_folder='/home/hana/Desktop/msd_task_folder/'
	dict_stats['Crops_with_no_images']=sum(len(v) for k,v in image_crop_dictionary.items() if k=='na')        

	count=0
	for key,value in image_crop_dictionary.items():
		if value==[]:
			count=count+1 
	dict_stats['Images_with_no_crops']=count       

	count=0
	for key,value in image_crop_dictionary.items():
		if (key!='na' and value!=[]):
			count=count+1
	dict_stats['Images_with_crops']=count

	X=list(dict_stats.keys())
	Y=list(dict_stats.values())

	chart=plt.figure()
	plt.bar(X,Y,align='center',alpha=0.5)
	plt.ylabel('Number of Images')
	#plt.show()
	chart.savefig(destination_folder+'output_chart.jpg',dpi=chart.dpi)
	
if __name__=="__main__":
	result_dictionary={}
	#Root folder for crops
	crop_root='/home/hana/Desktop/msd/crop/' 
	#Root folder for images	
	image_root='/home/hana/Desktop/msd/images/' 
	#Root folder to store the json output	
	target='/home/hana/Desktop/msd_task_folder/' 
	#Call find_association to find association between images and crops 
	result_dictionary=find_association(crop_root,image_root)
	#call visualise to visualise the obtained results
	visualise(result_dictionary)

	output=json.dumps(result_dictionary)
	output_json_file='imagesCropsAssociation.json'
	with open(target+output_json_file,"w+") as f:
    		f.write(output)
	f.close()
			    
