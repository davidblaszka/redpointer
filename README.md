# Project Title
**RedPointer**

# Business Understanding
There are a few different rock climbing sites on the internet that list a giant amount of routes. Mountain project is by far the most common in America. Every route has the option for users to rate the route 1 out of 4 stars and the list of all those users. Similarly, every user also has a list of every route the have rated along with their given ratings. The MVP for this project will build a model that will recommend routes to people based on either their previous selections, or top routes if they are a new user. 

# Data Preparation
A big part of this project will be web scraping, or using mountain project’s API. Once the data is collected into a dataframe using Pandas, it will be cleaned. The first part is to make a matrix of user ids x routes with the ratings as the values. I’ll have to come up with a scheme for filling nulls. 

# Modeling
The model will be an ensemble method using GradientBoosting and matrix factorization.

# Evaluation
I’ll create a hold out set and see how well it predicts the routes these users actually gave values to.

# Deployment
I’ll have a website where you can either list a few routes you like, or if possible, attach the url to your account page to give you back recommendations for climbs you’d like to do. 

## Installations:
Mongodb, anaconda, spark

## How to run the code:

1. Begin by running the file, scraper\_main.py, in the terminal with 

```python
python scraper_main.py
```

This will save three tables (ratings, user info, and route info), including urls and html, to a mongodb database.

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
  
