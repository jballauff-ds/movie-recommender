import pandas as pd
import requests
from io import BytesIO
import streamlit as st

from src.img_scraper import get_img_url

class Scroller:
    # df ordered from best to worst with movieId, tmdbId, mean(on show ratings), counts (on show ratings), title, genres
    N_COLS = 5

    def __init__(self, show_ratings = False):
        self.show_ratings = show_ratings

    def show(self):
        if self.show_ratings:
            ratings = pd.cut(self.df["mean"], bins = [-float("inf"),0.5,1,1.5,2,2.5,3,3.5,4,4.5,float("inf")], labels = ["05","10","15","20","25","30","35","40","45","50"]).values
        cols = st.columns(self.N_COLS)
        for i in self.positions:
            with cols[i-self.positions[0]]:
                st.text(self.df["title"].iloc[i])
                if self.imgs[i]: st.image(self.imgs[i])
                else:
                    st.image("assets\placeholder_img.png") 
                st.text(self.df["genres"].iloc[i])
                if self.show_ratings:
                    col1, col2 = st.columns([0.7,0.3])
                    with col1: st.image(f"assets/{ratings[i]}_stars.png")
                    with col2: st.text(self.df["count"].iloc[i])
        col_scroll_left, col_blank, col_scroll_right = st.columns([0.1,0.8,0.1])
        with col_scroll_left: st.button("<-", on_click=self.__scroll, args = ["left"], key = str(id(self)) + "left")
        with col_scroll_right: st.button("->", on_click=self.__scroll, args = ["right"], key = str(id(self)) + "right")


    def update(self, df):
        self.df = df
        self.__load()

    def __load(self):
        self.imgs = self.__scrape_images()
        length = len(self.imgs)
        if length < self.N_COLS: self.positions = range(0, length)
        else: self.positions = range(0,self.N_COLS)

    def __scrape_images(self):
        urls = [get_img_url("https://www.themoviedb.org/movie/" + url) for url in self.df["tmdbId"]]
        imgs = []
        for url in urls:
            try:
                response = requests.get(url)
                imgs.append(BytesIO(response.content))
            except:
                imgs.append(None)
        return imgs

    def __scroll(self, dir):
        if dir == "left": 
            if self.positions[0] > 0: self.positions = [x-1 for x in self.positions]
        elif dir == "right":
            lim = len(self.imgs)-1 
            if self.positions[-1] < lim: self.positions = [x+1 for x in self.positions]