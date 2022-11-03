#Import libraries
from netCDF4 import Dataset as NetCDFFile
import geopandas as gpd
import pandas as pd
import xarray as xr
import numpy as np
from datetime import datetime
import pandas as pd
import geopandas as gpd
import numpy as np
import glob
import re

#Create a list containing all MODIS files' directory (start from 2015-06-14)
modis_input_dir_after15 = f"/g/data/ct18/Historical_Curing/BOM_raw_daily_input_for_VISCA/unzipped/vic"
modis_filename_after15=np.sort(glob.glob(modis_input_dir_after15+'/*.tif'))

#Extract date (YYYY/MM/DD) from each MODIS directory
modis_filename_datetime_list_after15=[]
for x in range(len(modis_filename_after15)):
    modis_filename_datetime_after15=datetime.strptime(re.search(r'\d{4}\d{2}\d{2}',modis_filename_after15[x]).group(), '%Y%m%d').date()
    modis_filename_datetime_list_after15.append(modis_filename_datetime_after15)

#Create a dtf of MODIS directory and date
dtf_modis_after15=pd.DataFrame(list(zip(modis_filename_after15,modis_filename_datetime_list_after15)),columns=['modis_filename','time_diff'])

#Limit the year to be up to 2018 and the month to be the curing ramp up period (Sep-Feb, plus August to ensure that Sep data points are fully collocated)
dtf_modis_after15=dtf_modis_after15[dtf_modis_after15['time_diff']<pd.Timestamp(2019,1,1)]
dtf_modis_after15['month']=pd.DatetimeIndex(dtf_modis_after15.time_diff).month.tolist()
dtf_modis_after15=dtf_modis_after15[dtf_modis_after15['month'].isin(list([8,9,10,11,12,1,2]))]

#Create a list containing all MODIS Age files' directory (start from 2015-06-14)
modis_age_input_dir_after15 = f"/home/565/pd8410/python/dtf/unzip_modis_age_files"
modis_age_filename_after15=np.sort(glob.glob(modis_age_input_dir_after15+'/*.tif'))

#Extract date (YYYY/MM/DD) from each MODIS Age directory
modis_age_filename_datetime_list_after15=[]
for x in range(len(modis_age_filename_after15)):
    modis_age_filename_datetime_after15=datetime.strptime(re.search(r'\d{4}\d{2}\d{2}',modis_age_filename_after15[x]).group(), '%Y%m%d').date()
    modis_age_filename_datetime_list_after15.append(modis_age_filename_datetime_after15)

#Create a dtf of MODIS Age directory and date
dtf_modis_age_after15=pd.DataFrame(list(zip(modis_age_filename_after15,modis_age_filename_datetime_list_after15)),columns=['modis_age_filename','time_diff'])

#Limit the year to be up to 2018
dtf_modis_age_after15=dtf_modis_age_after15[dtf_modis_age_after15['time_diff']<pd.Timestamp(2019,1,1)]

#Merge the two MODIS directory and age dtf
dtf_modis_after15=pd.merge(dtf_modis_after15,dtf_modis_age_after15,on='time_diff')

#BARRA directory
#Any BARRA directory is fine, this is just for extracting the lat and lon which should be the same for all BARRA-R_v1
barra_input_dir = '/g/data/cj37/BARRA/BARRA_R/v1/analysis/spec/sfc_temp/2008/01/sfc_temp-an-spec-PT0H-BARRA_R-v1-20080101T0000Z.nc'
#Read BARRA NetCDFFile
ncdf_BARRA=NetCDFFile(barra_input_dir)
#Extract the lat and lon of BARRA
lat_BARRA=ncdf_BARRA.variables['latitude'][:]
lon_BARRA=ncdf_BARRA.variables['longitude'][:]

#BARRA directory for each variable
temp_input_dir = f"/g/data/cj37/BARRA/BARRA_R/v1/analysis/spec/sfc_temp"
relhum_input_dir = f"/g/data/cj37/BARRA/BARRA_R/v1/analysis/prs/relhum"
uwind_input_dir = f"/g/data/cj37/BARRA/BARRA_R/v1/analysis/spec/uwnd10m"
vwind_input_dir = f"/g/data/cj37/BARRA/BARRA_R/v1/analysis/spec/vwnd10m"
lwrad_input_dir = f"/g/data/cj37/BARRA/BARRA_R/v1/analysis/slv/av_lwsfcdown"
swrad_input_dir = f"/g/data/cj37/BARRA/BARRA_R/v1/analysis/slv/av_swsfcdown"

