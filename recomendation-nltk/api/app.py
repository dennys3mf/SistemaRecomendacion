from flask import Flask, request, jsonify
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.sql.functions import col
import redis
import pickle
import pandas as pd
import ast
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# Initialize Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Initialize Spark
spark = SparkSession.builder \
    .appName("RecommendationSystem") \
    .config("spark.driver.memory", "8g") \
    .config("spark.executor.memory", "8g") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.default.parallelism", "200") \
    .getOrCreate()

app.config['DATA_LOADED'] = False
app.config['MODEL'] = None
app.config['MOVIES'] = None

def read_files_with_spark():
    movies = spark.read.csv('movies.csv', header=True, inferSchema=True)
    links = spark.read.csv('links.csv', header=True, inferSchema=True)
    ratings = spark.read.csv('ratings.csv', header=True, inferSchema=True)
    tags = spark.read.csv('tags.csv', header=True, inferSchema=True)
    return movies, links, ratings, tags

def merge_data_with_spark(movies, links, ratings, tags):
    movies = movies.join(links, on='movieId', how='inner')
    movies = movies.join(tags, on='movieId', how='left')
    movies = movies.dropna()
    return movies

def train_als_model(ratings):
    als = ALS(maxIter=10, regParam=0.01, userCol="userId", itemCol="movieId", ratingCol="rating", coldStartStrategy="drop")
    model = als.fit(ratings)
    return model

def recommend_for_user_with_spark(user_id, model, movies, num_recommendations=10):
    user_recommendations = model.recommendForAllUsers(num_recommendations).filter(col("userId") == user_id).select("recommendations").collect()
    if user_recommendations:
        user_recommendations = user_recommendations[0][0]
        recommended_movie_ids = [row.movieId for row in user_recommendations]
        recommended_movies = movies.filter(col("movieId").isin(recommended_movie_ids)).select("title").distinct().collect()
        return [row.title for row in recommended_movies]
    else:
        return []

@app.route('/load_data', methods=['GET'])
def load_data_with_spark():
    start_time = time.time()
    if not app.config['DATA_LOADED']:
        movies, links, ratings, tags = read_files_with_spark()
        movies = merge_data_with_spark(movies, links, ratings, tags)
        model = train_als_model(ratings)
        
        app.config['DATA_LOADED'] = True
        app.config['MOVIES'] = movies
        app.config['MODEL'] = model
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        return jsonify({'message': 'Data loaded successfully with Spark!', 'load_time': elapsed_time})
    else:
        return jsonify({'message': 'Data has already been loaded.'})

@app.route("/user_recommendations/<int:user_id>", methods=['GET'])
def get_user_recommendations_with_spark(user_id):
    start_time = time.time()
    if not app.config['DATA_LOADED']:
        return jsonify({'error': 'Data has not been loaded. Call /load_data first.'})

    model = app.config['MODEL']
    movies = app.config['MOVIES']
    
    recommendations = recommend_for_user_with_spark(user_id, model, movies)
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    return jsonify({'user_id': user_id, 'recommendations': recommendations, 'load_time': elapsed_time})

@app.route("/", methods=['POST', 'GET'])
def hello():
    return jsonify({'message': 'API v1'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
