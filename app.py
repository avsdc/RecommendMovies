import pandas as pd
import numpy as np
from flask import Flask, render_template, render_template, request, session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Safely fetch the secret key or fallback during local testing
#configure secret key to key in .env file
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY', 'dev-fallback-key-only')

# Load datasets
movies_df = pd.read_csv('data/movies.csv')

# Converts bytes to a readable format for pandas
ratings_df = pd.read_csv('data/ratings.csv')

movies_df.dropna(subset=["movieId", "title", "genres"], inplace=True)
ratings_df.dropna(subset=["userId", "movieId", "rating"], inplace=True)

movies_df.drop_duplicates(subset=["movieId"], keep="last", inplace=True)
ratings_df.drop_duplicates(subset=["userId", "movieId"], keep="last", inplace=True)

movies_df = movies_df.head(5000)
ratings_df = ratings_df.head(5000)


#***************************************************
#                 CONTENT BASED FILTERING          *          
#***************************************************

# Vectorize textual metadata using TF-IDF
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_df['genres'])
content_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

def get_content_filtered_recommendations(movie_title, top_n):
    
    try:
        idx = movies_df[movies_df['title'].str.lower() == movie_title.lower()].index[0]
    except IndexError:
        return f"Movie '{movie_title}' not found in the dataset."
   
    # Get pairwise similarity scores of all movies with that movie
    sim_scores = list(enumerate(content_sim[idx])) 
    
    # Sort the movies based on the similarity scores in descending order
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
          
    # EXCLUSION STEP: Filter out the input movie itself 
    # Option A: Slice from index 1 if you are certain it is the top match
    # Option B (Safer): Explicitly remove the matching index
    
    sim_scores = [score for score in sim_scores if score[0] != idx]
    
    # Get the top N elements from the filtered list
    sim_scores = sim_scores[:top_n]
    
    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]
    
    # Return the top N most similar movies
    return movies_df['title'].iloc[movie_indices].tolist()

#***************************************************
#              COLLABORATIVE FILTERING             *          
#***************************************************
# Pivot to create a sparse User-Item Rating Matrix

user_item_matrix = ratings_df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
user_sim = cosine_similarity(user_item_matrix)
user_sim_df = pd.DataFrame(user_sim, index=user_item_matrix.index, columns=user_item_matrix.index)

def get_collaborative_recommendations(user_id, top_n):
    if user_id not in user_item_matrix.index:
        return []
    
    # Find most similar users
    similar_users = user_sim_df[user_id].sort_values(ascending=False).index[1:]
    
    # Extract candidate movies watched by similar users but unwatched by target user
    target_user = user_item_matrix.loc[user_id]
    movies_not_watched = target_user[target_user == 0].index
    
    predictions = {}
    for movie in movies_not_watched:
        score = 0
        weight = 0
        for similar_user in similar_users:
            user_rating = user_item_matrix.loc[similar_user, movie]
            if user_rating > 0:
                similarity = user_sim_df.loc[user_id, similar_user]
                score += user_rating * similarity
                weight += similarity
        
        if weight > 0:
            predictions[movie] = score / weight
            
    sorted_movies = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:top_n]
    movie_ids = [m[0] for m in sorted_movies]
    
    return movies_df[movies_df['movieId'].isin(movie_ids)]['title'].tolist()


#*************************END POINTS********************
@app.route('/', methods=['GET', 'POST'])
def index():            
    # Pass existing items to populate dropdown selectors
    all_movies = movies_df['title'].tolist()
    all_users = ratings_df['userId'].unique().tolist()
    
    filter_type = request.form.get('filter_type')
    recommendations = []
    target1 = ""
    target2 = ""
    
    if filter_type == 'content':
        target1 = request.form.get('movie_title')
        recommendations = get_content_filtered_recommendations(target1, 10)
    elif filter_type == 'collaborative':
        target2 = request.form.get('user_id')
        if target2:
            recommendations = get_collaborative_recommendations(int(target2), 10)
            
    #Create session variables        
    session['val1'] = target1
    session['val2'] = target2
    session['recs'] = recommendations
        
    return render_template('index.html', movies=all_movies, users=all_users, filter_type=filter_type, val1=session['val1'], val2=session['val2'], recs=session['recs'])

if __name__ == '__main__':
    app.run(debug=True)