#Create a list of BARRA directory for each variable within the curing ramp up period (Sep-Feb) from 2015-2018
temp_filename_list=[]
relhum_filename_list=[]
uwind_filename_list=[]
vwind_filename_list=[]
lwrad_filename_list=[]
swrad_filename_list=[]
for year in range(2015,2019):
    for month in range(1,13):
        temp_filename=glob.glob(temp_input_dir+'/'+f'{year}'+'/'+f'{month:02d}'+'/*.nc')
        temp_filename_list.append(temp_filename)
        relhum_filename=glob.glob(relhum_input_dir+'/'+f'{year}'+'/'+f'{month:02d}'+'/*.nc')
        relhum_filename_list.append(relhum_filename)
        uwind_filename=glob.glob(uwind_input_dir+'/'+f'{year}'+'/'+f'{month:02d}'+'/*.nc')
        uwind_filename_list.append(uwind_filename)
        vwind_filename=glob.glob(vwind_input_dir+'/'+f'{year}'+'/'+f'{month:02d}'+'/*.nc')
        vwind_filename_list.append(vwind_filename)
        lwrad_filename=glob.glob(lwrad_input_dir+'/'+f'{year}'+'/'+f'{month:02d}'+'/*.nc')
        lwrad_filename_list.append(lwrad_filename)
        swrad_filename=glob.glob(swrad_input_dir+'/'+f'{year}'+'/'+f'{month:02d}'+'/*.nc')
        swrad_filename_list.append(swrad_filename)

#Sort the BARRA directories
temp_filename_list=np.sort(sum(temp_filename_list,[]))
relhum_filename_list=np.sort(sum(relhum_filename_list,[]))
uwind_filename_list=np.sort(sum(uwind_filename_list,[]))
vwind_filename_list=np.sort(sum(vwind_filename_list,[]))
lwrad_filename_list=np.sort(sum(lwrad_filename_list,[]))
swrad_filename_list=np.sort(sum(swrad_filename_list,[]))

#BARRA has four analyses per day
#Create a list for all the datetime within the BARRA filenames
temp_filename_date_list=[]
temp_filename_time_list=[]
for x in range(len(temp_filename_list)):
    temp_filename_date=datetime.strptime(re.search(r'\d{4}\d{2}\d{2}T\d{2}\d{2}',temp_filename_list[x]).group(), '%Y%m%dT%H%M').date()
    temp_filename_date_list.append(temp_filename_date)
    temp_filename_time=datetime.strptime(re.search(r'\d{4}\d{2}\d{2}T\d{2}\d{2}',temp_filename_list[x]).group(), '%Y%m%dT%H%M').hour
    temp_filename_time_list.append(temp_filename_time)

#Create a dtf with directories for each variable and their corresponding date and time
dtf_barra=pd.DataFrame(list(zip(temp_filename_list,relhum_filename_list,uwind_filename_list,vwind_filename_list,lwrad_filename_list,swrad_filename_list,temp_filename_date_list,temp_filename_time_list)),columns=['temp_filename','relhum_filename','uwind_filename','vwind_filename','lwrad_filename','swrad_filename','date','time'])

#VIC shape directory
fwd_shapefile_path = '/g/data/er8/global_challenge/other_shapes/STE_2021_AUST_GDA2020.shp'
#Read VIC shape directory (this is used for clipping)
shapefile= gpd.read_file(fwd_shapefile_path)
vic_boundary = shapefile.loc[shapefile["STE_NAME21"] == "Victoria"]

