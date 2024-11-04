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


def json_to_cytoscape_elements(json_tree, parent_id=None, elements=None, node_counter=[0], x=0, y=0, x_offset=150, y_offset=100, min_separation=50, level_positions=None):
    if elements is None:
        elements = []

    if level_positions is None:
        level_positions = {}

    if json_tree is None:
        return elements

    node_id = json_tree['node_id']
    node_label = json_tree.get('node_type', 'Unknown')

    if json_tree.get('node_type') == "relation":
        node_label = json_tree.get('relation_name', 'Unknown Relation')
    elif json_tree.get('node_type') == "project":
        attributes = ', '.join(json_tree.get('columns', []))
        node_label += f"\n{attributes}"
    elif json_tree.get('node_type') == 'select':
        conditions = [
            f"{cond[1]} {cond[2]} {cond[4]}" for cond in json_tree.get('conditions', [])
        ]
        node_label += f"\n{' and '.join(conditions)}"
    elif json_tree.get('node_type') == 'rename':
        new_columns = ', '.join(json_tree.get('new_columns', []))
        node_label += f"\n{new_columns}"

    if y not in level_positions:
        level_positions[y] = []

    overlap_detected = False
    for pos in level_positions[y]:
        if abs(pos - x) < min_separation:
            overlap_detected = True
            break

    if overlap_detected and parent_id:
        y += y_offset

    level_positions[y].append(x)

    elements.append({
        'data': {'id': node_id, 'label': node_label},
        'position': {'x': x, 'y': y}
    })

    if parent_id:
        elements.append({
            'data': {'source': parent_id, 'target': node_id}
        })

    node_counter[0] += 1

    if json_tree.get('left_child') and json_tree.get('right_child'):
        json_to_cytoscape_elements(
            json_tree['left_child'], node_id, elements, node_counter, x -
            x_offset, y + y_offset, x_offset, y_offset, min_separation, level_positions
        )
        json_to_cytoscape_elements(
            json_tree['right_child'], node_id, elements, node_counter, x +
            x_offset, y + y_offset, x_offset, y_offset, min_separation, level_positions
        )
    elif json_tree.get('left_child'):
        json_to_cytoscape_elements(
            json_tree['left_child'], node_id, elements, node_counter, x, y +
            y_offset, x_offset, y_offset, min_separation, level_positions
        )
    elif json_tree.get('right_child'):
        json_to_cytoscape_elements(
            json_tree['right_child'], node_id, elements, node_counter, x, y +
            y_offset, x_offset, y_offset, min_separation, level_positions
        )

    return elements


def create_table_from_node_info(node_info):
    columns = node_info['columns']
    rows = node_info['rows']

    unique_columns = []
    seen_columns = set()

    for col in columns:
        base_col = col.split('.')[-1].lower() 
        if base_col not in seen_columns:
            unique_columns.append(col)
            seen_columns.add(base_col)

    table_header = [html.Th(col) for col in unique_columns]

    col_indices = [columns.index(col) for col in unique_columns]
    filtered_rows = [
        [row[idx] for idx in col_indices] for row in rows
    ]

    table_body = [html.Tr([html.Td(cell) for cell in row])
                  for row in filtered_rows]

    return html.Table(
        className='classic-table',
        children=[
            html.Thead(html.Tr(table_header)),
            html.Tbody(table_body)
        ]
    )


cytoscape_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'label': 'data(label)',
            'text-valign': 'bottom',
            'text-halign': 'center',
            'font-size': '18px',
            'text-wrap': 'wrap',
            'white-space': 'pre',
            'background-color': '#0071CE',
            'text-transform': 'none'
        }
    },
    {
        'selector': 'edge',
        'style': {
            'line-color': '#CCCCCC',
        }
    },
    {
        'selector': ':selected',
        'style': {
            'background-color': '#CC0000',
            'font-weight': 'bold',
        }
    }

]


# ------------------ HTML ------------------
app.title = "RA-viz"
app.layout = html.Div([
    html.Div(className="header", children=[
        html.Img(src=app.get_asset_url('RA-viz.png'), className="logo"),
        html.H1("RA-viz: Relational Algebra Visualizer"),
    ]),
    html.Div(id="app-container", children=[
        html.Div(className="left-section", children=[
            html.Div(className="input-container", children=[
                html.Div(className="header-dropdown-container", children=[
                    html.H3(id="db-name-header"),
                    dcc.Dropdown(id="db-dropdown", options=get_db_files(),
                                 placeholder="Select a database"),
                ]),
                dcc.Textarea(id="query-input",
                             placeholder="Enter relational algebra query"),
                html.Button("Submit", id="submit-btn"),
            ]),

            dcc.Store(id='tree-store'),
            dcc.Store(id='db-path-store'),
            dcc.Store(id="current-page", data=0),
            dcc.Store(id="prev-clicks", data=0),
            dcc.Store(id="next-clicks", data=0),
            dcc.Store(id="row-count", data=0),


            html.Div(className="tree-table-container", children=[
                cyto.Cytoscape(
                    id='cytoscape-tree',
                    layout={'name': 'preset'},
                    elements=[],
                    stylesheet=cytoscape_stylesheet
                ),
                html.Div(
                    className="table-and-pagination",
                    children=[
                        html.Div(id="node-table-placeholder",
                                 children="Click node to see info"),
                        html.Div(
                            [
                                html.Button(
                                    "Previous", id="prev-page-btn", n_clicks=0),
                                html.Button(
                                    "Next", id="next-page-btn", n_clicks=0)
                            ],
                            className="pagination-buttons"
                        ),
                    ],
                ),
            ]),
        ]),

        html.Div(className="right-section", children=[
            html.Div(id="documentation-placeholder",
                     children="Documentation Placeholder"),

            html.Details(id="schema-container", open=True, children=[
                html.Summary("Schema Information"),
                html.Div(id="schema-info", children="Schema Info Placeholder")
            ])
        ])
    ]),
    html.Div(id='error-div')
])

