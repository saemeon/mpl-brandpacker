import plotly.graph_objects as go
from dash import Dash, dcc, html

from s5ndt.mpl_export import mpl_export_button

app = Dash(__name__)

fig = go.Figure(go.Scatter(x=[1, 2, 3, 4], y=[4, 2, 3, 1], mode="markers"))
fig.update_layout(title="Sample scatter")

export_btn = mpl_export_button(graph_id="my-graph")

app.layout = html.Div([
    dcc.Graph(id="my-graph", figure=fig),
    export_btn,
])

if __name__ == "__main__":
    app.run(debug=True)
