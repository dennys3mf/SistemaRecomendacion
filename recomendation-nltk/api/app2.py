from flask import Flask, request, jsonify
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors
import dask.dataframe as dp
from flask_cors import CORS

nltk.download('punkt')

app = Flask(__name__)
CORS(app)

app.config['DATA_LOADED'] = False
app.config['DF'] = None
app.config['SIMILARITY'] = None
app.config['X'] = None

def read_files():
    movies = dp.read_csv('movies.csv')
    return movies

def clean_data(movies):
    movies.dropna()
    return movies

def transform_dask(obj):
    List = []
    for i in obj.split('|'):
        List.append(i)
    return List

def apply_transform(movies):
    movies['genres'] = movies['genres'].map(transform_dask)
    return movies

def format_data(movies):
    df = movies[['movieId','title','genres']]
    df['genres'] = df['genres'].apply(lambda x: " ".join(x))
    df['genres'] = df['genres'].apply(lambda x:x.lower())
    #df['title'] = df['title'].apply(lambda x:[i.replace(" ","") for i in x])
    return df

@app.route("/recommendations/<string:movie_title>", methods=['GET'])
def get_recommendations_for_movie(movie_title):
    if not app.config['DATA_LOADED']:
        return jsonify({'error': 'Data has not been loaded. Call /load_data first.'})

    df = app.config['DF']
    vectorizer = CountVectorizer(token_pattern=r"(?u)\b\w+\b", stop_words='english')
    X = vectorizer.fit_transform(df['genres'])
    knn = NearestNeighbors(n_neighbors=10, algorithm='brute', metric='cosine')
    knn.fit(X)

    if df is not None:
        title_index = df[df['title'] == movie_title].index.compute()[0]
        distances, indices = knn.kneighbors(X[title_index])
        recommended_movies_df = df.compute().iloc[indices[0]]
        recommended_movies = recommended_movies_df['title'].tolist()

        return jsonify({'movie_title': movie_title, 'recommendations': recommended_movies})
    else:
        return jsonify({'error': 'Movie not found in the dataset.'})


@app.route("/", methods=['POST','GET'])
def hello():
    return jsonify({'message': 'API v1'})

@app.route('/load_data', methods=['GET'])
def load_data():
    if not app.config['DATA_LOADED']:
        movies = read_files()
        movies = clean_data(movies)
        movies = apply_transform(movies)
        df = format_data(movies)
        app.config['DATA_LOADED'] = True
        app.config['DF'] = df
        return jsonify({'message': 'Data loaded successfully!'})
    else:
        return jsonify({'message': 'Data has already been loaded.'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)