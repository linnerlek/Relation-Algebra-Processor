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
    http://127.0.0.1:8050
    ```
## Using the app
1. **Select a Database:** Use the dropdown menu to choose a .db file from the databases folder.
2. **Enter Relational Algebra Query:** Type a query in the relational algebra format and click "Submit."
3. **Interact with Visualization:** Nodes are clickable, allowing you to view results for specific relational operations.

#### Example query syntax
```
project[pnumber,dnum,lname,address,bdate](
  (
   (select[plocation='Stafford'](projects) 
    join 
    rename[dname,dnum,ssn,mgrstartdate](department)
   )
   join employee
  )
);
```
## Troubleshooting
1. **Database Files:** Ensure .db files are in the databases folder, and the schema matches your relational algebra queries.
2. **Dependencies:** If you encounter issues, ensure all required packages are installed, especially `dash-cytoscape` and `ply`.
