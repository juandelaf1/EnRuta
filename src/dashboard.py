import sys
sys.path.insert(0, ".")
import dash
from dash import dcc, html, dash_table, callback
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.database import read_sql, get_connection
from src.geo.engine import haversine
from src import pricing

app = dash.Dash(__name__, title="EnRuta", suppress_callback_exceptions=True)


def kpi_card(label, value, color="#333", unit=""):
    return html.Div([
        html.Div(value, style={"fontSize": "28px", "fontWeight": "bold", "color": color}),
        html.Div(label, style={"fontSize": "12px", "color": "#666"}),
        html.Div(unit, style={"fontSize": "11px", "color": "#999"}) if unit else None,
    ], style={"textAlign": "center", "padding": "10px 15px", "backgroundColor": "#f8f9fa",
              "borderRadius": "8px", "minWidth": "100px"})


def load_all():
    prods = read_sql("SELECT * FROM productores")
    trans = read_sql("SELECT * FROM transportistas")
    ofertas = read_sql("SELECT * FROM ofertas WHERE activa=1")
    demandas = read_sql("SELECT * FROM demandas WHERE activa=1")
    matches = read_sql("""
        SELECT m.*, o.origen_localidad, o.destino_localidad, o.origen_lat, o.origen_lon,
               o.destino_lat, o.destino_lon, d.kg, d.producto, d.urgente
        FROM matches m
        JOIN ofertas o ON m.oferta_id = o.id
        JOIN demandas d ON m.demanda_id = d.id
        ORDER BY m.score DESC
    """)
    provs = read_sql("SELECT * FROM provincias")
    reportes = read_sql("SELECT * FROM reportes_climaticos ORDER BY id DESC LIMIT 20")
    return prods, trans, ofertas, demandas, matches, provs, reportes


def build_mapa(prods, trans, ofertas, demandas, matches, show_prods=True, show_trans=True, show_rutas=True):
    fig = go.Figure()

    if show_prods and not prods.empty:
        fig.add_trace(go.Scattermapbox(
            lat=prods["lat"], lon=prods["lon"],
            mode="markers",
            marker=dict(size=5, color="#1a73e8", opacity=0.6),
            text=prods["nombre"],
            name="Productores",
            hovertemplate="<b>%{text}</b><br>%{customdata}<extra></extra>",
            customdata=prods["tipo"],
        ))

    if show_trans and not trans.empty:
        fig.add_trace(go.Scattermapbox(
            lat=trans["lat"], lon=trans["lon"],
            mode="markers",
            marker=dict(size=6, color="#34a853", opacity=0.7),
            text=trans["nombre"],
            name="Transportistas",
            hovertemplate="<b>%{text}</b><br>Cap: %{customdata}kg<extra></extra>",
            customdata=trans["capacidad_kg"],
        ))

    if show_rutas:
        for _, of in ofertas.head(150).iterrows():
            fig.add_trace(go.Scattermapbox(
                lat=[of["origen_lat"], of["destino_lat"]],
                lon=[of["origen_lon"], of["destino_lon"]],
                mode="lines", line=dict(width=1, color="#34a853"),
                opacity=0.25, showlegend=False, hoverinfo="skip",
            ))
        for _, de in demandas.head(150).iterrows():
            fig.add_trace(go.Scattermapbox(
                lat=[de["origen_lat"], de["destino_lat"]],
                lon=[de["origen_lon"], de["destino_lon"]],
                mode="lines", line=dict(width=1, color="#1a73e8"),
                opacity=0.25, showlegend=False, hoverinfo="skip",
            ))

    if not matches.empty:
        mejores = matches.nsmallest(20, "ahorro_estimado")
        for _, m in mejores.iterrows():
            fig.add_trace(go.Scattermapbox(
                lat=[m["origen_lat"], m["destino_lat"]],
                lon=[m["origen_lon"], m["destino_lon"]],
                mode="lines+markers",
                line=dict(width=3, color="#e8710a"),
                marker=dict(size=4, color="#e8710a"),
                name=f"Match {m['id']}" if _ == 0 else None,
                showlegend=(_ == 0),
                hovertemplate=f"<b>{m['origen_localidad']} → {m['destino_localidad']}</b><br>Score: {m['score']:.0f}<br>Desvio: {m['ahorro_estimado']:.1f}km<extra></extra>",
            ))

    fig.update_layout(
        mapbox=dict(style="open-street-map", center=dict(lat=40.0, lon=-3.5), zoom=5.3),
        margin=dict(l=0, r=0, t=0, b=0), height=600,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )
    return fig


def calc_pricing_matches(matches):
    total_ahorro_eur = 0
    total_co2 = matches["co2_evitado_kg"].sum() if not matches.empty else 0
    for _, m in matches.iterrows():
        km_ruta = haversine(m["origen_lat"], m["origen_lon"], m["destino_lat"], m["destino_lon"]) * 1.3
        p = pricing.calcular_ahorro(float(m.get("kg", 0) or 0), km_ruta, float(m.get("ahorro_estimado", 0) or 0))
        total_ahorro_eur += p["ahorro_eur"]
    return round(total_ahorro_eur, 0), round(total_co2, 0)


