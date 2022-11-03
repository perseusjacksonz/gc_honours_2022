#Import relevant libraries
import pandas as pd
import numpy as np
from datetime import datetime
from fileinput import filename
import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import glob
import re

#THIS FILE IS SIMILAR TO FINALCODE_ADDTEMPORALSCALES, BUT IS FOR THE PIXELS OUTSIDE OF THE CASESTUDY TIME AND AREA
#General directory of all collocated files
modis_input_dir_after15 = f"/home/565/pd8410/python/dtf/sem2_16_9_newcol"

#Create a list containing directories of all collocated files
modis_filename_after15=np.sort(glob.glob(modis_input_dir_after15+'/*.pkl'))

#Create an empty list for the date of the collocated files
modis_filename_datetime_list_after15=[]
for x in range(len(modis_filename_after15)):
    #Extract the date of each collocated file
    modis_filename_datetime_after15=datetime.strptime(re.search(r'\d{4}\d{2}\d{2}',modis_filename_after15[x]).group(), '%Y%m%d').date()
    #Add the extracted date to the empty list
    modis_filename_datetime_list_after15.append(modis_filename_datetime_after15)

#Create a dtf containing the directory and date of the collocated files
dtf_modis_after15=pd.DataFrame(list(zip(modis_filename_after15,modis_filename_datetime_list_after15)),columns=['modis_filename','time_diff'])
#Create a new column with just the months of the collocated files
dtf_modis_after15['month']=pd.DatetimeIndex(dtf_modis_after15.time_diff).month.tolist()
#Subset the months within the curing ramp up period (Sep-Feb) (plus Aug for extra room)
dtf_modis_after15_fireseason=dtf_modis_after15[dtf_modis_after15['month'].isin(list([8,9,10,11,1,2]))]

#Rows that were excluded from case study
rows=pd.read_pickle('/home/565/pd8410/python/obj_plots_sem2_newcol/casestudy_rows.pkl')

