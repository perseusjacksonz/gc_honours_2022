#Import libraries
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error,median_absolute_error
import pickle

#Read the splitted training and testing datasets as pandas dtfs
X_train=pd.read_pickle('/g/data/er8/global_challenge/code/persie_help/final/dtf/X_train_newcol.pkl')
y_train=pd.read_pickle('/g/data/er8/global_challenge/code/persie_help/final/dtf/y_train_newcol.pkl')
X_test=pd.read_pickle('/g/data/er8/global_challenge/code/persie_help/final/dtf/X_test_newcol.pkl')
y_test=pd.read_pickle('/g/data/er8/global_challenge/code/persie_help/final/dtf/y_test_newcol.pkl')

####For the model with just meteorological variables, do this extra step####
# curing_vars=['curing_4day','curing_5day','curing_6day','curing_7day','curing_8day','curing_9day','curing_10day','curing_avg_7day','curing_avg_4day']
# X_train=X_train.drop(curing_vars,axis=1)
# X_test=X_test.drop(curing_vars,axis=1)

#Drop the date column in the training and testing input variables
X_train=X_train.drop('date',axis=1)
X_test=X_test.drop('date',axis=1)

####For model with only curing variables, do this step####
# X_train=X_train[curing_vars]
# X_test=X_test[curing_vars]

#Covert all the columns to numeric
X_train=X_train.apply(pd.to_numeric,errors='ignore')
X_test=X_test.apply(pd.to_numeric,errors='ignore')

#Read the dictionary of optimised hyperparameters
hyperparameters=pd.read_pickle('/g/data/er8/global_challenge/code/persie_help/final/machinelearning/allvars/hyperopt.pkl')

#Define the XGBoost model and hyperparameters
#If you want to run the model with default hyperparameters, just include the objective and exclude the rest
xg_reg = xgb.XGBRegressor(objective='reg:squarederror',
                    learning_rate=hyperparameters['learning_rate'],
                    sub_sample=hyperparameters['sub_sample'],
                    min_child_weight=int(hyperparameters['min_child_weight']),
                    max_depth = int(hyperparameters['max_depth']),
                    gamma = int(hyperparameters['gamma']),
                    reg_alpha = hyperparameters['reg_alpha'],
                    reg_lambda = hyperparameters['reg_lambda'],
                    colsample_bytree=hyperparameters['colsample_bytree'])

#Train the XGBoost model with training data
#Training this model takes approx. 36-40hrs
xg_reg.fit(X_train,y_train)

#Save the XGBoost model
xg_reg.save_model("/g/data/er8/global_challenge/code/persie_help/final/machinelearning/allvars/xgboost_hyperopt.json")

#Give the model the testing data for it to make a set of prediction
#Running this model takes approx. 12hrs
predictions = xg_reg.predict(X_test) 

#Use scikit-learn library to extract key metrics (MSE, MAE)
dictionary={'mean_squared_error_grid':'%d'%mean_squared_error(y_test, predictions),
            'median_absolute_error_grid':'%d'%median_absolute_error(y_test, predictions)}

#Save key metrics
with open('/g/data/er8/global_challenge/code/persie_help/final/machinelearning/allvars/metrics_hyperopt.pkl', 'wb') as f:
    pickle.dump(dictionary, f)

#Save feature importance
#This is the gain scores, see https://datascience.stackexchange.com/questions/12318/how-to-interpret-the-output-of-xgboost-importance
with open('/g/data/er8/global_challenge/code/persie_help/final/machinelearning/allvars/featureimportance_hyperopt.pkl', 'wb') as f:
    pickle.dump(xg_reg.feature_importances_, f)

#Save the model predictions
with open('/g/data/er8/global_challenge/code/persie_help/final/machinelearning/allvars/predictions_hyperopt.pkl', 'wb') as f:
    pickle.dump(predictions, f)

#Save the variable list
with open('/g/data/er8/global_challenge/code/persie_help/final/machinelearning/allvars/variables_hyperopt.pkl', 'wb') as f:
    pickle.dump(X_test.keys(), f)
