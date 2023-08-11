import pandas as pd
from surprise import Reader, Dataset, SVD
from surprise.model_selection import GridSearchCV

ratings_df = pd.read_csv("data/ratings.csv")
reader = Reader(rating_scale=(0.5, 5))
data = Dataset.load_from_df(ratings_df[["userId", "movieId", "rating"]], reader)

param_grid = {
    "n_factors" : [200],
    "n_epochs": [300], 
    "lr_all": [0.003], 
    "reg_all": [0.1]
}
gs = GridSearchCV(SVD, param_grid, measures=["rmse", "mae"], cv=3, n_jobs = -1)
gs.fit(data)

print(gs.best_score["rmse"])
print(gs.best_params["rmse"])

#algo = gs.best_estimator["rmse"]
#svg_pred = algo.fit(train).test(test)
