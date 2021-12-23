
from app import app
from layout import layout
import callbacks
import cb_datatables
import cb_open_modal

app.layout = layout

if __name__ == '__main__':
    app.run_server(debug=True)
