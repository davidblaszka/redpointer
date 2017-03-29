# RedPointer
A Mountain Project Rock Climbing Route Recommender

Galvanize Data Science Program - Winter 2017 - Capstone Project - David Blaszka

## Overview

Mountain Project is a tremendous resource for finding information about rock climbing routes across the globe. While the site provides this excellent information on routes, it does not have any current installation of a route recommender based on past routes that a user has liked. I built RedPointer to provide users with a recommender system.

![Image](data/images/redpointer.png)


## DATA SOURCE

All of my data is scraped from the Mountain Project website using Requests and BeautifulSoup. For each route, I scraped the route meta data. Similarly, for each user that rated a route, I scraped their meta deta and the rating they gave the route. 

All of the data was stored in MongoDB database.

### RECOMMENDATION SYSTEM

The recommendation system is implemented using an ensemble method, including: Apache Spark's Alternating Least Squares (ALS) model, Sklearn's Gradient Boosting model, and a cosine similarity matrix. I tried four different types of recommendation systems:
  * Factorization Recommender
  * Gradient Boosting
  * Item Content Recommender
  * Full Ensemble of all three

The models were each evaluated using RMSE scores calculated on a hold out test group. 


### Installations Required to Run the Code:
Mongodb, pymongo, anaconda, spark, pyspark, ggplot

## HOW TO RUN THE CODE:

1. Begin by running the file, scraper\_main.py, in the terminal with 

```python
python scraper_main.py
```

This will save three tables (ratings, user info, and route info), including URLs and HTML, to a mongodb database.

2. Next, run the file, parse\_clean\_store\_main.py, to parse html, clean the contents, and store user/route info in a mongodb database.

```python
python parse_clean_store_main.py
```

3. Run the function, create\_ratings\_matrix.py, to create a utility matrix for the als model. 

```python
python create_ratings_matrix.py
```

4. Run the jupyter notebook file, ensemble\_model\_setup.ipynb, to prep the data for the ensemble model. 

5. Run the file, gradient\_boosting\_model.py, to get a gradient boosted model, or you can use the model already saved as a pickle file

6. Run the file, als\_model\_test.py, to create both a validation als model and a final als model, or use saved models.

7. Run the file, ensemble\_model.py, to obtain an RMSE score for the ensemble model.
  

## FUTURE WORK
  * Add bouldering routes
  * Extend to outside of Washington
  * Focus model on only top recommendations
  * Find a faster way to run my model on the website

## SOURCES

1) MountainProject.com

2) Koren, Yehuda, Robert Bell, and Chris Volinsky. "Matrix factorization techniques for recommender systems." Computer 42.8 (2009).

3) Leskovec, Jure, Anand Rajaraman, and Jeffrey David Ullman. Mining of massive datasets. Cambridge University Press, 2014.

3) Tabony, Jade. https://github.com/Jadetabony/wta_hikes