# ------------------ Callbacks ------------------

@app.callback(
    Output('db-name-header', 'children'),
    Output('query-input', 'value'),
    [Input('db-dropdown', 'value')]
)
def update_db_header(selected_db):
    if selected_db:
        header = f"Selected Database: {selected_db}"
    else:
        header = "No Database Selected"

    query_input = ""
    
    return header, query_input


@app.callback(
    Output('schema-info', 'children'),
    [Input('db-dropdown', 'value')]
)
def display_schema_info(selected_db):
    if not selected_db:
        return "Select a database from the dropdown to view schema information."

    try:
        db_path = os.path.join(DB_FOLDER, selected_db)
        schema_info = fetch_schema_info(db_path)

        if isinstance(schema_info, str):
            return schema_info

        schema_elements = []
        for rname, details in schema_info.items():
            schema_elements.append(
                html.Details([
                    html.Summary(rname),
                    html.Table(className='classic-table', children=[
                        html.Thead(
                            html.Tr([html.Th("Attribute"), html.Th("Data type")])),
                        html.Tbody([html.Tr([html.Td(detail['attribute']), html.Td(
                            detail['domain'])]) for detail in details])
                    ])
                ])
            )

        return schema_elements

    except Exception as e:
        return f"Error: {str(e)}"


@app.callback(
    [Output('cytoscape-tree', 'elements'),
     Output('tree-store', 'data'),
     Output('db-path-store', 'data'),
     Output('error-div', 'children'),
     Output('error-div', 'style')],
    [Input('submit-btn', 'n_clicks'),
     Input('db-dropdown', 'value')],
    [State('query-input', 'value')]
)
def update_tree(n_clicks, selected_db, query):
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('db-dropdown'):
        return [], {}, "", "", {'display': 'none'}

    if n_clicks is None: 
        return [], {}, "", "", {'display': 'none'}

    if not selected_db:
        return [], {}, "", "Please select a database.", {'display': 'block'}

    if not query:
        return [], {}, "", "Please enter a query.", {'display': 'block'}

    if n_clicks and selected_db and query:
        try:
            db_path = os.path.join(DB_FOLDER, selected_db)
            db = SQLite3()
            db.open(db_path)

            json_tree = generate_tree_from_query(query, db, node_counter=[0])

            if 'error' in json_tree:
                raise Exception(
                    f"Error in query: {json_tree['error']}. Is the right database selected?")

            elements = json_to_cytoscape_elements(json_tree)

            db.close()

            return elements, json_tree, db_path, "", {'display': 'none'}

        except Exception as e:
            # Show the error message
            return [], {}, str(e), str(e), {'display': 'block'}


@app.callback(
    [Output('node-table-placeholder', 'children'),
     Output('row-count', 'data')],
    [Input('cytoscape-tree', 'tapNodeData'),
     Input('db-dropdown', 'value'),
     Input('current-page', 'data')],
    [State('tree-store', 'data'), State('db-path-store', 'data')]
)
def display_node_info(node_data, selected_db, current_page, json_tree, db_path):
    ctx = dash.callback_context

    if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('db-dropdown'):
        return "Click node to see info.", 0  


    if node_data:
        try:
            node_id = node_data['id']
            db = SQLite3()
            db.open(db_path)

            node_info = get_node_info_from_db(node_id, json_tree, db)
            db.close()

            if 'error' in node_info:
                return html.Div([html.P(f"Error: {node_info['error']}")]), 0

            rows_per_page = 8
            total_rows = len(node_info['rows'])
            max_page = (total_rows - 1) // rows_per_page

            current_page = min(current_page, max_page)
            start_index = current_page * rows_per_page
            end_index = start_index + rows_per_page
            visible_rows = node_info['rows'][start_index:end_index]

            columns = node_info['columns']
            table_header = [html.Th(col) for col in columns]
            table_body = [html.Tr([html.Td(cell) for cell in row])
                          for row in visible_rows]

            result_table = html.Table(
                className='classic-table',
                children=[
                    html.Thead(html.Tr(table_header)),
                    html.Tbody(table_body)
                ]
            )

            return result_table, total_rows

        except Exception as e:
            return f"Error occurred: {str(e)}", 0

    return "Click node to see info.", 0 


@app.callback(
    [Output("current-page", "data"),
     Output("prev-clicks", "data"),
     Output("next-clicks", "data")],
    [Input("prev-page-btn", "n_clicks"),
     Input("next-page-btn", "n_clicks")],
    [State("current-page", "data"),
     State("prev-clicks", "data"),
     State("next-clicks", "data")]
)
def update_page(prev_clicks, next_clicks, current_page, last_prev_clicks, last_next_clicks):
    prev_clicks_delta = prev_clicks - last_prev_clicks
    next_clicks_delta = next_clicks - last_next_clicks

    new_page = current_page + next_clicks_delta - prev_clicks_delta

    new_page = max(new_page, 0)

    return new_page, prev_clicks, next_clicks


app.clientside_callback(
    """
    function(rowCount) {
        if (rowCount > 8) {
            return [{'display': 'inline-block'}, {'display': 'inline-block'}];
        } else {
            return [{'display': 'none'}, {'display': 'none'}];
        }
    }
    """,
    [Output("prev-page-btn", "style"), Output("next-page-btn", "style")],
    [Input("row-count", "data")]
)


if __name__ == '__main__':
    app.run_server(debug=True)
