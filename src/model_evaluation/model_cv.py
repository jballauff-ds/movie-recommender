import pandas as pd
from surprise import Reader, Dataset, NormalPredictor, SVD, KNNBasic, KNNBaseline, KNNWithMeans, NMF, SlopeOne
from surprise.model_selection import cross_validate

ratings_df = pd.read_csv("data/ratings.csv")
reader = Reader(rating_scale=(0.5, 5))
data = Dataset.load_from_df(ratings_df[["userId", "movieId", "rating"]], reader)

models = {
    "norm": NormalPredictor(), 
    "knnBasic" : KNNBasic(sim_options={ 'name': 'cosine', 'user_based': True}), 
    "knnBasel" : KNNBaseline(sim_options={ 'name': 'cosine', 'user_based': True}), 
    "knnMeans" : KNNWithMeans(sim_options={ 'name': 'cosine', 'user_based': True}),
    "SVD" : SVD(),
    "NMF" : NMF(),
    "Slope" : SlopeOne()
}

scores_df = pd.DataFrame(index = ["test_rmse", "test_mae", "test_fcp", "fit_time", "test_time"])
for name, model in models.items():
    cv = cross_validate(model, data, measures=["RMSE", "MAE", "fcp"], n_jobs = 6, cv=5, verbose=False)
    scores_df[name] = pd.DataFrame(cv).mean(axis = 0)

scores_df.to_csv("assets/Model_CV_Scores.csv")