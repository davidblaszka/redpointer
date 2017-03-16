import pyspark
from pyspark.sql.types import *
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pymongo import MongoClient

# Build our Spark Session and Context
spark = pyspark.sql.SparkSession.builder.getOrCreate()
sc = spark.sparkContext
spark, sc

class ALS_Model(object):

	def __inti__(self, user, item, rating,
				nonnegative=True, regParam=0.1,
				rank=10):
		self.als_model = ALS(userCol=user,
							itemCol=item,
							ratingCol=rating,
							nonnegative=nonnegative,
							regParam=regParam,
							rank=rank
							)

	def fit(self, train, write=False):
		self.recommender = self.als_model.fit(train)
		if write == True:
			self.recommender.write()
		return recommender

	def transform(self, test):
		# Make predictions for the whole test set
		self.predictions = self.recommender.transform(test)
		return self.predictions

