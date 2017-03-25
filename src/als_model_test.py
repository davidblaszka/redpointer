import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import pyspark
from pyspark.sql.types import *
from pyspark.ml.tuning import TrainValidationSplit
from pymongo import MongoClient
from pyspark.ml.recommendation import ALS


def als_validation(y_train, y_test):
	# Convert to a Spark DataFrame
	y_train_spark = spark.createDataFrame(y_train)
	y_test_spark = spark.createDataFrame(y_test)

	# call als model
	als = ALS(userCol='user_id',
			itemCol='route_id',
			ratingCol='rating',
			nonnegative=True,
			regParam=0.1,
			rank=10
			)

	# fit model
	recommender = als.fit(y_train_spark)

	#save model
	path = '../data/alsmodel_val'
	recommender.save(path)

	# Make predictions for the whole test set
	predictions = recommender.transform(y_test_spark)

	# Dump the predictions to Pandas DataFrames to make our final calculations easier
	predictions_df = predictions.toPandas()
	train_df = y_train_spark.toPandas()

	# Fill any missing values with the mean rating
	predictions_df = predictions.toPandas().fillna(train_df['rating'].mean())

	predictions_df['squared_error'] = (predictions_df['rating'] - predictions_df['prediction'])**2

	# Calculate RMSE
	print "RMSE: ", np.sqrt(sum(predictions_df['squared_error']) / len(predictions_df))


if __name__ == '__main__':

	# Build our Spark Session and Context
	spark = pyspark.sql.SparkSession.builder.getOrCreate()
	sc = spark.sparkContext
	spark, sc

	# load data frame from csv
	data_df = pd.read_csv("model_df.csv", sep='\t')

	# drop duplicates
	data_df = data_df.drop_duplicates(subset=['route_id', 'user_id'])
	y_data = data_df[['route_id', 'user_id','rating']]
	x_data = data_df.drop(['rating', 'route_id', 'user_id', 'member_since', 'Unnamed: 0'], axis=1)
	X_train, X_test, y_train, y_test = train_test_split(x_data, y_data, random_state=42)
	# run validation model
	als_validation(y_train, y_test)