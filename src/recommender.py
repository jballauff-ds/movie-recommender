import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from surprise.dump import load

ratings_df = pd.read_csv("data/ratings.csv")

class Popular:
    def __init__(self, rating_weight = 1, popular_weight = 0.8):
        self.movie_ratings_df = ratings_df.groupby('movieId')['rating'].agg(['mean', 'count']).reset_index()
        self.movie_ratings_df['weighted_rating'] = self.__calculate_weighted_ratings(rating_weight, popular_weight)
        self.movie_ratings_df.sort_values("weighted_rating", ascending=False, inplace=True)

    def get_ratings(self):
        return self.movie_ratings_df

    def __calculate_weighted_ratings(self, rating_weight, popular_weight):
        movie_ratings_df_scaled = MinMaxScaler().set_output(transform = "pandas").fit_transform(self.movie_ratings_df)
        movie_ratings_df_scaled['weighted_mean'] = movie_ratings_df_scaled['mean'] * rating_weight
        movie_ratings_df_scaled['weighted_count'] = movie_ratings_df_scaled['count'] * popular_weight
        return movie_ratings_df_scaled['weighted_mean'].add(movie_ratings_df_scaled["weighted_count"])
    

class Item_based:
    def __init__(self, min_ratings = 20):
        self.min_ratings = min_ratings
        self.user_movie_matrix = pd.pivot_table(data=ratings_df, values='rating', index='userId', columns='movieId', fill_value=0)
        self.cosine_cor_matrix = pd.DataFrame(cosine_similarity(self.user_movie_matrix.T), columns=self.user_movie_matrix.columns, index=self.user_movie_matrix.columns)

    def get_correlations(self, movie_id):
        cosines = self.cosine_cor_matrix[movie_id][self.cosine_cor_matrix.index != movie_id]
        n_ratings = pd.Series([sum((self.user_movie_matrix[movie_id] > 0) & (self.user_movie_matrix[other] > 0)) for other in cosines.index], index = cosines.index)
        corrs = cosines.loc[n_ratings >= self.min_ratings]
        corrs = corrs.reset_index()
        corrs.columns.values[1] = "corr"
        return corrs
    

class User_based:
    def __init__(self, model_path):
        pred, self.model = load(model_path)

    def get_predictions(self, user_id, movie_ids):
        predictions = []
        for movie in movie_ids:
            predictions.append(self.model.predict(user_id,movie)[3])
        return predictions