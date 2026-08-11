import os
import glob
import pandas as pd

BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Dataset')

candidate = glob.glob(os.path.join(BASE_DATA_DIR, 'E-Commerce Dataset*'))
if candidate:
    DATA_SOURCE_DIR = candidate[0]
else:
    DATA_SOURCE_DIR = os.path.join(BASE_DATA_DIR, 'E-Commerce Dataset')

DATA_FILES = {
    'customers': 'customers_dataset.csv',
    'geolocation': 'geolocation_dataset.csv',
    'order_items': 'order_items_dataset.csv',
    'order_payments': 'order_payments_dataset.csv',
    'order_reviews': 'order_reviews_dataset.csv',
    'orders': 'orders_dataset.csv',
    'product_categories': 'product_category_name_translation.csv',
    'products': 'products_dataset.csv',
    'sellers': 'sellers_dataset.csv',
}


def load_table(key, nrows=None):
    path = os.path.join(DATA_SOURCE_DIR, DATA_FILES[key])
    return pd.read_csv(path, nrows=nrows)


def load_all_metadata():
    metadata = {}
    for key, filename in DATA_FILES.items():
        path = os.path.join(DATA_SOURCE_DIR, filename)
        try:
            df = pd.read_csv(path, nrows=5)
            metadata[key] = {
                'file': filename,
                'rows': None,
                'columns': df.columns.tolist(),
                'sample': df.head(3).to_dict(orient='records'),
                'dtypes': df.dtypes.apply(lambda x: x.name).to_dict(),
            }
        except Exception as exc:
            metadata[key] = {'error': str(exc), 'file': filename}
    return metadata