#Soil moisture directory
dir_sm='/g/data/fj4/SatelliteSoilMoistureProducts/CCI/COMBINED/2015/ESACCI-SOILMOISTURE-L3S-SSMV-COMBINED-20150614000000-fv04.4.nc'
#Extract latitude of soil moisture dataset
lat_sm=NetCDFFile(dir_sm).variables['lat'][:].data
#Only take the absolute because collocating function (np.searchsorted) works badly with negative values
lat_sm_mod=abs(lat_sm[360:])
#Extract longitude of soil moisture dataset
lon_sm=NetCDFFile(dir_sm).variables['lon'][:].data

#CFA Australian fuel type file (based on AFDRS)
tif=xr.open_dataset('/g/data/ct18/dw4060/viirs/inputfiles/boundaries/ID_Districts_GrassPixels_May2022_1.tif')
#Only select VIC area
tif1=tif.rio.clip(vic_boundary.geometry)
#Extract absolute latitudes
FBM_lat=abs(tif1.y.values[:])
#Extract longitudes
FBM_lon=tif1.x.values[:]
#Extract fuel types
FBM=tif1.band_data.values[:][0]

#Precipitation directory
agcd_input_dir=f'/g/data/zv2/agcd/v1/precip/total/r005/01day/agcd_v1_precip_total_r005_daily_'

