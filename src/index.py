
from app import app
from app import celery_app  # noqa: F401
from layout import layout
import callbacks  # noqa: F401
import cb_data  # noqa: F401
import cb_open_modal  # noqa: F401

app.layout = layout

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
