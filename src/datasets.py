""" Everything to load data and to make datasets from them. Will be growing as
input data is more specific
"""
import os
import base64
import io
import yaml
import pandas as pd
from sentence_transformers import SentenceTransformer
from sentence_transformers.models import Normalize
import numpy as np
import faiss

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


def create_dataset(data, name, description, text_column):
    """ Creates a dataset from a pandas Dataframe.

    Takes a dict('records') as input and create a dataframe from it
    The function will try to first load an index, then to load embeddings and
    then will create and store embeddings and a faiss index.
    The function will also look for a column with IDs, if no column with Ids is
    in the csv, the ids will be generated from the dataframes' index.

    Args:
        data: data records of the dataset
        name: dataset name
        description: dataset description
        text_column: dataset column from which to extract text data

    Returns:
        dataframe and search index of the dataset
    """
    pd_data = pd.DataFrame(data)
    if 'id' not in pd_data:
        pd_data.insert(0, 'id', pd_data.index)
    add_ds_metadata(pd_data, name, description, text_column)
    pd_data.to_csv(f'{DATA_PATH}/{name}.csv', index=False)
    return True


def get_dataset_labels(dataset_name):
    """returns the column names of a dataset and their number of unique items.

    Args:
        dataset_name: name of the dataset

    Returns:
        list of tuples: (column name, number of unique items in column)
    """
    df = pd.read_csv(f'{DATA_PATH}/{dataset_name}.csv')
    return [(key, df[key].nunique()) for key in df.keys() if not key.endswith('_label')]


def create_project(dataset_name, project_name, label_column=False):
    meta = load_meta_file('datasets_meta.yaml')
    text_column = meta[dataset_name]['text column']
    dataset = pd.read_csv(f'{DATA_PATH}/{dataset_name}.csv')
    if label_column:
        dataset[f'{project_name}_label'] = dataset[label_column]
    else:
        dataset[f'{project_name}_label'] = None
    dataset.to_csv(f'{DATA_PATH}/{dataset_name}.csv', index=False)
    project_dict = {
        project_name: {
            'dataset': dataset_name,
            'labels': 1,
            'progress': 0
        }
    }
    with open(f'{DATA_PATH}/projects_meta.yaml', 'a') as f:
        f.write(yaml.dump(project_dict))
    return text_column


def load_project(project_name):
    existing_projects = load_meta_file('projects_meta.yaml')
    dataset_meta = load_meta_file('datasets_meta.yaml')
    if project_name in existing_projects.keys():
        dataset_name = existing_projects[project_name]["dataset"]
        text_column = dataset_meta[dataset_name]['text column']
        return dataset_name, text_column


def fetch_data_slice(project_name, size=10, start=0):
    dataset_name, text_column = load_project(project_name)
    df = pd.read_csv(f'{DATA_PATH}/{dataset_name}.csv', keep_default_na=False)
    return df.iloc[start:start + size].to_dict('records'), text_column


def get_data_from_id(project_name, id):
    """gets data from dataset for an id

    Args:
        project_name: project name
        id: id

    Returns:
        text and label data
    """
    dataset_name, text_column = load_project(project_name)
    df = pd.read_csv(f'{DATA_PATH}/{dataset_name}.csv', keep_default_na=False)
    return df[df.id == id].to_dict('records')[0]


def store_embeddings(embeddings, filename):
    """Stores embeddings on disk.
    If these are corespondend to a data set in the data sets folder, give it the
    same name for loading.
    """
    np.save(f'{EMBEDDINGS_PATH}/{filename}.npy', embeddings)


