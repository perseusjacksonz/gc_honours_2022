#Import libraries
import pandas as pd
import numpy as np
import glob

#General directory of all the files with added temporal scales
modis_input_dir_after15 = f"/home/565/pd8410/python/dtf/dtfappend_newcol"

#Create a list of all those directories
modis_filename_after15=np.sort(glob.glob(modis_input_dir_after15+'/*.pkl'))

#Create an empty list
emptydtf=[]
#Create a loop to go through each directory
for file in modis_filename_after15:
    #Read the file as a pandas dtf
    modisdtf=pd.read_pickle(file)
    #Append the pandas dtf to the empty list
    emptydtf.append(modisdtf)

#Concat all the dtfs in the empty list together into one big dtf
#This is the input dataset to be splitted into training and testing sub-datasets
modisdtf=pd.concat(emptydtf)

#Save input dataset
modisdtf.to_pickle('/home/565/pd8410/python/dtf/dtfappend_versions/dtfappend_newcol.pkl')

#The following part is optional, but it creates an input dataset with no null values
modisdtf=modisdtf.dropna()

#Save no-null input dataset
modisdtf.to_pickle('/home/565/pd8410/python/dtf/dtfappend_versions/dtfappend_nonull_newcol.pkl')