#Create a loop through case study days
for file in range(75,136):
    #Find collocated filename
    filename=dtf_modis_after15_fireseason.modis_filename.values[file]
    #Read collocated file as pandas dtf
    modisdtf=pd.read_pickle(filename)
    #Only select applicable rows/pixels from the case study days
    modisdtf=modisdtf.iloc[rows,]
    #Include first few important columns
    modisdtf=modisdtf[['y', 'x', 'curing', 'age', 'date', 'day_of_year']]

    #Create a 'day of cycle' column
    modisdtf['day_of_cycle']=''
    for i in range(len(modisdtf)):
        #Assign any August days to nan because we were not interested in this month
        if modisdtf.date.values[i].month==8:
            modisdtf['day_of_cycle'].values[i]=np.nan
        #For all of the other months, the day of year is calculated from the day of that month plus any how many days it is from September
        #Because Sep is the first month, the day of cycle is equal to the date of month
        elif modisdtf.date.values[i].month==9:
            modisdtf['day_of_cycle'].values[i]=modisdtf.date.values[i].day
        #Since Sep has 30 days, day of cycle in October is simply the date of month plus 30
        elif modisdtf.date.values[i].month==10:
            modisdtf['day_of_cycle'].values[i]=modisdtf.date.values[i].day+30
        #Similar reasoning to above, Oct has 31 days, day of cycle in November equals date of month plus 30 for Sep and 31 for Oct
        elif modisdtf.date.values[i].month==11:
            modisdtf['day_of_cycle'].values[i]=modisdtf.date.values[i].day+61
        elif modisdtf.date.values[i].month==12:
            modisdtf['day_of_cycle'].values[i]=modisdtf.date.values[i].day+91
        elif modisdtf.date.values[i].month==1:
            modisdtf['day_of_cycle'].values[i]=modisdtf.date.values[i].day+122
        else:
            modisdtf['day_of_cycle'].values[i]=modisdtf.date.values[i].day+153

    #This loop extracts information 4-7 days before the day that is used to predict
    #So if the day of prediction is t0, this looks at the week between t0-4 and t0-11, hence the (4,11) range
    for day in range(4,11):
        #This if condition checks if there exists data 4 (or up to 11 days or 1 week) prior to the day of prediction t0
        #If this is true
        if (dtf_modis_after15_fireseason.time_diff.values[file]-dtf_modis_after15_fireseason.time_diff.values[file-day])==timedelta(day):
            #Look for the collocated file x days before
            filename_other=dtf_modis_after15_fireseason.modis_filename.values[file-day]
            #Read as a separate pandas dataframe
            modisdtf_other=pd.read_pickle(filename_other)
            #Extract all the curing and meteorological variables
            modisdtf_other=modisdtf_other[['curing', 'sm','precip', 'max_temp', 'min_temp', 'max_relhum', 'min_relhum',
            'max_wind', 'min_wind', 'max_swrad', 'min_swrad', 'max_lwrad', 'min_lwrad']]
            #Calculate vpd
            modisdtf_other['vpd']=6.1078*np.exp((17.269*modisdtf_other.max_temp)/(237.3+modisdtf_other.max_temp))
            modisdtf_other['vpd']=modisdtf_other.vpd-((modisdtf_other.vpd*modisdtf_other.min_relhum)/100)
            #Add the suffix to signify the number of days prior to each variable
            modisdtf_other=modisdtf_other.add_suffix(('_'+'%d'+'day')%day)
            #Add all the columns to the current-day dtf
            modisdtf=pd.concat([modisdtf,modisdtf_other],axis=1)
        #If there is no data of any day of the past week
        else:
            #Create null columns in the current-day dtf
            modisdtf[['curing_%dday'%day, 'sm_%dday'%day,'precip_%dday'%day, 'max_temp_%dday'%day, 'min_temp_%dday'%day,
            'max_relhum_%dday'%day, 'min_relhum_%dday'%day,'max_wind_%dday'%day, 'min_wind_%dday'%day, 'max_swrad_%dday'%day,
            'min_swrad_%dday'%day, 'max_lwrad_%dday'%day, 'min_lwrad_%dday'%day, 'vpd_%dday'%day]]=np.nan

    #Create a list to calculate curing average 7 days
    curinglist=[]
    for day in range(4,11):
        #Select all the curing columns of everyday of the entire week
        curing='curing_%dday'%day
        #Append all the curing values of the 7 days to the list
        curinglist.append(curing)
    #Create a column in the current-day dtf
    #Calculate the average of the 7 curing values from the previous list
    modisdtf['curing_avg_7day']=modisdtf[curinglist].mean(axis=1)

    #7-day average soil moisture (same as above)
    smlist=[]
    for day in range(4,11):
        sm='sm_%dday'%day
        smlist.append(sm)
    modisdtf['sm_avg_7day']=modisdtf[smlist].mean(axis=1)

    #7-day average precipitation (same as above)
    preciplist=[]
    for day in range(4,11):
        precip='precip_%dday'%day
        preciplist.append(precip)
    modisdtf['precip_avg_7day']=modisdtf[preciplist].mean(axis=1)

    #7-day average max temp (same as above)
    max_templist=[]
    for day in range(4,11):
        max_temp='max_temp_%dday'%day
        max_templist.append(max_temp)
    modisdtf['max_temp_avg_7day']=modisdtf[max_templist].mean(axis=1)

    #7-day average min temp (same as above)
    min_templist=[]
    for day in range(4,11):
        min_temp='min_temp_%dday'%day
        min_templist.append(min_temp)
    modisdtf['min_temp_avg_7day']=modisdtf[min_templist].mean(axis=1)

    #7-day average min relative humidity (same as above)
    min_relhumlist=[]
    for day in range(4,11):
        min_relhum='min_relhum_%dday'%day
        min_relhumlist.append(min_relhum)
    modisdtf['min_relhum_avg_7day']=modisdtf[min_relhumlist].mean(axis=1)

    #7-day average max relative humidity (same as above)
    max_relhumlist=[]
    for day in range(4,11):
        max_relhum='max_relhum_%dday'%day
        max_relhumlist.append(max_relhum)
    modisdtf['max_relhum_avg_7day']=modisdtf[max_relhumlist].mean(axis=1)

    #7-day average max wind speed (same as above)
    max_windlist=[]
    for day in range(4,11):
        max_wind='max_wind_%dday'%day
        max_windlist.append(max_wind)
    modisdtf['max_wind_avg_7day']=modisdtf[max_windlist].mean(axis=1)

    #7-day average min wind speed (same as above)
    min_windlist=[]
    for day in range(4,11):
        min_wind='min_wind_%dday'%day
        min_windlist.append(min_wind)
    modisdtf['min_wind_avg_7day']=modisdtf[min_windlist].mean(axis=1)

    #7-day average min shortwave radiation (same as above)
    min_swradlist=[]
    for day in range(4,11):
        min_swrad='min_swrad_%dday'%day
        min_swradlist.append(min_swrad)
    modisdtf['min_swrad_avg_7day']=modisdtf[min_swradlist].mean(axis=1)

    #7-day average max shortwave radiation (same as above)
    max_swradlist=[]
    for day in range(4,11):
        max_swrad='max_swrad_%dday'%day
        max_swradlist.append(max_swrad)
    modisdtf['max_swrad_avg_7day']=modisdtf[max_swradlist].mean(axis=1)

    #7-day average max longwave radiation (same as above)
    max_lwradlist=[]
    for day in range(4,11):
        max_lwrad='max_lwrad_%dday'%day
        max_lwradlist.append(max_lwrad)
    modisdtf['max_lwrad_avg_7day']=modisdtf[max_lwradlist].mean(axis=1)

    #7-day average min longwave radiation (same as above)
    min_lwradlist=[]
    for day in range(4,11):
        min_lwrad='min_lwrad_%dday'%day
        min_lwradlist.append(min_lwrad)
    modisdtf['min_lwrad_avg_7day']=modisdtf[min_lwradlist].mean(axis=1)

    #7-day average vpd (same as above)
    vpdlist=[]
    for day in range(4,11):
        vpd='vpd_%dday'%day
        vpdlist.append(vpd)
    modisdtf['vpd_avg_7day']=modisdtf[vpdlist].mean(axis=1)

    #Calculate 4-day average
    #Similar idea to calculate 7-day average, but instead of range(4,11), change to range(4,8)
    curinglist=[]
    for day in range(4,8):
        curing='curing_%dday'%day
        curinglist.append(curing)
    modisdtf['curing_avg_4day']=modisdtf[curinglist].mean(axis=1)

    smlist=[]
    for day in range(4,8):
        sm='sm_%dday'%day
        smlist.append(sm)
    modisdtf['sm_avg_4day']=modisdtf[smlist].mean(axis=1)

    preciplist=[]
    for day in range(4,8):
        precip='precip_%dday'%day
        preciplist.append(precip)
    modisdtf['precip_avg_4day']=modisdtf[preciplist].mean(axis=1)

    max_templist=[]
    for day in range(4,8):
        max_temp='max_temp_%dday'%day
        max_templist.append(max_temp)
    modisdtf['max_temp_avg_4day']=modisdtf[max_templist].mean(axis=1)

    min_templist=[]
    for day in range(4,8):
        min_temp='min_temp_%dday'%day
        min_templist.append(min_temp)
    modisdtf['min_temp_avg_4day']=modisdtf[min_templist].mean(axis=1)

    min_relhumlist=[]
    for day in range(4,8):
        min_relhum='min_relhum_%dday'%day
        min_relhumlist.append(min_relhum)
    modisdtf['min_relhum_avg_4day']=modisdtf[min_relhumlist].mean(axis=1)

    max_relhumlist=[]
    for day in range(4,8):
        max_relhum='max_relhum_%dday'%day
        max_relhumlist.append(max_relhum)
    modisdtf['max_relhum_avg_4day']=modisdtf[max_relhumlist].mean(axis=1)

    max_windlist=[]
    for day in range(4,8):
        max_wind='max_wind_%dday'%day
        max_windlist.append(max_wind)
    modisdtf['max_wind_avg_4day']=modisdtf[max_windlist].mean(axis=1)

    min_windlist=[]
    for day in range(4,8):
        min_wind='min_wind_%dday'%day
        min_windlist.append(min_wind)
    modisdtf['min_wind_avg_4day']=modisdtf[min_windlist].mean(axis=1)

    min_swradlist=[]
    for day in range(4,8):
        min_swrad='min_swrad_%dday'%day
        min_swradlist.append(min_swrad)
    modisdtf['min_swrad_avg_4day']=modisdtf[min_swradlist].mean(axis=1)

    max_swradlist=[]
    for day in range(4,8):
        max_swrad='max_swrad_%dday'%day
        max_swradlist.append(max_swrad)
    modisdtf['max_swrad_avg_4day']=modisdtf[max_swradlist].mean(axis=1)

    max_lwradlist=[]
    for day in range(4,8):
        max_lwrad='max_lwrad_%dday'%day
        max_lwradlist.append(max_lwrad)
    modisdtf['max_lwrad_avg_4day']=modisdtf[max_lwradlist].mean(axis=1)

    min_lwradlist=[]
    for day in range(4,8):
        min_lwrad='min_lwrad_%dday'%day
        min_lwradlist.append(min_lwrad)
    modisdtf['min_lwrad_avg_4day']=modisdtf[min_lwradlist].mean(axis=1)

    vpdlist=[]
    for day in range(4,8):
        vpd='vpd_%dday'%day
        vpdlist.append(vpd)
    modisdtf['vpd_avg_4day']=modisdtf[vpdlist].mean(axis=1)

    #Only include curing observations smaller than 100
    modisdtf=modisdtf[modisdtf.curing<=100]
    modisdtf=modisdtf[modisdtf.curing_4day<=100]
    modisdtf=modisdtf[modisdtf.curing_5day<=100]
    modisdtf=modisdtf[modisdtf.curing_6day<=100]
    modisdtf=modisdtf[modisdtf.curing_7day<=100]
    modisdtf=modisdtf[modisdtf.curing_8day<=100]
    modisdtf=modisdtf[modisdtf.curing_9day<=100]
    modisdtf=modisdtf[modisdtf.curing_10day<=100]
    modisdtf=modisdtf[modisdtf.curing_avg_7day<=100]
    modisdtf=modisdtf[modisdtf.curing_avg_4day<=100]
    #Only include curing observations with age equals zero (current)
    modisdtf=modisdtf[modisdtf.age==0]
    #Exclude null day of cycle (i.e. August)
    modisdtf=modisdtf[~modisdtf.day_of_cycle.isnull()]

    #Save daily updated dtf to this directory
    modisdtf.to_pickle('/home/565/pd8410/python/dtf/dtfappend_newcol/dtfappend%d.pkl'%file)