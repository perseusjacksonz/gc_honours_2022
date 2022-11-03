This folder contains 2022 Honours work by Persie Duong, Kate Howard and Gabrielle Malley
Bachelor of Science Advanced - Global Challenges (Honours)
Monash University, Australia

Project: Short-term Prediction of Grassland Curing in Victoria using Machine Learning
Supervised by Dr. Caroline Poulsen (Bureau of Meteorology) and Dr. Danielle Wright (Country Fire Authority)
All files are last editted on: 03/11/2022

There are various files available in three main directories:

1) code
Contains the detailed steps to process the data and recreate the machine learning models

Step 1: Collocate data from different sources
Step 2: Obtain data of everyday in the past week from the current-day file
Step 3: (optional) Similar to Step 2, but for the pixels excluding from a case study of the Scotsburn grassfire
Step 4: Append all the files in Step 2 and 3 into one big dataset
Step 5: Split Step 4's dataset into training and testing sub-datasets using 80:20 training:testing ratio
Step 6: Determine the optimised values for XGBoost hyperparameters using Bayesian optimisation method (via Hyperopt library)
Step 7: Train and run the XGBoost model

2) dtf
Contains:
    - Appended datasets from Step 4
    - Splitted training and testing sub-datasets from Step 5

For each dataset, there are two versions with and without null values

Daily files for Steps 1-3 are not available due to storage limitation

3) machine learning
Has three folders containing results from three tested models
    i. allvars: Model with both curing and meteorological variables
    ii. onlycuringvars: Model with only curing variables
    iii. onlymeteorologicalvars: Model with only meteorological variables

Each folder contains:
    > featureimportance_hyperopt.csv: Feature importance analysis with gain score for each variable
    > hyperopt.pkl: Optimised values of each hyperparameters (as a dictionary)
    > predictions_hyperopt.pkl: Model prediction when given the testing data (as a numpy.ndarray)
    > variables_hyperopt.pkl: Model variables (as a pandas.core.indexes.base.Index)
    > xgboost_hyperopt.json: Trained XGBoost model
