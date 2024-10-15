import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto
import os
from RAP import *


DB_FOLDER = 'databases'

app = dash.Dash(__name__)

def get_db_files():
    db_files = [f for f in os.listdir(DB_FOLDER) if f.endswith('.db')]
    return [{'label': f, 'value': f} for f in db_files]


def json_to_cytoscape_elements(json_tree, parent_id=None, elements=None, node_counter=[0]):
    """
    Recursively convert the JSON tree into Cytoscape elements.
    """
    if elements is None:
        elements = []

    if json_tree is None:
        return elements

    # node ID
    node_id = f"node{node_counter[0]}"
    node_label = json_tree.get('node_type', 'Unknown')

    if json_tree.get('node_type') == "relation":
        node_label = json_tree.get('relation_name', 'Unknown Relation')

    elements.append({
        'data': {'id': node_id, 'label': node_label}
    })

    if parent_id:
        elements.append({
            'data': {'source': parent_id, 'target': node_id}
        })

    node_counter[0] += 1

    json_to_cytoscape_elements(json_tree.get(
        'left_child'), node_id, elements, node_counter)
    json_to_cytoscape_elements(json_tree.get(
        'right_child'), node_id, elements, node_counter)

    return elements


# ------------------ HTML ------------------
app.layout = html.Div([
    html.Div(id="app-container", children=[
        html.Div(className="left-section", children=[
            html.Div(className="header-dropdown-container", children=[
                html.H3(id="db-name-header"),
                dcc.Dropdown(id="db-dropdown", options=get_db_files(),
                             placeholder="Select a database"),
            ]),
            dcc.Textarea(id="query-input",
                         placeholder="Enter relational algebra query"),
            html.Button("Submit", id="submit-btn"),

            html.Div(className="tree-table-container", children=[
                cyto.Cytoscape(
                    id='cytoscape-tree',
                    layout={'name': 'breadthfirst', 'directed': True},
                    elements=[]
                ),
                html.Div(id="node-table-placeholder",
                         children="Click node to see info"),
            ]),
        ]),

        html.Div(className="right-section", children=[
            html.Div(id="documentation-placeholder",
                     children="Documentation Placeholder"),
            html.Div(id="schema-info", children="Schema Info Placeholder"),
        ]),
    ]),
    # Error message display
    html.Div(id='error-div')
])


# ------------------ Callbacks ------------------
# Database name 
@app.callback(
    Output('db-name-header', 'children'),
    [Input('db-dropdown', 'value')]
)
def update_db_header(selected_db):
    if selected_db:
        return f"Selected Database: {selected_db}"
    return "No Database Selected"


@app.callback(
    [Output('cytoscape-tree', 'elements'), Output('error-div', 'children')],
    [Input('submit-btn', 'n_clicks')],
    [State('db-dropdown', 'value'), State('query-input', 'value')]
)
def update_tree(n_clicks, selected_db, query):
    if not selected_db:
        return [], "Please select a database."

    if not query:
        return [], "Please enter a query."

    if n_clicks and selected_db and query:
        try:
            db_path = os.path.join(DB_FOLDER, selected_db)
            db = SQLite3()
            db.open(db_path)

            json_tree = generate_tree_from_query(query, db)

            if 'error' in json_tree:
                raise Exception(f"Error in query: {json_tree['error']}")

            elements = json_to_cytoscape_elements(json_tree)

            db.close()

            return elements, ""

        except Exception as e:
            return [], str(e)


if __name__ == '__main__':
    app.run_server(debug=True)
