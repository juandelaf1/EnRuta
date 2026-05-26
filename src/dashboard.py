import sys
sys.path.insert(0, ".")
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.database import read_sql, get_connection

app = dash.Dash(__name__, title="EnRuta — Logística Colaborativa Rural")


def load_data():
    muns = read_sql("SELECT * FROM municipios")
    provs = read_sql("SELECT * FROM provincias")
    prods = read_sql("SELECT * FROM productores")
    trans = read_sql("SELECT * FROM transportistas")
    ofertas = read_sql("SELECT * FROM ofertas WHERE activa=1")
    demandas = read_sql("SELECT * FROM demandas WHERE activa=1")
    matches = read_sql("SELECT * FROM matches ORDER BY ahorro_estimado ASC LIMIT 50")
    return muns, provs, prods, trans, ofertas, demandas, matches


def build_map(prods, trans, ofertas, demandas, matches):
    fig = go.Figure()

    # Productores
    fig.add_trace(go.Scattermapbox(
        lat=prods["lat"], lon=prods["lon"],
        mode="markers",
        marker=dict(size=6, color="blue", opacity=0.6),
        text=prods["nombre"],
        name="Productores",
        hovertemplate="<b>%{text}</b><br>%{customdata}<extra></extra>",
        customdata=prods["tipo"],
    ))

    # Transportistas
    fig.add_trace(go.Scattermapbox(
        lat=trans["lat"], lon=trans["lon"],
        mode="markers",
        marker=dict(size=8, color="green", opacity=0.7, symbol="truck"),
        text=trans["nombre"],
        name="Transportistas",
        hovertemplate="<b>%{text}</b><extra></extra>",
    ))

    # Ofertas (rutas)
    for _, of in ofertas.head(100).iterrows():
        fig.add_trace(go.Scattermapbox(
            lat=[of["origen_lat"], of["destino_lat"]],
            lon=[of["origen_lon"], of["destino_lon"]],
            mode="lines",
            line=dict(width=1, color="green"),
            opacity=0.3,
            showlegend=False,
            hoverinfo="skip",
        ))

    # Demandas (rutas)
    for _, de in demandas.head(100).iterrows():
        fig.add_trace(go.Scattermapbox(
            lat=[de["origen_lat"], de["destino_lat"]],
            lon=[de["origen_lon"], de["destino_lon"]],
            mode="lines",
            line=dict(width=1, color="blue"),
            opacity=0.3,
            showlegend=False,
            hoverinfo="skip",
        ))

    # Top matches (flecha)
    if not matches.empty:
        match_details = read_sql("""
            SELECT m.*, o.origen_localidad, o.destino_localidad
            FROM matches m
            JOIN ofertas o ON m.oferta_id = o.id
            ORDER BY m.ahorro_estimado ASC LIMIT 10
        """)
        for _, m in match_details.iterrows():
            pass  # Podríamos dibujar la rota óptima

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=40.0, lon=-3.5),
            zoom=5.5,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=700,
    )
    return fig


def app_layout():
    muns, provs, prods, trans, ofertas, demandas, matches = load_data()

    col1 = html.Div([
        html.H3("EnRuta", style={"margin": "10px 0 5px 0"}),
        html.P("Logística colaborativa para la España rural", style={"fontSize": "14px", "color": "#666", "margin": "0 0 15px 0"}),

        html.Div([
            html.Div([
                html.Span("🗺️ ", style={"fontSize": "24px"}),
                html.Span(f" {len(prods)}", style={"fontSize": "28px", "fontWeight": "bold"}),
                html.Br(),
                html.Span("Productores", style={"fontSize": "12px", "color": "#666"}),
            ], style={"display": "inline-block", "textAlign": "center", "padding": "10px", "minWidth": "80px"}),
            html.Div([
                html.Span("🚛 ", style={"fontSize": "24px"}),
                html.Span(f" {len(trans)}", style={"fontSize": "28px", "fontWeight": "bold"}),
                html.Br(),
                html.Span("Transportistas", style={"fontSize": "12px", "color": "#666"}),
            ], style={"display": "inline-block", "textAlign": "center", "padding": "10px", "minWidth": "80px"}),
            html.Div([
                html.Span("✅ ", style={"fontSize": "24px"}),
                html.Span(f" {len(matches)}", style={"fontSize": "28px", "fontWeight": "bold"}),
                html.Br(),
                html.Span("Matches", style={"fontSize": "12px", "color": "#666"}),
            ], style={"display": "inline-block", "textAlign": "center", "padding": "10px", "minWidth": "80px"}),
        ], style={"margin": "10px 0"}),

        html.Div([
            html.P(f"Ofertas activas: {len(ofertas)}", style={"margin": "2px 0"}),
            html.P(f"Demandas activas: {len(demandas)}", style={"margin": "2px 0"}),
            html.P(f"CO₂ ahorrado: {matches['co2_evitado_kg'].sum():.0f} kg" if not matches.empty else "CO₂ ahorrado: —", style={"margin": "2px 0"}),
        ], style={"fontSize": "13px", "margin": "10px 0"}),

        html.H5("Top Matches", style={"margin": "15px 0 5px 0"}),
        dash_table.DataTable(
            columns=[
                {"name": "Ruta", "id": "ruta_short", "type": "text"},
                {"name": "Desvío", "id": "ahorro_estimado", "type": "numeric", "format": {"specifier": ".1f"}},
                {"name": "CO₂", "id": "co2_evitado_kg", "type": "numeric", "format": {"specifier": ".2f"}},
            ],
            data=[
                {
                    "ruta_short": f"{o['origen_localidad'][:12]}...",
                    "ahorro_estimado": o["ahorro_estimado"],
                    "co2_evitado_kg": o["co2_evitado_kg"],
                }
                for _, o in read_sql("""
                    SELECT m.*, o.origen_localidad, o.destino_localidad
                    FROM matches m
                    JOIN ofertas o ON m.oferta_id = o.id
                    ORDER BY m.ahorro_estimado ASC LIMIT 10
                """).iterrows()
            ],
            style_table={"overflowX": "auto"},
            style_cell={"fontSize": "12px", "padding": "4px"},
        ),
    ], style={"width": "320px", "display": "inline-block", "verticalAlign": "top", "padding": "15px", "backgroundColor": "#f8f9fa", "height": "100vh", "overflowY": "auto"})

    col2 = html.Div([
        dcc.Graph(
            id="mapa",
            figure=build_map(prods, trans, ofertas, demandas, matches),
            style={"height": "100vh"},
        ),
    ], style={"width": "calc(100% - 350px)", "display": "inline-block", "verticalAlign": "top"})

    return html.Div([col1, col2], style={"margin": "0", "padding": "0"})


app.layout = app_layout

if __name__ == "__main__":
    print("[EnRuta] Dashboard en http://127.0.0.1:8050")
    app.run(debug=True, port=8050)
