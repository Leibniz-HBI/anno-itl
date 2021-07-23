""" Everything to load data and to make datasets from them. Will be growing as
input data is more specific
"""
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer('paraphrase-mpnet-base-v2')

DATA_PATH = './datasets'
EMBEDDINGS_PATH = './embeddings'


def dataset_from_csv(filename, load_embeddings=False):
    """ Creates a dataset from a csv.
    Takes a CSV filename as input (must in be in datasets folder) and creates a
    list of sentences from i, as well as a list of their embeddings.
    The CSV needs to have a column named sentece. For now,
    all is done at once and embeddings are not stored.
    """
    pd_data = pd.read_csv(f'{DATA_PATH}/{filename}.csv')
    sentences = pd_data['sentence'].to_list()
    if load_embeddings:
        sentence_embeddings = np.load(f'{EMBEDDINGS_PATH}/{filename}.npy')
    else:
        sentence_embeddings = model.encode(sentences)
    if 'categories' in pd_data:
        sentences = [create_sentence_dict(id, sentence_info[0], category=sentence_info[1])
                    for id, sentence_info in enumerate(zip(pd_data.sentences, pd_data.categories))]
    else:
        sentences = [create_sentence_dict(id, sentence) for id, sentence in enumerate(pd_data['sentence'])]


    return sentences, sentence_embeddings


def store_embeddings(embeddings, filename):
    """Stores embeddings on disk.
    If these are corespondend to a data set in the data sets folder, give it the
    same name for loading.
    """
    np.save(f'{EMBEDDINGS_PATH}/{filename}.npy', embeddings)


def create_sentence_dict(id, sentence, category = ''):
    return {'id': id, 'sentence': sentence, 'category': category}


def get_similar_args():
    print('späder päder')
