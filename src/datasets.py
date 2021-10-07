""" Everything to load data and to make datasets from them. Will be growing as
input data is more specific
"""
import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from sentence_transformers.models import Normalize
import numpy as np
import faiss

embedding_model = SentenceTransformer('paraphrase-mpnet-base-v2')

model = SentenceTransformer(modules=[embedding_model, Normalize()])

FAISS_PATH = './faiss_indexes'
DATA_PATH = './datasets'
EMBEDDINGS_PATH = './embeddings'


def dataset_from_csv(filename):
    """ Creates a dataset from a csv.
    Takes a CSV filename as input (must in be in datasets folder) and creates a
    list of sentences from i, as well as a list of their embeddings.
    The CSV needs to have a column named sentece. For now,
    all is done at once and embeddings are not stored.
    The function will try to first load an index, then to load embeddings and
    then will create and store embeddings and a faiss index.
    The function will also look for a column with IDs, if no column with Ids is
    in the csv, the ids will be generated from the dataframes' index.
    """
    pd_data = pd.read_csv(f'{DATA_PATH}/{filename}.csv')
    # add blank category column to data without category
    if 'category' not in pd_data:
        pd_data['category'] = None
    if 'id' not in pd_data:
        pd_data.insert(0, 'id', pd_data.index)

    if os.path.isfile(f'{FAISS_PATH}/{filename}.faiss'):
        search_index = faiss.read_index(f'{FAISS_PATH}/{filename}.faiss')
    elif os.path.isfile(f'{EMBEDDINGS_PATH}/{filename}.npy'):
        sentence_embeddings = np.load(f'{EMBEDDINGS_PATH}/{filename}.npy')
    else:
        sentence_embeddings = model.encode(pd_data['sentence'], convert_to_numpy=True)
    if not search_index:
        search_index = create_faiss_index(sentence_embeddings, filename)
    return pd_data, search_index


def store_embeddings(embeddings, filename):
    """Stores embeddings on disk.
    If these are corespondend to a data set in the data sets folder, give it the
    same name for loading.
    """
    np.save(f'{EMBEDDINGS_PATH}/{filename}.npy', embeddings)


def create_sentence_dict(id, sentence, category = ''):
    return {'id': id, 'sentence': sentence, 'category': category}


def create_faiss_index(sentence_embeddings, name):
    """creates and stores faiss index from sentence embeddings.
    The normalization is done because it was recommended in the docs when I
    first used the package (edit: and it still is, on another site in the docs).
    Args:
        sentence_embeddings: sentence embeddings to be put into the index.
        name: name of the index for storing it.

    Returns:
        The index.
    """
    index = faiss.IndexFlatIP(768)
    index.add(sentence_embeddings)
    faiss.write_index(index, f'{FAISS_PATH}/{name}.faiss')
    return index


def search_faiss_with_string(text, index, k):
    """ searches a faiss index with the model and returns the indices of the k
    most similar entries in the index as a list.
    """
    _, I = index.search(model.encode([text]), k = k +1  )
    return I.tolist()[0][1:]
