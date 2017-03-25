import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
from sklearn.externals import joblib
from sklearn.model_selection import GridSearchCV


def gb_all_data(x_data, y_data):
	gb = GradientBoostingRegressor(min_samples_leaf=3,
									learning_rate=0.01,
									max_depth=2,
									n_estimators=500,
									subsample = 0.2,
									random_state=42)
	gb.fit(x_data, y_data['rating'])
	# pickle model
	joblib.dump(gb, '../pickle/gb_model_all_data.pkl')


def gb_train(x_data, y_data):
	'''runs a gradient boosting model on featured data'''
	X_train, X_test, y_train, y_test = train_test_split(x_data, y_data, random_state=42)
	gb = GradientBoostingRegressor(min_samples_leaf=3,
									learning_rate=0.01,
									max_depth=2,
									n_estimators=500,
									subsample = 0.2,
									random_state=42)
	gb.fit(X_train, y_train['rating'])
	print 'RMSE: ', np.sqrt(mean_squared_error(y_test['rating'], gb.predict(X_test)))

	# pickle model
	joblib.dump(gb, '../pickle/gb_model.pkl') 	
	'''
	grid_params = {'learning_rate': [ 0.001, 0.01],
               'max_features': ['sqrt', 'log2', None],
               'min_samples_leaf': [1,2,4],
               'max_depth':[1,2,5],
               'n_estimators': [500, 1000, 4000],
               'subsample': [0.2, 0.5, 1.0]
              }
	gb = GradientBoostingRegressor()
	grid = GridSearchCV(gb, grid_params, n_jobs=-1)
	grid.fit(X_train, y_train['rating'])
	print grid.cv_results_['mean_test_score']
	print 'RMSE: ', np.sqrt(mean_squared_error(y_test['rating'], grid.predict(X_test)))
	'''


if __name__ == '__main__':
	# load data frame from csv
	data_df = pd.read_csv("model_df.csv", sep='\t')

	# drop duplicates
	data_df = data_df.drop_duplicates(subset=['route_id', 'user_id'])

	y_data = data_df[['rating', 'route_id', 'user_id']]
	x_data = data_df.drop(['rating', 'route_id', 
							'user_id', 'member_since', 
							'Unnamed: 0'], axis=1)
	# run gb model for validation
	gb_train(x_data, y_data)
	# run gb model on all data
	gb_all_data(x_data, y_data)

	