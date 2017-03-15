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

