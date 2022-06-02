"""Dash application for annotation of short text usign custom labels and
giving suggestions for similar text units.
"""
import dash
import dash_bootstrap_components as dbc
from dash.long_callback import CeleryLongCallbackManager
from celery import Celery

celery_app = Celery(
    __name__, broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")

long_callback_manager = CeleryLongCallbackManager(celery_app)

app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL, dbc.icons.BOOTSTRAP],
                suppress_callback_exceptions=True,
                long_callback_manager=long_callback_manager,
                )
