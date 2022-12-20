# YelpDataAnalysis (09/2022)
<img src="https://user-images.githubusercontent.com/59380765/205797142-b168bbdd-693f-4967-886d-3d89008f583a.png" height="100">

**Dataset Link Yelp: https://www.kaggle.com/yelp-dataset/yelp-dataset** \
**Dataset Link Twitter: https://drive.google.com/uc?id=1zSkudfJkgL_NChvK2EqzU50sGpB375Aq** \
[![Demo Link](https://user-images.githubusercontent.com/59380765/205802177-665f2d4f-f4b7-40df-a560-23e1745fe1cf.png)](https://www.youtube.com/watch?v=JlHGKPuRJCA)


## Problem Formulation: 
Figuring out a place to eat is usually a challenge. We are often faced with so many choices that it may be difficult to determine the best option. It is also difficult to sort through many reviews and decide based on that. Yelp has so much data, that it is not always possible to get a clear idea of where to go from all this information along with the fact that reviews may go unnoticed and the ratings may be deceiving. Therefore, having an application that can analyze the reviews from customers and use that data to create ratings based on negative and positive reviews would be helpful. Furthermore, generating these ratings and displaying what is the best, along with the worst place to eat depending on different geolocations is a useful feature. It can help inform customers where to especially avoid going versus a place that is worth checking out. 

## Solution/ Goal: 
Using sentiment analysis along with ML to look through customer reviews and figure out what is the best and worst food places in different zip code areas by using geolocation and other data that is included in the Yelp dataset. In addition, we will have a web application that uses an interactive map to display this information.



### Part 1: Data Collection
Requirements:
For the data collection process, we collected data from an already pre-existing Yelp dataset that has data on Yelp reviews, restaurants, and business data.
Part 1&2 (Processing, Data Collection):
The application will read the data from the json files: business.json, reviews.json
Data should contain information about the restaurants:
name,business unique identifier, zip code, gps coordinates, review text
The application will preprocess the JSON files using python and pyspark
The application will store these files in a MySQL database
The application will process the sentiment analysis on reviews.json
The application will join the tables in the database to be used to create the frontend
Part 3 (Frontend, Usability):
The user will search for a zip code in the web application
the visualizations should update with the user’s input
The user will be able to view the best and worst restaurant in the area
Top 10 lists visualization
The user will be able to see the ratings based on the sentiment analysis of the reviews

Design:
For the Yelp dataset, we want to ensure all the reviews are in one language and remove incomprehensible/null from the dataset.
 
Each file has 1 JSON object per line.
The business.json file contains location data, business attributes, and business categories.
name, postal_code, latitude, longitude
The review.json file has the review text data and business_id (the unique business identifier for the business that the review belongs to).

### Part 2: Preprocessing and Sentiment Analysis 

Requirements: 

Required Libraries
import pyspark
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyspark.sql import functions as func
from pyspark.sql.types import StringType,FloatType
import nltk
from pyspark.sql import SparkSession
from pyspark.ml.classification import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import IDF
from wordcloud import WordCloud
from nltk.corpus import stopwords
from  nltk.stem import SnowballStemmer
import re
from pyspark.sql.functions import lit

### Data Flow Chart:
![image](https://user-images.githubusercontent.com/59380765/205798656-ea64de0c-bfb5-4c29-a562-2d258b20e45a.png)

#### ERD Model: 
![image](https://user-images.githubusercontent.com/59380765/205798974-09300efc-f25c-470e-bf26-6a705a2faa8b.png)


We want to join two tables for use in our front end: The reviews table and the business table.
Before they are joined, they must both be individually inserted into a MySQL database as tables with cleaned columns.

For the business.json file, null values must be accounted for and once the data frame is preprocessed, it must be inserted into the MySQL database.

For sentiment analysis, we want to use a machine learning model to determine the rating of a restaurant. 
A logistic regression model must be run on a twitter dataset for the tweet labels and tweet text features (features show the word count and word importance of tweets). 
To obtain the features, the tweet text must be cleaned and preprocessed. After running the model, the yelp_academic_dataset_review.json must be read in, cleaned, and preprocessed so as to remove any empty values and token words and obtain the review text features. 
For data preprocessing and running the Logistic regression model a spark session must be built and running.
A dataframe containing all the review features and twitter work tokens must be transformed to obtain the prediction value of whether the review is positive or negative.
To obtain the review features, the review text must be cleaned and preprocessed. The resulting dataframe size will be very large so it must be written into a parquet (zipped to a gzip) file to avoid crashing of the spark session through memory outage. The sentiment review must be calculated by multiplying the average prediction column of the sentiment dataframe by 10. Lastly, the dataframe must load the parquet file to be iterated and inserted into the MySQL database.

Design: 
We first train the model using the twitter dataset for sentiment analysis
this analysis uses logistic regression for predicting the sentiment given textual input
we trained the model with the tweets sentiment to bring in a sentiment score for the reviews left by users
the reasoning behind training the model with the twitter data versus using yelp stars is so that we are able to get the most accurate prediction for our model
we noticed there was a discrepancy between the star ratings people gave and the feedback they left in text (high star rating but sentiment was lacking and vice versa)
Implementation:
Import all necessary libraries and read in the data of twitter dataset
Start a spark session and increase the memory size of the heap to avoid crashing.
Drop any unnecessary columns & removed punctuation/common words from the text & drop duplicate values
Sentiment analysis → negative target value assigned to 0, neutral assigned to 2, and positive assigned to 4
If target is positive, assign label to 1, neutral or negative are assigned as 0
Used nltk package for tweet text preprocessing
Used tokenizer & CountVectorizer for word frequency and TF-IDF for word importance → this gets you the tweet features
Split into training/testing data & run logistic regression model on test dataframe
Read in yelpreview dataset
Drop any unnecessary columns & removed punctuation/common words from the text
Sentiment analysis → negative label assigned to 0 and positive label assigned to 1 
Used nltk package for text preprocessing
Used tokenizer & CountVectorizer for word frequency and TF-IDF for word importance to obtain review features
Transform the dataframe containing all the review text features and work tokens to obtain predictions
Calculate rating by multiplying average prediction column by 10
Insert into MySQL database

Evaluation:
Execution graphs with varying # Spark workers (1 vs. 2), and varying data sizes
Struggled working with our EC2 instance since our Spark session would crash when trying to train the model
learned how to adjust the executor memory at run time and read and write to parquet files
learned what pickling of dataframes does

From the graph we can see that as we increased the number of spark workers, the execution time decreased. Looking at the elbow graph, we seem to reach a point of diminishing returns at around 4 spark workers here. This execution time is for all code besides the actual training of the model. This is because on the EC2 instance running with 8 workers, the training was taking ~40 minutes just by itself. Due to time and memory constraints we believed this was the most practical and effective way to compare workers versus time. 

<img src="https://user-images.githubusercontent.com/59380765/205797699-93f126be-20c6-4ffc-982e-8280dea3f020.png" height="300">


### Part 3: Web Interface
Requirements:
 Build an interactive geo heat map that shows the best restaurants within a specified radius 
Users have ability to filter results based on zipcode
corresponding visualizations are reflect the with the user’s filtering of zipcode
Heatmap of businesses from yelp dataset with sentiment score
Show best and worst restaurants overall
Top restaurants List in area
Fetches entire US or based on Zip Code from MySQL
Worst restaurants List in area
Fetches entire US or based on Zip Code from MySQL
Design: 
The design for this part follows the structure of a CRUD web application. All the data from the previous parts was inserted into a MySQL database. The table had a schema that allowed for all the appropriate queries to take place. Based on the user requirements which we drafted up earlier, we came up with 2 main components that needed to be displayed -  A set of tables and an interactive heatmap. The front end would have to query the back end to retrieve the review values from the database based on the entered ZIP code.

Implementation:
Django
Python,HTML,CSS
Sentiment Heatmap
Folium Library 
Location Markers
Layers for negative/positive heat
Zoom on ZIP Code
MYSQL for data retrieval

The heatmap is a multilayered map where you can filter your views from all locations, only positive locations, or only negative locations. You can zoom and scroll around the map as much as you please in order to get a true understanding of the areas that contain highly rated vs poorly rated establishments. The tables dynamically update results based on whatever ZIP code is entered by the user. By default the map is zoomed out to capture the entire United States. The default tables also showcase the Top 10 and Bottom 10 establishments which we found with our sentiment analysis. 




## Conclusion of project
### Evaluation: Overall, the web interface gives a nice understanding of our dataset and accomplishes what we were trying to achieve. One large element that Yelp lacks is to filter the worst rated establishments, and star rating based on textual sentiment. With this project we were able to fill in that missing element	


