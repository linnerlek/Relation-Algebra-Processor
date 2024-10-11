import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto
import os
from RAP import get_tree_as_json, SQLite3

# Path to the folder containing .db files
DB_FOLDER = 'databases'

app = dash.Dash(__name__)

# Function to scan the databases folder and return a list of .db files
def get_db_files():
    db_files = [f for f in os.listdir(DB_FOLDER) if f.endswith('.db')]
    return [{'label': f, 'value': f} for f in db_files]


# Function to parse and validate the query
def parse_query_with_validation(query: str, db: SQLite3):
    try:
        schema = db.relations
        json_tree = get_tree_as_json(query)

        def validate_tree(node):
            if node is None:
                return True
            if node['node_type'] == 'relation':
                relation = node.get('relation_name')
                if relation and relation not in schema:
                    raise Exception(
                        f"Table '{relation}' not found in the selected database schema.")
            validate_tree(node.get('left_child'))
            validate_tree(node.get('right_child'))
            return True

        if 'error' not in json_tree:
            validate_tree(json_tree)

        return json_tree

    except Exception as e:
        return {'error': str(e)}


# Function to convert JSON tree to Cytoscape elements
def json_to_cytoscape_elements(json_tree, parent_id=None, elements=None, node_counter=[0]):
    if elements is None:
        elements = []

    if json_tree is None:
        return elements

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
# HTML of the main app layout
app.layout = html.Div([
    # Main app container
    html.Div(id="app-container", children=[
        # Left section: database name, input, submit, and tree + table container
        html.Div(className="left-section", children=[
            html.Div(className="header-dropdown-container", children=[
                html.H3(id="db-name-header"),
                dcc.Dropdown(id="db-dropdown", options=get_db_files(),
                             placeholder="Select a database"),
            ]),
            dcc.Textarea(id="query-input",
                         placeholder="Enter relational algebra query"),
            html.Button("Submit", id="submit-btn"),

            # Tree and table placeholder side by side
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

        # Right section: documentation, schema info
        html.Div(className="right-section", children=[
            html.Div(id="documentation-placeholder",
                     children="Documentation Placeholder"),
            html.Div(id="schema-info", children="Schema Info Placeholder"),
        ]),
    ]),

    # Error message area at the bottom
    html.Div(id='error-div')
])


# ------------------ Callbacks ------------------
# Update the database name in the header when a database is selected
@app.callback(
    Output('db-name-header', 'children'),
    [Input('db-dropdown', 'value')]
)
def update_db_header(selected_db):
    if selected_db:
        return f"Selected Database: {selected_db}"
    return "No Database Selected"


# Update the tree and display error messages when a query is submitted
@app.callback(
    [Output('cytoscape-tree', 'elements'),
     Output('error-div', 'children')],
    [Input('submit-btn', 'n_clicks')],
    [State('db-dropdown', 'value'), State('query-input', 'value')]
)
def update_tree(n_clicks, selected_db, query):
    if not selected_db:
        return [], "Please select a database."

    if not query:
        return [], "Please enter a query."

    if n_clicks and selected_db and query:
        formatted_query = query.replace('\n', ' ')

        try:
            db_path = os.path.join(DB_FOLDER, selected_db)
            db = SQLite3()
            db.open(db_path)

            json_tree = parse_query_with_validation(formatted_query, db)

            if 'error' in json_tree:
                raise Exception(f"Error in query: {json_tree['error']}")

            elements = json_to_cytoscape_elements(json_tree)

            db.close()

            return elements, ""

        except Exception as e:
            return [], str(e)

    return [], "Please select a database and enter a valid query."


# Display node information when a node is clicked
@app.callback(
    Output('node-table-placeholder', 'children'),
    [Input('cytoscape-tree', 'tapNodeData')]
)
def display_node_info(node_data):
    if node_data:
        # Replace with actual node data
        node_info = f"Node clicked: {node_data['label']}"
        return node_info
    return "Click node to see info."


if __name__ == '__main__':
    app.run_server(debug=True)
