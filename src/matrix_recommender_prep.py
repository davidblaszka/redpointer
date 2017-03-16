import pandas as pd


def clean_ratings(rating_by_user_df):
	'''takes a dataframe'''

	# convert route name to utf-8
	routes_series = rating_by_user_df['route'].map(lambda x: x.encode('utf-8'))
	routes_list = routes_series.tolist()
	# intialize dataframe with index as routes
	df = pd.DataFrame(index=routes_list)
	for route, usernames, ratings in zip(routes_list, 
										rating_by_user_df['username'],
										rating_by_user_df['rating']):
		for username, rating in zip(usernames, ratings):
			username = username.encode('utf-8')
			df.loc[route, username] = rating
	return df.T


def cold_start(df):
	''' fillna with column mean. The columns should be routes. '''
	# clean first
	df = clean_ratings(df)
	new_df = pd.DataFrame(columns=df.columns.unique())
	for column in df.columns:
		# not allowing duplicates
		if isinstance(df[column], pd.Series):
			new_df[column] = df[column].fillna(df[column].mean())
	return new_df

def update_df(df):
	row = 0
	df_new = pd.DataFrame(columns=['username','route','rating'])
	for route, usernames, ratings in zip(df['route'], 
										df['username'],
										df['rating']):
		row += 1
		for username, rating in zip(usernames, ratings):
			row += 1
			df_new.loc[row, 'username'] = username.encode('utf-8')
			df_new.loc[row, 'rating'] = rating
			df_new.loc[row, 'route'] = route
	# convert to catagorical the numerical
	df_new['username'] = df_new['username'].astype('category').cat.codes
	df_new['route'] = df_new['route'].astype('category').cat.codes
	return df_new