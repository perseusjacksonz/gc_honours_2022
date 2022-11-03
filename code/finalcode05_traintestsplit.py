#Import libraries
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import rioxarray as rio
from sklearn.model_selection import train_test_split
import pickle

#Read big input dataset as a pandas dtf
modisdtf=pd.read_pickle('/home/565/pd8410/python/dtf/dtfappend_versions/dtfappend_newcol.pkl')

#Extract the current-day curing column
labels = modisdtf.curing

#Separate the current-day curing column from the rest of the input dataset
features=modisdtf.drop('curing',axis=1)

# y is the truth variable (current-day curing), x is the remaining information (past curing and meteorological variables)
# _train is for training, _val is for testing
# train_size is the split ratio (in this case it's 80% training, 20% testing)
# random_state is just to control the randomness every time train_test_split function is run, I don't know too much but it doesn't matter in this case since the training and testing datasets are splitted once and used repeatedly
X_train, X_test, y_train, y_test = train_test_split(features, labels, train_size=0.80,random_state=0)

#Use pickle.dump to save the splitted datasets
with open('/home/565/pd8410/python/dtf/dtfappend_versions/X_train_newcol.pkl', 'wb') as f:
    pickle.dump(X_train, f)
with open('/home/565/pd8410/python/dtf/dtfappend_versions/X_test_newcol.pkl', 'wb') as f:
    pickle.dump(X_test, f)
with open('/home/565/pd8410/python/dtf/dtfappend_versions/y_train_newcol.pkl', 'wb') as f:
    pickle.dump(y_train, f)
with open('/home/565/pd8410/python/dtf/dtfappend_versions/y_test_newcol.pkl', 'wb') as f:
    pickle.dump(y_test, f)

#Visualise spatial coverage of training dataset

#Define the size
output_x_size = 1600
output_y_size = 900
# pyplot specifies figure size in inches (dpi = dots per inch = anything, but 72 is a magic number from print days)
dpi = 72

# Area of interest: Victoria:
crs = ccrs.PlateCarree()
map_extent = [140.5, 150.5, -39.5, -33.5]
# read vic boundary
fwd_shapefile_path = '/g/data/er8/global_challenge/other_shapes/STE_2021_AUST_GDA2020.shp'
shapefile= gpd.read_file(fwd_shapefile_path)
vic_boundary = shapefile.loc[shapefile["STE_NAME21"] == "Victoria"]

plt.clf()
fig, ax = plt.subplots(1, 1,
            figsize=(output_x_size/dpi, output_y_size/dpi), dpi=dpi,
            subplot_kw={'projection': crs},zorder=5)
ax.set_extent(map_extent, crs=crs)
#Plot the Vic border
vic_boundary.plot(ax=ax, color='none', facecolor='none', edgecolor='black',zorder=1)
#Plot the training pixels
ax.scatter(X_train.x,X_train.y,color='r',zorder=2,s=0.01)
#Add legend
ax.legend(['Training'],fontsize=20,frameon=False,markerscale=2)
#Add grid
gl=ax.gridlines(draw_labels=True, linewidth=2, linestyle='--',alpha=0.2,zorder=6)
#Format lat and lon
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {'size': 20}
gl.ylabel_style = {'size': 20}
#Add axis titles
ax.text(-0.05, 0.5, 'Latitude', va='bottom', ha='center',
        rotation='vertical', rotation_mode='anchor',
        transform=ax.transAxes,fontsize=20)
ax.text(0.5, -0.07, 'Longitude', va='bottom', ha='center',
        rotation='horizontal', rotation_mode='anchor',
        transform=ax.transAxes,fontsize=20)
#Save fig
plt.savefig('/home/565/pd8410/python/obj_plots_sem2/X_train.png', bbox_inches='tight')

#Plot bar chart of number of pixels in each month of the training dataset
fig, ax = plt.subplots(1, 1,
            figsize=(output_x_size/dpi, output_y_size/dpi), dpi=dpi)
#Use groupby(year,month).count() of X_train.date to get number of pixels every month
X_train.date.groupby([pd.DatetimeIndex(X_train.date).year, pd.DatetimeIndex(X_train.date).month]).count().plot(kind="bar")
#Save fig
plt.savefig('/home/565/pd8410/python/obj_plots_sem2/X_train_datecount.png', bbox_inches='tight')
