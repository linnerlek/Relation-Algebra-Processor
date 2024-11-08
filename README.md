# Relational Algebra Visualizer

This application is a `Dash`-based tool for visualizing relational algebra queries. It includes an interactive graphical interface for constructing and displaying relational operations using `dash-cytoscape`.

## Prerequisites

Ensure you have Python 3.11+ and SQLite3 installed. The following libraries are required:

- `dash`: The main library for building the web application
- `dash-cytoscape`: For visualizing relational trees as graphs
- `ply`: For lexing and parsing of relational algebra queries

## Installation

1. **Clone the repository** or create a new directory and add the necessary files for the project.
2. **Navigate** to your project directory:
   ```bash
    cd your_project_directory
   ```
3. **Install** required dependencies:
   ```bash
   pip install dash dash-cytoscape ply
   ```

## Running the app

1. **Start** the application
   ```bash
   python3 app.py
   ```
2. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5020
   ```

## Using the app

### Step 1: Selecting a Database

- **Navigate to the Dropdown Menu:** On the top right side, you will find a dropdown menu labeled "Select a Database".
- **Choose a .db File:** Click the dropdown to display the available `.db` files in the `databases` folder. Select the database you wish to query.
- **Verify Database Selection:** Once selected, the database name will be displayed at the top of the left panel.

**Note:** Ensure that the database schema in the right panel matches the queries you plan to run.

### Step 2: Entering a Relational Algebra Query

- **Locate the Input Field:** Below the database dropdown, there is a text area where you can input your relational algebra query.
- **Format Your Query:** Use proper relational algebra syntax. See **"Queries"** for examples.
- **Submit the Query:** Click the **"Submit"** button below the input field to run the query.
- **Clear Previous Inputs:** Ensure you clear or modify any previous input if you plan to run a new query.

**Tip:** Click on a query in **"Queries"** to automatically insert it into the query input box.

### Step 3: Viewing and Interacting with the Visualization

- **Initial View:** Once the query is submitted, a visual representation of the relational operations will appear as a **tree** in the main display area.
- **Interact with Nodes:** Click on nodes to view operation-specific details in a table on the right.
- **Graph controls:** Use your mouse or trackpad to zoom, pan, and interact with the tree.

### Step 4: Working with the Node Table

- **View Node Details:** The node table on the right displays details for the selected node.
- **Resize the Node Table:** Drag the left edge of the node table to adjust its width for better visibility.
- **Scroll Inside the Node Table:** Use the scrollbars or your trackpad to explore the table content if it overflows.

## Operations

### List of Supported Operations

The application supports the following relational algebra operations:

- **`project:`** Specifies the columns to be displayed in the output.
- **`select:`** Filters rows based on a condition.
- **`join:`** Combines data from two or more tables based on matching columns.
- **`rename:`** Changes the column names for clarity or disambiguation.
- **`union:`** Combines the results of two queries, removing duplicates.
- **`intersect:`** Returns only the rows that are present in both queries.
- **`times:`** Computes the Cartesian product, specifically handled with relational naming for clear output.
- **`minus:`** Returns rows from the first query that are not present in the second.

## Troubleshooting

### Common Issues and Solutions

1. **Schema Mismatch:**
   - **Verify Database Schema:** Confirm that the columns and table structures in your query match the database schema.
2. **Errors on Query Submission:**
   - **Syntax Check:** Review your query for correct relational algebra syntax.
3. **Database Selection:**
   - **Ensure the Correct Database is Selected:** Double-check that the database displayed at the top of the left panel is the one you intended to use. If not, use the dropdown menu to select the correct .db file.
   - **Verify Database Contents:** Make sure the selected database contains the necessary tables and columns for your query.
4. **Dependencies:** If you encounter issues ensure all required packages are installed, and that you are running the newest version, especially of `sqlite3`, `dash-cytoscape`, and `ply`
