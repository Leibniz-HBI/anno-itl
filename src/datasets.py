""" Everything to load data and to make datasets from them. Will be growing as
input data is more specific
"""
import os
import base64
import io
import yaml
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from sentence_transformers.models import Normalize
import numpy as np
import faiss
from dash import html


embedding_model = SentenceTransformer('paraphrase-mpnet-base-v2')

model = SentenceTransformer(modules=[embedding_model, Normalize()])

FAISS_PATH = './faiss_indexes'
DATA_PATH = './datasets'
EMBEDDINGS_PATH = './embeddings'


def dataset_from_csv(filename):
    """Creates datasets from csv file.

    Args:
        filename: name of file to load

    Returns:
        dataframe and search index of the dataset
    """
    pd_data = pd.read_csv(f'{DATA_PATH}/{filename}.csv')
    return create_dataset(pd_data, filename)


def create_dataset(data, name, description):
    """ Creates a dataset from a pandas Dataframe.

    Takes a dict('records') as input and create a dataframe from it
    The dataframe needs to have a column named text unit.
    The function will try to first load an index, then to load embeddings and
    then will create and store embeddings and a faiss index.
    The function will also look for a column with IDs, if no column with Ids is
    in the csv, the ids will be generated from the dataframes' index.

    Args:
        pd_data: pandas dataframe, needs column text unit

    Returns:
        dataframe and search index of the dataset
    """

    # add blank category column to data without category
    pd_data = pd.DataFrame(data)
    if 'category' not in pd_data:
        pd_data['category'] = None
    if 'id' not in pd_data:
        pd_data.insert(0, 'id', pd_data.index)
    add_metadata(pd_data, name, description)
    search_index = None
    if os.path.isfile(f'{FAISS_PATH}/{name}.faiss'):
        search_index = faiss.read_index(f'{FAISS_PATH}/{name}.faiss')
    elif os.path.isfile(f'{EMBEDDINGS_PATH}/{name}.npy'):
        sentence_embeddings = np.load(f'{EMBEDDINGS_PATH}/{name}.npy')
    else:
        sentence_embeddings = model.encode(pd_data['text unit'], convert_to_numpy=True)
    if not search_index:
        search_index = create_faiss_index(sentence_embeddings, name)
    pd_data.to_csv(f'{DATA_PATH}/{name}.csv')
    return True


def store_embeddings(embeddings, filename):
    """Stores embeddings on disk.
    If these are corespondend to a data set in the data sets folder, give it the
    same name for loading.
    """
    np.save(f'{EMBEDDINGS_PATH}/{filename}.npy', embeddings)


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


def search_faiss_with_string(text, index_name, k):
    """ searches a faiss index with the model and returns the indices of the k
    most similar entries in the index as a list.
    """
    if os.path.isfile(f'{FAISS_PATH}/{index_name}.faiss'):
        search_index = faiss.read_index(f'{FAISS_PATH}/{index_name}.faiss')
    else:
        raise FileNotFoundError(f'no faiss index for name {index_name}')
    _, I = search_index.search(model.encode([text]), k = k +1  )
    return I.tolist()[0][1:]


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith('.csv'):
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif filename.endswith('.tsv'):
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), sep='\t')
        elif filename.endswith('.xls'):
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return None
    return df


def add_metadata(dataframe, name, description):
    """writes and gathers metadata from dataset.

    Args:
        dataframe: data for which metadata is gathered
        name: name of the dataset
    """
    meta_dict = {
        name: {
            'size': dataframe.shape[0],
            'description': description
        }
    }
    with open(f'{DATA_PATH}/datasets_meta.yaml', 'a') as f:
        f.write(yaml.dump(meta_dict))


def load_meta_file():
    if os.path.isfile(f'{DATA_PATH}/datasets_meta.yaml'):
        with open(f'{DATA_PATH}/datasets_meta.yaml', 'r') as f:
            meta = yaml.safe_load(f)
        return meta
    else:
         return None


def check_dataset_exists(name):
    meta = load_meta_file()
    if meta:
        if name in meta:
            return True
        else:
            return False
    else:
        return False
