import streamlit as st
import pandas as pd

from src.widgets import Scroller
from src.recommender import Popular, Item_based, User_based

## static vars
MAX_REC = 10
INIT_USER = 1

# callback functions
def update_popular_recommender():
    if "genre" in st.session_state: genre = st.session_state["genre"]
    else: genre = ""

    all_ratings = st.session_state["popular_recommender"].get_ratings().merge(st.session_state["movies_df"], how = "left", on = "movieId")
    mask = all_ratings["movieId"].isin(st.session_state["user_not_seen"]["movieId"]) & all_ratings["genres"].str.contains(genre)
    top_ratings = all_ratings.loc[mask,:].nlargest(MAX_REC, "weighted_rating")
    top_ratings = top_ratings.merge(st.session_state["links_df"], how = "left", on = "movieId")
    st.session_state["popular_widget"].update(top_ratings)

def update_item_recommender():
    if "current_item" in st.session_state: movie = st.session_state["current_item"]
    else: movie = st.session_state["user_has_rated"]["movieId"].values[0]
    correlations = st.session_state["item_recommender"].get_correlations(movie)
    top_correlations = correlations.loc[correlations["movieId"].isin(st.session_state["user_not_seen"]["movieId"]),:].nlargest(MAX_REC, "corr")
    top_correlations = top_correlations.merge(st.session_state["movies_df"], how = "left", on = "movieId").merge(st.session_state["links_df"], how = "left", on = "movieId")
    st.session_state["item_widget"].update(top_correlations)

def update_user_recommender():
    predictions = st.session_state["user_recommender"].get_predictions(st.session_state["current_user"], st.session_state["user_not_seen"]["movieId"].values)
    st.session_state["user_not_seen"]["predictions"] = predictions
    top_predictions = st.session_state["user_not_seen"].nlargest(MAX_REC, "predictions").merge(st.session_state["links_df"], how = "left", on = "movieId")
    st.session_state["user_widget"].update(top_predictions)

def update_user():
    if "genre" in st.session_state: st.session_state["genre"] = ""
    user_ratings = st.session_state["ratings_df"].loc[st.session_state["ratings_df"]["userId"] == st.session_state["current_user"],:].drop_duplicates()
    st.session_state["user_has_rated"] = user_ratings.merge(st.session_state["movies_df"], how = "left", on = "movieId").sort_values("rating", ascending = False)
    st.session_state["user_not_seen"] = st.session_state["movies_df"].loc[~st.session_state["movies_df"]["movieId"].isin(st.session_state["user_has_rated"]["movieId"])].copy()
    update_popular_recommender()
    update_item_recommender()
    update_user_recommender()

# static states
if "new_session" not in st.session_state:
    st.session_state["new_session"] = True
if "ratings_df" not in st.session_state:
    st.session_state["ratings_df"] = pd.read_csv("data/ratings.csv")
if "movies_df" not in st.session_state:
    st.session_state["movies_df"] = pd.read_csv("data/movies.csv")
if "links_df" not in st.session_state:
    st.session_state["links_df"] = pd.read_csv("data/links.csv",  dtype={'tmdbId': object})
if "user_ids" not in st.session_state:
    st.session_state["user_id"] = st.session_state["ratings_df"]["userId"].drop_duplicates()
if "genres" not in st.session_state:
    st.session_state["genres"] = [ "", "Action", "Adventure", "Animation", "Children", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western", "(no genres listed)" ]
if "popular_recommender" not in st.session_state:
    st.session_state["popular_recommender"] = Popular(rating_weight = 1, popular_weight = 0.7)
if "popular_widget" not in st.session_state:
    st.session_state["popular_widget"] = Scroller(show_ratings=True)
if "item_recommender" not in st.session_state:
    st.session_state["item_recommender"] = Item_based(10)
if "item_widget" not in st.session_state:
    st.session_state["item_widget"] = Scroller()
if "user_recommender" not in st.session_state:
    st.session_state["user_recommender"] = User_based("assets/svd.sav")
if "user_widget" not in st.session_state:
    st.session_state["user_widget"] = Scroller()

# init session
if st.session_state["new_session"]:
    st.session_state["current_user"] = INIT_USER
    update_user()
    st.session_state["new_session"] = False

st.expander("Admin").selectbox("", st.session_state["user_id"], on_change=update_user, key = "current_user")
side = st.sidebar

ratings = pd.cut(st.session_state["user_has_rated"]["rating"], bins = [-float("inf"),0.5,1,1.5,2,2.5,3,3.5,4,4.5,float("inf")], labels = ["05","10","15","20","25","30","35","40","45","50"]).values
titles = st.session_state["user_has_rated"]["title"].values

st.header(f"Welcome user {st.session_state['current_user']}!")
with side:
    st.header("Your rated movies:")
    for i in range(0,len(titles)):
        st.text(titles[i])
        st.image(f"assets/{ratings[i]}_stars.png", width = 70)

col_subh, col_blank, col_sel = st.columns([0.6, 0.1, 0.3])
with col_subh: st.subheader("Popular with our customers:")
with col_sel: st.selectbox("Genre", st.session_state["genres"], key="genre", on_change=update_popular_recommender)
st.session_state["popular_widget"].show()

options = st.session_state["user_has_rated"].loc[st.session_state["user_has_rated"]["rating"] >= 4,:]
st.subheader("Recommended because you like:")
st.selectbox("", options = options["movieId"].values, 
             format_func = lambda x: options.loc[options["movieId"] == x, "title"].values[0],
             on_change = update_item_recommender,
             key = "current_item")
st.session_state["item_widget"].show()

st.subheader("Selected for you:")
st.session_state["user_widget"].show()