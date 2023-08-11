import pandas as pd
from surprise import Reader, Dataset, SVD
from surprise.model_selection import train_test_split
from surprise.dump import dump

ratings_df = pd.read_csv("data/ratings.csv")
reader = Reader(rating_scale=(0.5, 5))
data = Dataset.load_from_df(ratings_df[["userId", "movieId", "rating"]], reader)

train, test = train_test_split(data, test_size=0.2, random_state=42)

# from best GridSearchCV {'n_factors': 200, 'n_epochs': 300, 'lr_all': 0.003, 'reg_all': 0.1}
model = SVD(n_factors = 200, n_epochs = 300, lr_all = 0.003, reg_all = 0.1)

model.fit(train)
pred = model.test(test)

dump("assets/svd.sav", algo=model)
