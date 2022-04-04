import json
import requests
import pickle
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import streamlit as st


URL = "https://slot-ml.com/"
TOKEN = "f5d972e2a847e8fa8586a292579d972a07485796"


class FeatureSelector(BaseEstimator, TransformerMixin):
    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X[self.columns]


def get_file(URL, TOKEN):
    input = requests.get(url=f'{URL}api/v1/users/{TOKEN}/vectors/?random')
    try:
        x = input.json()
    except ValueError:
        x = json.loads(input.text.replace('\n\t', ' '))
    return x


def predict(x, clust_model, preprocess):
    x_trn = preprocess.transform(pd.DataFrame().from_records([x]).drop('id', axis=1))
    y_pred = clust_model.predict(x_trn)
    answer = {'vector': x['id'], "class": y_pred[0]}
    return answer


def send_pred(answer, URL, TOKEN):
    status = requests.post(f'{URL}api/v1/users/{TOKEN}/results', data=answer)
    return status


def get_stats(URL, TOKEN):
    ans = requests.get(url=f'{URL}api/v1/users/{TOKEN}/stats')
    return ans.json()['stats'][0]


def job(URL, TOKEN, clust_model, preprocess):
    x = get_file(URL, TOKEN)
    ans = predict(x, clust_model, preprocess)
    s = send_pred(ans, URL, TOKEN)
    return s


if __name__ == '__main__':
    preprocess = pickle.load(open('prep.p', 'rb'))
    clust_model = pickle.load(open('km.p', 'rb'))
    if 'acc' not in st.session_state:
        st.session_state['acc'] = []
    if 'avg_time' not in st.session_state:
        st.session_state['avg_time'] = []

    num_files = int(st.number_input('Insert number of files to process', value=40, step=1))
    my_bar = st.progress(0)
    start = st.button("Start processing")

    if start:
        for i in range(num_files):
            stat = job(URL, TOKEN, clust_model, preprocess)
            my_bar.progress((i + 1) / num_files)
            ans = get_stats(URL, TOKEN)
            st.session_state['acc'].append(ans['avg_accuracy'])
            st.session_state['avg_time'].append(ans['avg_spent_time'])

    if st.button('Show processing stats'):
        st.line_chart(pd.DataFrame({'avg_acc': st.session_state['acc']}))
        st.line_chart(pd.DataFrame({'avg_spent_time': st.session_state['avg_time']}))
