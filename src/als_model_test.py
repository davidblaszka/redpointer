import pandas as pd
from matrix_recommender_prep import update_df
import numpy as np
import pyspark
from pyspark.sql.types import *
from pyspark.ml.tuning import TrainValidationSplit
from pyspark.ml.evaluation import RegressionEvaluator
from pymongo import MongoClient
from als_model import ALS_Model


# Build our Spark Session and Context
spark = pyspark.sql.SparkSession.builder.getOrCreate()
sc = spark.sparkContext
spark, sc

client = MongoClient('mongodb://localhost:27017/')
db = client.ratings_collection
ratings_collection = db.ratings_collection
raw_data = ratings_collection.find()
df_ratings = pd.DataFrame(list(raw_data))
df_ratings.head()

ratings_df_pd, route_list = update_df(df_ratings)

# Convert to a Spark DataFrame
ratings_df = spark.createDataFrame(ratings_df_pd)

# split train and test
train, test = ratings_df.randomSplit([0.8, 0.2], seed=427471138)

# call als model
als = ALS_Model(userCol='username',
				itemCol='route',
				ratingCol='rating',
				nonnegative=True,
				regParam=0.1,
				rank=10
				)

# fit model
recommender = als.fit(train)

# Make predictions for the whole test set
predictions = recommender.transform(test)

# Dump the predictions to Pandas DataFrames to make our final calculations easier
predictions_df = predictions.toPandas()
train_df = train.toPandas()

# Fill any missing values with the mean rating
predictions_df = predictions.toPandas().fillna(train_df['rating'].mean())

predictions_df['squared_error'] = (predictions_df['rating'] - predictions_df['prediction'])**2

# Calculate RMSE
print "RMSE: ", np.sqrt(sum(predictions_df['squared_error']) / len(predictions_df))