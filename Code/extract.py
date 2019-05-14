
# coding: utf-8

# In[28]:


import requests

contents=[]
i=0
with open('/home/hana/Desktop/msd/crops_url_list.txt',"r") as f:
    for link in f:
        contents.append(link[:-1])
        response=requests.get(contents[i])
        filename="/home/hana/Desktop/msd/crop/crops"+str(i)+".jpg"
        print(filename)
        with open(filename,"wb") as image_f:
            image_f.write(response.content)
        i=i+1

contents=[]
i=0
with open('/home/hana/Desktop/msd/images_url_list.txt',"r") as f:
    for link in f:
        contents.append(link[:-1])
        response=requests.get(contents[i])
        filename="/home/hana/Desktop/msd/images/images"+str(i)+".jpg"
        print(filename)
        with open(filename,"wb") as image_f:
            image_f.write(response.content)
        i=i+1