app.layout = html.Div([
    html.Div(id="kpi-bar"),
    html.Div(id="tab-content"),
    dcc.Interval(id="refresh", interval=30000, n_intervals=0),
])


@callback(
    [Output("kpi-bar", "children"),
     Output("tab-content", "children")],
    Input("refresh", "n_intervals"),
)
def update_dashboard(_):
    prods, trans, ofertas, demandas, matches, provs, reportes = load_all()
    ahorro, co2 = calc_pricing_matches(matches)

    kpi_bar = html.Div([
        html.Div([
            html.H2("EnRuta", style={"margin": "0", "color": "#1a73e8", "fontSize": "22px"}),
            html.Span("Logistica colaborativa rural", style={"fontSize": "12px", "color": "#666", "marginLeft": "10px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "padding": "10px 20px"}),
        html.Div([
            kpi_card("Productores", f"{len(prods):,}".replace(",", ".")),
            kpi_card("Transportistas", f"{len(trans):,}".replace(",", ".")),
            kpi_card("Ofertas", len(ofertas)),
            kpi_card("Demandas", len(demandas)),
            kpi_card("Matches", len(matches)),
            kpi_card("Ahorro total", f"{ahorro:,.0f}", color="#2e7d32", unit="EUR"),
            kpi_card("CO2 evitado", f"{co2:,.0f}".replace(",", "."), color="#1a73e8", unit="kg"),
        ], style={"display": "flex", "gap": "10px", "padding": "0 20px 10px 20px", "flexWrap": "wrap"}),
    ], style={"backgroundColor": "white", "borderBottom": "1px solid #e0e0e0"})

    tabs_content = html.Div([
        dcc.Tabs(id="tabs", value="mapa", children=[
            dcc.Tab(label="Mapa", value="mapa"),
            dcc.Tab(label="Analytics", value="analytics"),
            dcc.Tab(label="Matches", value="matches"),
            dcc.Tab(label="Rutas", value="rutas"),
        ], style={"fontSize": "14px"}),
        html.Div(id="tabs-output"),
    ], style={"padding": "10px"})

    return kpi_bar, tabs_content


@callback(
    Output("tabs-output", "children"),
    [Input("tabs", "value"),
     Input("refresh", "n_intervals")],
)
def render_tab(tab, _):
    prods, trans, ofertas, demandas, matches, provs, reportes = load_all()

    if tab == "mapa":
        fig = build_mapa(prods, trans, ofertas, demandas, matches)
        return html.Div([
            html.Div([
                html.Label("Capas:", style={"fontWeight": "bold", "marginRight": "10px"}),
                dcc.Checklist(id="capas", options=[
                    {"label": " Productores", "value": "prods"},
                    {"label": " Transportistas", "value": "trans"},
                    {"label": " Rutas", "value": "rutas"},
                ], value=["prods", "trans", "rutas"], inline=True,
                inputStyle={"marginRight": "5px"}, style={"marginBottom": "10px"}),
            ], style={"display": "flex", "alignItems": "center"}),
            dcc.Graph(id="mapa-fig", figure=fig, style={"height": "600px"}),
        ])

    if tab == "analytics":
        prods_por_prov = prods.groupby("provincia_id").size().reset_index(name="count")
        prods_por_prov = prods_por_prov.merge(provs[["id", "nombre"]], left_on="provincia_id", right_on="id", how="left")
        trans_por_prov = trans.groupby("provincia_id").size().reset_index(name="count")
        trans_por_prov = trans_por_prov.merge(provs[["id", "nombre"]], left_on="provincia_id", right_on="id", how="left")

        fig_prods = px.bar(prods_por_prov.sort_values("count", ascending=False).head(15),
                           x="nombre", y="count", title="Productores por provincia",
                           color_discrete_sequence=["#1a73e8"])
        fig_trans = px.bar(trans_por_prov.sort_values("count", ascending=False).head(15),
                           x="nombre", y="count", title="Transportistas por provincia",
                           color_discrete_sequence=["#34a853"])
        fig_tipos = px.pie(prods, names="tipo", title="Tipo de productor",
                           color_discrete_sequence=px.colors.qualifier.Set3)

        fig_scores = px.histogram(matches, x="score", nbins=20,
                                  title="Distribucion de scores de matching",
                                  color_discrete_sequence=["#e8710a"])

        return html.Div([
            html.Div([
                dcc.Graph(id="fig-prods", figure=fig_prods, style={"width": "50%", "display": "inline-block"}),
                dcc.Graph(id="fig-trans", figure=fig_trans, style={"width": "50%", "display": "inline-block"}),
            ]),
            html.Div([
                dcc.Graph(id="fig-tipos", figure=fig_tipos, style={"width": "33%", "display": "inline-block"}),
                dcc.Graph(id="fig-scores", figure=fig_scores, style={"width": "66%", "display": "inline-block"}),
            ]),
        ])

    if tab == "matches":
        match_rows = []
        for _, m in matches.iterrows():
            km_ruta = haversine(m["origen_lat"], m["origen_lon"], m["destino_lat"], m["destino_lon"]) * 1.3
            kg = float(m.get("kg", 0) or 0)
            extra = float(m.get("ahorro_estimado", 0) or 0)
            p = pricing.calcular_ahorro(kg, km_ruta, extra)
            match_rows.append({
                "id": m["id"],
                "ruta": f"{m['origen_localidad'][:12]} -> {m['destino_localidad'][:12]}",
                "producto": m.get("producto", "-")[:18],
                "score": round(m["score"], 0),
                "kg": kg,
                "trad_eur": p["coste_tradicional_eur"],
                "enruta_eur": p["coste_enruta_eur"],
                "ahorro_eur": p["ahorro_eur"],
                "ingreso_tpte": p["ingreso_transportista_eur"],
                "co2_kg": round(m["co2_evitado_kg"], 2),
                "desvio_km": round(extra, 1),
            })
        df = pd.DataFrame(match_rows)

        return html.Div([
            html.H4(f"Total: {len(df)} matches | {ahorro:,} EUR ahorro | {co2:,} kg CO2",
                    style={"margin": "10px 0"}),
            dash_table.DataTable(
                columns=[
                    {"name": "Ruta", "id": "ruta"},
                    {"name": "Producto", "id": "producto"},
                    {"name": "Score", "id": "score", "type": "numeric"},
                    {"name": "Kg", "id": "kg", "type": "numeric", "format": {"specifier": ".0f"}},
                    {"name": "Trad EUR", "id": "trad_eur", "type": "numeric", "format": {"specifier": ".2f"}},
                    {"name": "EnRuta EUR", "id": "enruta_eur", "type": "numeric", "format": {"specifier": ".2f"}},
                    {"name": "Ahorro EUR", "id": "ahorro_eur", "type": "numeric", "format": {"specifier": ".2f"}},
                    {"name": "Ingr.Tpte EUR", "id": "ingreso_tpte", "type": "numeric", "format": {"specifier": ".2f"}},
                    {"name": "CO2 kg", "id": "co2_kg", "type": "numeric", "format": {"specifier": ".2f"}},
                    {"name": "Desvio km", "id": "desvio_km", "type": "numeric", "format": {"specifier": ".1f"}},
                ],
                data=df.to_dict("records") if not df.empty else [],
                sort_action="native", filter_action="native",
                style_table={"overflowX": "auto"},
                style_cell={"fontSize": "12px", "padding": "4px", "textAlign": "right"},
                style_cell_conditional=[{"if": {"column_id": "ruta"}, "textAlign": "left"},
                                        {"if": {"column_id": "producto"}, "textAlign": "left"}],
                style_data_conditional=[
                    {"if": {"filter_query": "{ahorro_eur} > 1000"}, "backgroundColor": "#e8f5e9"},
                ],
            ),
        ])

    if tab == "rutas":
        top_rutas = matches.groupby(["origen_localidad", "destino_localidad"]).agg(
            num_matches=("id", "count"),
            avg_score=("score", "mean"),
            total_co2=("co2_evitado_kg", "sum"),
        ).reset_index().sort_values("num_matches", ascending=False).head(20)

        fig_rutas = px.bar(top_rutas, x="num_matches", y="origen_localidad",
                           orientation="h", title="Rutas mas frecuentes",
                           color="avg_score", color_continuous_scale="YlOrRd",
                           labels={"num_matches": "Matches", "origen_localidad": "Origen"})

        fig_co2 = px.bar(matches.nlargest(15, "co2_evitado_kg"),
                         x="co2_evitado_kg", y="origen_localidad",
                         orientation="h", title="Top 15 matches por CO2 evitado",
                         color="score", color_continuous_scale="Greens",
                         labels={"co2_evitado_kg": "CO2 kg", "origen_localidad": "Origen"})

        return html.Div([
            dcc.Graph(figure=fig_rutas, style={"width": "50%", "display": "inline-block"}),
            dcc.Graph(figure=fig_co2, style={"width": "50%", "display": "inline-block"}),
        ])

    return html.Div("Selecciona una pestana")


@callback(
    Output("mapa-fig", "figure"),
    [Input("capas", "value"),
     Input("refresh", "n_intervals")],
)
def update_mapa(capas, _):
    prods, trans, ofertas, demandas, matches, provs, reportes = load_all()
    return build_mapa(prods, trans, ofertas, demandas, matches,
                      show_prods="prods" in capas,
                      show_trans="trans" in capas,
                      show_rutas="rutas" in capas)


if __name__ == "__main__":
    print("[EnRuta] Dashboard en http://127.0.0.1:8050")
    app.run(debug=True, port=8050)
