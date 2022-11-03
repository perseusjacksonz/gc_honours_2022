#Import libraries
import pandas as pd
import numpy as np
import math
import xgboost as xgb
from sklearn.metrics import median_absolute_error
# pip install hyperopt
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
import pickle

#Read the splitted training and testing datasets as pandas dtfs
X_train=pd.read_pickle('/g/data/er8/global_challenge/code/persie_help/final/dtf/X_train_newcol.pkl')
y_train=pd.read_pickle('/g/data/er8/global_challenge/code/persie_help/final/dtf/y_train_newcol.pkl')
X_test=pd.read_pickle('/g/data/er8/global_challenge/code/persie_help/final/dtf/X_test_newcol.pkl')
y_test=pd.read_pickle('/g/data/er8/global_challenge/code/persie_help/final/dtf/y_test_newcol.pkl')

#Drop the date column in the training and testing input variables
X_train=X_train.drop('date',axis=1)
X_test=X_test.drop('date',axis=1)
#Covert all the columns to numeric
X_train=X_train.apply(pd.to_numeric,errors='ignore')
X_test=X_test.apply(pd.to_numeric,errors='ignore')

#The following part is based on this notebook
#https://www.kaggle.com/code/prashant111/a-guide-on-xgboost-hyperparameters-tuning/notebook

#Define the hyperparameters and the range of values we want to optimise
#hp.uniform is for continuous floats, hp.quniform is for continuous integers
#hp.loguniform is for continuous log floats. It is only used for learning rates as this can be really small (<0.005)
space={'learning_rate':hp.loguniform('learning_rate',-4,0),
        'sub_sample':hp.uniform('sub_sample',0.01,0.99),
        'min_child_weight' : hp.quniform('min_child_weight',0,10,1),
        'max_depth': hp.quniform("max_depth",5,65,5),
        'gamma': hp.quniform('gamma',1,20,1),
        #For explanation of reg_lambda and reg_alpha (or regularisation in general), see https://www.linkedin.com/pulse/l1-l2-regularization-why-neededwhat-doeshow-helps-ravi-shankar/
        #or https://medium.com/nerd-for-tech/lasso-and-ridge-regularization-simply-explained-d551ee1e47b7
        'reg_alpha':hp.uniform('reg_alpha',0,100),
        'reg_lambda' : hp.uniform('reg_lambda',0,100),
        'colsample_bytree':hp.uniform('colsample_bytree',0,1)}

#Define the objective space (refer to notebook link)
def objective(space):
    clf=xgb.XGBRegressor(objective='reg:squarederror',
                #Important here to convert the log learning rate back to normal using exponential
                    learning_rate=math.exp(space['learning_rate']),
                    sub_sample=space['sub_sample'],
                    min_child_weight=int(space['min_child_weight']),
                    max_depth = int(space['max_depth']),
                    gamma = int(space['gamma']),
                    reg_alpha = int(space['reg_alpha']),
                    reg_lambda = space['reg_lambda'],
                    colsample_bytree=int(space['colsample_bytree']))
    
    evaluation = [( X_train, y_train), ( X_test, y_test)]
    
    #early_stopping_round was set to 10, but more research needs to be done as I haven't fully understood what its significance is
    #eval_metrics was set to Root Mean Squared Error ('rmse') in this case, but again I wasn't sure what it does
    clf.fit(X_train, y_train,
            eval_set=evaluation,eval_metric="rmse",
            early_stopping_rounds=10,verbose=False)
    
    pred = clf.predict(X_test)
    
    #The loss function was set to be median_absolute_error which is an error/accuracy metric
    #Essentially what it means is the algorithm is optimised for accuracy
    #There might be other accuracy metrics or stability (or variance for technical ML term) such as Root Mean Squared Error, depending what you want to optimise the algorithm upon
    loss = median_absolute_error(y_test, pred)
    return {'loss': loss, 'status': STATUS_OK }

trials = Trials()

#The settings of fmin was based on this website: https://www.databricks.com/blog/2021/04/15/how-not-to-tune-your-model-with-hyperopt.html
#max_evals should be 160 (20*number of hyperparameters, see databricks link), but it takes very long (>48hrs which is gadi's max allowance)
best_hyperparams = fmin(fn = objective,
                        space = space,
                        algo = tpe.suggest,
                        max_evals = 45,
                        trials = trials)

#Save the optimised hyperparameter values as dictionary
with open('/g/data/er8/global_challenge/code/persie_help/final/machinelearning/allvars/hyperopt.pkl', 'wb') as f:
    pickle.dump(best_hyperparams, f)