def create_faiss_index(data, name, text_column):
    """creates and stores faiss index from sentence embeddings.
    The normalization is done because it was recommended in the docs when I
    first used the package (edit: and it still is, on another site in the docs).
    Args:
        sentence_embeddings: sentence embeddings to be put into the index.
        name: name of the index for storing it.

    Returns:
        The index.
    """
    pd_data = pd.DataFrame(data)
    # TODO: Error handling for when the index already exists or can't be created!
    if os.path.isfile(f'{FAISS_PATH}/{name}.faiss'):
        return True
    elif os.path.isfile(f'{EMBEDDINGS_PATH}/{name}.npy'):
        sentence_embeddings = np.load(f'{EMBEDDINGS_PATH}/{name}.npy')
    else:
        sentence_embeddings = model.encode(pd_data[text_column], convert_to_numpy=True)
        index = faiss.IndexFlatIP(768)
        index.add(sentence_embeddings)
        faiss.write_index(index, f'{FAISS_PATH}/{name}.faiss')
    return True


def similarity_request(current_dataset, id):
    """executes frontend request for 'get similar text'.

    Args:
        current_dataset (_type_): current_dataset info from fronten
        id (_type_): id for which new data is needed
    """
    df = pd.read_csv(f'{DATA_PATH}/{current_dataset["dataset_name"]}.csv')
    text = df.loc[id][current_dataset["text_column"]]
    return search_faiss_with_string(text, current_dataset["dataset_name"], 10)


def search_faiss_with_string(text, index_name, k):
    """ searches a faiss index with a string and returns the indices of the k
    most similar entries in the index as a list.
    """
    if os.path.isfile(f'{FAISS_PATH}/{index_name}.faiss'):
        search_index = faiss.read_index(f'{FAISS_PATH}/{index_name}.faiss')
    else:
        raise FileNotFoundError(f'no faiss index for name {index_name}')
    _, index = search_index.search(model.encode([text]), k=k + 1)
    return index.tolist()[0][1:]


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


def add_ds_metadata(dataframe, name, description, text_column):
    """writes and gathers metadata from dataset.

    Args:
        dataframe: data for which metadata is gathered
        name: name of the dataset
    """
    meta_dict = {
        name: {
            'size': dataframe.shape[0],
            'description': description,
            'text column': text_column,
        }
    }
    with open(f'{DATA_PATH}/datasets_meta.yaml', 'a') as f:
        f.write(yaml.dump(meta_dict))


def load_meta_file(name):
    """loads a metadata file

    Args:
        name: filename

    Returns:
        dictionary of the file or an empty dictionary if file not present.
        Could probably log something when logging is there.
    """
    if os.path.isfile(f'{DATA_PATH}/{name}'):
        with open(f'{DATA_PATH}/{name}', 'r') as f:
            meta = yaml.safe_load(f)
        return meta
    else:
        return {}


def check_name_exists(name, dataset='True'):
    """Check if project or dataset name exists in meta file.


    Args:
        name: name to check
        dataset: dataset flag. Defaults to 'True'. If false, check projet meta
        file instead.

    Returns:
        Boolean whether the name exists or not.
    """
    if dataset:
        meta = load_meta_file('datasets_meta.yaml')
    else:
        meta = load_meta_file('projects_meta.yaml')
    if meta:
        if name in meta:
            return True
        else:
            return False
    else:
        return False


def update_project_columns(data, project_name, dataset_name):
    new_df = pd.DataFrame(data)
    old_df = pd.read_csv(f'{DATA_PATH}/{dataset_name}.csv')
    for column in new_df:
        if column.startswith(project_name):
            old_df[column] = new_df[column]
    old_df.to_csv(f'{DATA_PATH}/{dataset_name}.csv', index=False)


def save_labels(project_name, labels):
    with open(f'{DATA_PATH}/{project_name}_labels.txt', 'w') as f:
        for label in labels:
            f.write(label + '\n')


def load_labels(project_name):
    label_file = f'{DATA_PATH}/{project_name}_labels.txt'
    if os.path.isfile(label_file):
        with open(label_file, 'r') as f:
            labels = [line.rstrip() for line in f]
    else:
        labels = []
    return labels


def save_project_changes(label_updates, project_name):
    dataset_name, _ = load_project(project_name)
    label_col = project_name + '_label'
    df = pd.read_csv(f'{DATA_PATH}/{dataset_name}.csv', index_col='id')
    for update in label_updates:
        df.at[update[0], label_col] = update[1]
    df.to_csv(f'{DATA_PATH}/{dataset_name}.csv')