#Create a collocation loop for each MODIS file (corresponding to each day)
#Collocation of each file takes a long time. Here the code processes 30 files which takes up to 48hrs
#There are a total of 780 MODIS files to collocate
for file in range(0,31):
    #Read MODIS directory as an xarray
    modisraster=xr.open_dataset(dtf_modis_after15.modis_filename.values[file])
    #Clip the xarray with the VIC shape so that data is only in VIC (important to reduce processing time)
    modisraster1=modisraster.rio.clip(vic_boundary.geometry).to_array()
    #Convert xarray to dtf (this will give a dtf with lat, lon and curing values)
    modisdtf=modisraster1.to_dataframe('curing').reset_index()

    #Read MODIS age directory as an xarray
    modisageraster=xr.open_dataset(dtf_modis_after15.modis_age_filename.values[file])
    #Clip the xarray with the VIC shape so that data is only in VIC (important to reduce processing time)    
    modisageraster1=modisageraster.rio.clip(vic_boundary.geometry).to_array()
    #Convert xarray to dtf (this will give a dtf with lat, lon and curing age)
    modisagedtf=modisageraster1.to_dataframe('age').reset_index()

    #Merge to get one dtf with lat, lon, curing value and age
    modisdtf=pd.merge(modisdtf,modisagedtf,on=['variable','band','x','y','spatial_ref'])
    #Exclude all data points with no curing values recorded
    modisdtf=modisdtf.dropna()
    #Add a column for date
    modisdtf["date"]=dtf_modis_after15.time_diff[file]
    #Delete unnecessary columns
    del modisdtf['band']
    del modisdtf['spatial_ref']
    del modisdtf['variable']

    #Create a column for fuel type/fbm
    modisdtf['fbm']=''
    #Create a loop for collocation
    for i in range(len(modisdtf)):
        #Collocate (absolute) lat
        grid_lat_fbm=np.searchsorted(FBM_lat,abs(modisdtf.y.values[i]))
        #Collocate lon
        grid_lon_fbm=np.searchsorted(FBM_lon,modisdtf.x.values[i])
        #Fill in the 'fbm' column with corresponding fuel type
        #Lat has to minus 1 because we collocated using absolute values
        modisdtf.fbm.values[i]=FBM[grid_lat_fbm-1,grid_lon_fbm]

    #Exclude any null fbm pixels as they indicate forest
    modisdtf=modisdtf[~modisdtf.fbm.isnull()]

    #Create a column with a string of date (YYYYMMDD)
    modisdtf['date_str']=str(modisdtf['date'].values[0]).replace("-","")
    #Soil moisture general directory
    sm_input_dir=f'/g/data/fj4/SatelliteSoilMoistureProducts/CCI/COMBINED/'
    #Attach the MODIS date and extract relavant soil moisture directories
    #Example: /g/data/fj4/SatelliteSoilMoistureProducts/CCI/COMBINED/2015/ESACCI-SOILMOISTURE-L3S-SSMV-COMBINED-20150101000000-fv04.4.nc
    sm_filename=sm_input_dir+modisdtf['date_str'].values[0][:4]+'/ESACCI-SOILMOISTURE-L3S-SSMV-COMBINED-'+modisdtf['date_str'].values[0]+'000000-fv04.4.nc'
    #Read soil moisture directory with NetCDFFile function
    sm_filename_read=NetCDFFile(sm_filename)

    #Create a column for soil moisture
    modisdtf['sm']=''
    #Create a loop for collocation
    for i in range(len(modisdtf)):
        #Collocate lat using absolute MODIS lat
        #Remember to add 360 at the end to flip things back (it's quite complicated, but it works, np.searchsorted just hates negative lat)
        grid_lat_sm=np.searchsorted(lat_sm_mod,abs(modisdtf.y.values[i]))+360
        #Collocate lon
        grid_lon_sm=np.searchsorted(lon_sm,modisdtf.x.values[i])
        #Fill in the 'sm' column with corresponding soil moisture from the NetCDF file 
        modisdtf['sm'].values[i]=sm_filename_read.variables['sm'][0,grid_lat_sm,grid_lon_sm]

    #Read precipitation (AGCD) yearly files
    #Example: /g/data/zv2/agcd/v1/precip/total/r005/01day/agcd_v1_precip_total_r005_daily_2018.nc
    ncdf_AGCD = NetCDFFile(agcd_input_dir+modisdtf['date_str'].values[0][:4]+'.nc')
    #List of daily precipitation
    precip=ncdf_AGCD.variables['precip'][:]
    #Numpy arrays of lat and lon
    lat_AGCD=np.array(ncdf_AGCD.variables['lat'][:])
    lon_AGCD=np.array(ncdf_AGCD.variables['lon'][:])

    #Create a MODIS 'day of year' column
    modisdtf['day_of_year']=int(modisdtf['date'].values[0].strftime('%j'))

    #Create a column for precipitation
    modisdtf['precip']=''
    #Create a loop for collocation
    for i in range(len(modisdtf)):
        #Collocate lat
        grid_lat_agcd=np.searchsorted(lat_AGCD,modisdtf.y.values[i])
        #Collocate lon
        grid_lon_agcd=np.searchsorted(lon_AGCD,modisdtf.x.values[i])
        #Fill in the 'precip' column with precipitation list (needs day of year -1, lat, lon)
        modisdtf['precip'].values[i]=precip[modisdtf['day_of_year'].values[i]-1,grid_lat_agcd,grid_lon_agcd]

    #Get four BARRA files for the relevant date
    dtf_barra1=dtf_barra[dtf_barra['date']==modisdtf.date.values[0]]

    #Create two columns for collocated lat and lon
    modisdtf['grid_lat_barra']=''
    modisdtf['grid_lon_barra']=''
    #Create a loop to collocate BARRA lat and lon
    for i in range(len(modisdtf)):
        modisdtf['grid_lat_barra'].values[i]=np.searchsorted(lat_BARRA,modisdtf.y.values[i])
        modisdtf['grid_lon_barra'].values[i]=np.searchsorted(lon_BARRA,modisdtf.x.values[i])

    #Read NetCDFFile for each of the four daily analyses of each variable
    temp0=NetCDFFile(dtf_barra1.temp_filename.values[0]).variables['sfc_temp']
    temp6=NetCDFFile(dtf_barra1.temp_filename.values[1]).variables['sfc_temp']
    temp12=NetCDFFile(dtf_barra1.temp_filename.values[2]).variables['sfc_temp']
    temp18=NetCDFFile(dtf_barra1.temp_filename.values[3]).variables['sfc_temp']
    #Relhum
    relhum0=NetCDFFile(dtf_barra1.relhum_filename.values[0]).variables['relhum']
    relhum6=NetCDFFile(dtf_barra1.relhum_filename.values[1]).variables['relhum']
    relhum12=NetCDFFile(dtf_barra1.relhum_filename.values[2]).variables['relhum']
    relhum18=NetCDFFile(dtf_barra1.relhum_filename.values[3]).variables['relhum']
    #U-Wind
    uwind0=NetCDFFile(dtf_barra1.uwind_filename.values[0]).variables['uwnd10m']
    uwind6=NetCDFFile(dtf_barra1.uwind_filename.values[1]).variables['uwnd10m']
    uwind12=NetCDFFile(dtf_barra1.uwind_filename.values[2]).variables['uwnd10m']
    uwind18=NetCDFFile(dtf_barra1.uwind_filename.values[3]).variables['uwnd10m']
    #V-Wind
    vwind0=NetCDFFile(dtf_barra1.vwind_filename.values[0]).variables['vwnd10m']
    vwind6=NetCDFFile(dtf_barra1.vwind_filename.values[1]).variables['vwnd10m']
    vwind12=NetCDFFile(dtf_barra1.vwind_filename.values[2]).variables['vwnd10m']
    vwind18=NetCDFFile(dtf_barra1.vwind_filename.values[3]).variables['vwnd10m']
    #Shortwave radiation
    swrad0=NetCDFFile(dtf_barra1.swrad_filename.values[0]).variables['av_swsfcdown']
    swrad6=NetCDFFile(dtf_barra1.swrad_filename.values[1]).variables['av_swsfcdown']
    swrad12=NetCDFFile(dtf_barra1.swrad_filename.values[2]).variables['av_swsfcdown']
    swrad18=NetCDFFile(dtf_barra1.swrad_filename.values[3]).variables['av_swsfcdown']
    #Longwave radiation
    lwrad0=NetCDFFile(dtf_barra1.lwrad_filename.values[0]).variables['av_lwsfcdown']
    lwrad6=NetCDFFile(dtf_barra1.lwrad_filename.values[1]).variables['av_lwsfcdown']
    lwrad12=NetCDFFile(dtf_barra1.lwrad_filename.values[2]).variables['av_lwsfcdown']
    lwrad18=NetCDFFile(dtf_barra1.lwrad_filename.values[3]).variables['av_lwsfcdown']

    #Create columns for each of the four analyses of each variable
    modisdtf['temp0']=''
    modisdtf['temp6']=''
    modisdtf['temp12']=''
    modisdtf['temp18']=''
    modisdtf['relhum0']=''
    modisdtf['relhum6']=''
    modisdtf['relhum12']=''
    modisdtf['relhum18']=''
    modisdtf['uwind0']=''
    modisdtf['uwind6']=''
    modisdtf['uwind12']=''
    modisdtf['uwind18']=''
    modisdtf['vwind0']=''
    modisdtf['vwind6']=''
    modisdtf['vwind12']=''
    modisdtf['vwind18']=''
    modisdtf['wind0']=''
    modisdtf['wind6']=''
    modisdtf['wind12']=''
    modisdtf['wind18']=''
    modisdtf['swrad0']=''
    modisdtf['swrad6']=''
    modisdtf['swrad12']=''
    modisdtf['swrad18']=''
    modisdtf['lwrad0']=''
    modisdtf['lwrad6']=''
    modisdtf['lwrad12']=''
    modisdtf['lwrad18']=''
    modisdtf['max_temp']=''
    modisdtf['min_temp']=''
    modisdtf['max_relhum']=''
    modisdtf['min_relhum']=''
    modisdtf['max_uwind']=''
    modisdtf['min_uwind']=''
    modisdtf['max_vwind']=''
    modisdtf['min_vwind']=''
    modisdtf['max_wind']=''
    modisdtf['min_wind']=''
    modisdtf['max_swrad']=''
    modisdtf['min_swrad']=''
    modisdtf['max_lwrad']=''
    modisdtf['min_lwrad']=''

    #Create a loop to fill in the corresponding BARRA values
    for i in range(len(modisdtf)):
        #For temperatures, use lat and lon and remember to subtract 273.15 to get degrees Celsius
        modisdtf.temp0.values[i]=temp0[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]-273.15
        modisdtf.temp6.values[i]=temp6[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]-273.15
        modisdtf.temp12.values[i]=temp12[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]-273.15
        modisdtf.temp18.values[i]=temp18[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]-273.15
        #For relative humidity, first term is 36 (surface level pressure), followed by lat and lon
        modisdtf.relhum0.values[i]=relhum0[36,modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.relhum6.values[i]=relhum6[36,modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.relhum12.values[i]=relhum12[36,modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.relhum18.values[i]=relhum18[36,modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        #U- and V-Winds and Short- and Longwave radiations just need lat and lon
        modisdtf.uwind0.values[i]=uwind0[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.uwind6.values[i]=uwind6[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.uwind12.values[i]=uwind12[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.uwind18.values[i]=uwind18[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.vwind0.values[i]=vwind0[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.vwind6.values[i]=vwind6[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.vwind12.values[i]=vwind12[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.vwind18.values[i]=vwind18[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.swrad0.values[i]=swrad0[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.swrad6.values[i]=swrad6[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.swrad12.values[i]=swrad12[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.swrad18.values[i]=swrad18[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.lwrad0.values[i]=lwrad0[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.lwrad6.values[i]=lwrad6[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.lwrad12.values[i]=lwrad12[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        modisdtf.lwrad18.values[i]=lwrad18[modisdtf.grid_lat_barra.values[i],modisdtf.grid_lon_barra.values[i]]
        #Calculate wind speed using standard equation
        modisdtf['wind0'].values[i]=np.sqrt((modisdtf['uwind0'].values[i]**2)+(modisdtf['vwind0'].values[i]**2))
        modisdtf['wind6'].values[i]=np.sqrt((modisdtf['uwind6'].values[i]**2)+(modisdtf['vwind6'].values[i]**2))
        modisdtf['wind12'].values[i]=np.sqrt((modisdtf['uwind12'].values[i]**2)+(modisdtf['vwind12'].values[i]**2))
        modisdtf['wind18'].values[i]=np.sqrt((modisdtf['uwind18'].values[i]**2)+(modisdtf['vwind18'].values[i]**2))
        #Select max measurement from four daily analyses
        modisdtf['max_temp'].values[i]=max(modisdtf.temp0.values[i],modisdtf.temp6.values[i],modisdtf.temp12.values[i],modisdtf.temp18.values[i])
        modisdtf['max_relhum'].values[i]=max(modisdtf.relhum0.values[i],modisdtf.relhum6.values[i],modisdtf.relhum12.values[i],modisdtf.relhum18.values[i])
        modisdtf['max_uwind'].values[i]=max(abs(modisdtf.uwind0.values[i]),abs(modisdtf.uwind6.values[i]),abs(modisdtf.uwind12.values[i]),abs(modisdtf.uwind18.values[i]))
        modisdtf['max_vwind'].values[i]=max(abs(modisdtf.vwind0.values[i]),abs(modisdtf.vwind6.values[i]),abs(modisdtf.vwind12.values[i]),abs(modisdtf.vwind18.values[i]))
        modisdtf['max_wind'].values[i]=max(modisdtf.wind0.values[i],modisdtf.wind6.values[i],modisdtf.wind12.values[i],modisdtf.wind18.values[i])
        modisdtf['max_swrad'].values[i]=max(modisdtf.swrad0.values[i],modisdtf.swrad6.values[i],modisdtf.swrad12.values[i],modisdtf.swrad18.values[i])
        modisdtf['max_lwrad'].values[i]=max(modisdtf.lwrad0.values[i],modisdtf.lwrad6.values[i],modisdtf.lwrad12.values[i],modisdtf.lwrad18.values[i])
        #Select min measurement from four daily analyses
        modisdtf['min_temp'].values[i]=min(modisdtf.temp0.values[i],modisdtf.temp6.values[i],modisdtf.temp12.values[i],modisdtf.temp18.values[i])
        modisdtf['min_relhum'].values[i]=min(modisdtf.relhum0.values[i],modisdtf.relhum6.values[i],modisdtf.relhum12.values[i],modisdtf.relhum18.values[i])
        modisdtf['min_uwind'].values[i]=min(abs(modisdtf.uwind0.values[i]),abs(modisdtf.uwind6.values[i]),abs(modisdtf.uwind12.values[i]),abs(modisdtf.uwind18.values[i]))
        modisdtf['min_vwind'].values[i]=min(abs(modisdtf.vwind0.values[i]),abs(modisdtf.vwind6.values[i]),abs(modisdtf.vwind12.values[i]),abs(modisdtf.vwind18.values[i]))
        modisdtf['min_wind'].values[i]=min(modisdtf.wind0.values[i],modisdtf.wind6.values[i],modisdtf.wind12.values[i],modisdtf.wind18.values[i])
        modisdtf['min_swrad'].values[i]=min(modisdtf.swrad0.values[i],modisdtf.swrad6.values[i],modisdtf.swrad12.values[i],modisdtf.swrad18.values[i])
        modisdtf['min_lwrad'].values[i]=min(modisdtf.lwrad0.values[i],modisdtf.lwrad6.values[i],modisdtf.lwrad12.values[i],modisdtf.lwrad18.values[i])

    #Covert the BARRA columns to float (otherwise it stays as object which makes future coding harder)
    modisdtf.fbm=modisdtf.fbm.astype(float)
    modisdtf.sm=modisdtf.sm.astype(float)
    modisdtf.precip=modisdtf.precip.astype(float)
    modisdtf.temp0=modisdtf.temp0.astype(float)
    modisdtf.temp6=modisdtf.temp6.astype(float)
    modisdtf.temp12=modisdtf.temp12.astype(float)
    modisdtf.temp18=modisdtf.temp18.astype(float)
    modisdtf.relhum0=modisdtf.relhum0.astype(float)
    modisdtf.relhum6=modisdtf.relhum6.astype(float)
    modisdtf.relhum12=modisdtf.relhum12.astype(float)
    modisdtf.relhum18=modisdtf.relhum18.astype(float)
    modisdtf.uwind0=modisdtf.uwind0.astype(float)
    modisdtf.uwind6=modisdtf.uwind6.astype(float)
    modisdtf.uwind12=modisdtf.uwind12.astype(float)
    modisdtf.uwind18=modisdtf.uwind18.astype(float)
    modisdtf.vwind0=modisdtf.vwind0.astype(float)
    modisdtf.vwind6=modisdtf.vwind6.astype(float)
    modisdtf.vwind12=modisdtf.vwind12.astype(float)
    modisdtf.vwind18=modisdtf.vwind18.astype(float)
    modisdtf.swrad0=modisdtf.swrad0.astype(float)
    modisdtf.swrad6=modisdtf.swrad6.astype(float)
    modisdtf.swrad12=modisdtf.swrad12.astype(float)
    modisdtf.swrad18=modisdtf.swrad18.astype(float)
    modisdtf.lwrad0=modisdtf.lwrad0.astype(float)
    modisdtf.lwrad6=modisdtf.lwrad6.astype(float)
    modisdtf.lwrad12=modisdtf.lwrad12.astype(float)
    modisdtf.lwrad18=modisdtf.lwrad18.astype(float)
    modisdtf.wind0=modisdtf.wind0.astype(float)
    modisdtf.wind6=modisdtf.wind6.astype(float)
    modisdtf.wind12=modisdtf.wind12.astype(float)
    modisdtf.wind18=modisdtf.wind18.astype(float)
    modisdtf.max_temp=modisdtf.max_temp.astype(float)
    modisdtf.min_temp=modisdtf.min_temp.astype(float)
    modisdtf.max_relhum=modisdtf.max_relhum.astype(float)
    modisdtf.min_relhum=modisdtf.min_relhum.astype(float)
    modisdtf.max_uwind=modisdtf.max_uwind.astype(float)
    modisdtf.min_uwind=modisdtf.min_uwind.astype(float)
    modisdtf.max_vwind=modisdtf.max_vwind.astype(float)
    modisdtf.min_vwind=modisdtf.min_vwind.astype(float)
    modisdtf.max_swrad=modisdtf.max_swrad.astype(float)
    modisdtf.min_swrad=modisdtf.min_swrad.astype(float)
    modisdtf.max_lwrad=modisdtf.max_lwrad.astype(float)
    modisdtf.min_lwrad=modisdtf.min_lwrad.astype(float)
    modisdtf.max_wind=modisdtf.max_wind.astype(float)
    modisdtf.min_wind=modisdtf.min_wind.astype(float)

    #Save daily dtf with corresponding date
    modisdtf.to_pickle('/home/565/pd8410/python/dtf/sem2_16_9_newcol/'+f'{modisdtf.date_str.values[0]}'+'.pkl')