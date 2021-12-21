"""Dash application for annotation of short text usign custom labels and
giving suggestions for similar text units.
"""
import dash
import dash_bootstrap_components as dbc

app = dash.Dash(external_stylesheets=[dbc.themes.JOURNAL, dbc.icons.BOOTSTRAP],
                suppress_callback_exceptions=True
                )
