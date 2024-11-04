# Relational Algebra Visualizer

This application is a `Dash`-based tool for visualizing relational algebra queries. It includes an interactive graphical interface for constructing and displaying relational operations using `dash-cytoscape`.

## Getting Started
### Step 1: Selecting a Database
- **Navigate to the Dropdown Menu:** On the top right side, you will find a dropdown menu labeled "Select a Database".
-  **Choose a .db File:** Click the dropdown to display the available `.db` files in the `databases` folder. Select the database you wish to query.
- **Verify Database Selection:** Once selected, the database name will be displayed at the top of the left panel.

**Note:** Ensure that the database schema in the right panel matches the queries you plan to run.

### Step 2: Entering a Relational Algebra Query
- **Locate the Input Field:** Below the database dropdown, there is a text area where you can input your relational algebra query.
- **Format Your Query:** Use proper relational algebra syntax. For example:
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
- **Submit the Query:** Click the **"Submit"** button below the input field to run the query.
- **Clear Previous Inputs:** Ensure you clear or modify any previous input if you plan to run a new query.

### Step 3: Viewing and Interacting with the Visualization
- **Initial View:** Once the query is submitted, a visual representation of the relational operations will appear as a **tree** in the main display area.
- **Node Interaction:**
    - **Click Nodes:** Click on any node to view details about the specific operation it represents.
    - **Details Display:** A table with operation-specific data will appear on the right side, showing relevant columns and rows.
- **Graph Navigation:**
    - **Zoom and Pan:** Use your mouse or trackpad to zoom in/out and drag to pan across the graph.
    - **Select and Highlight:** Selected nodes are highlighted for better visibility.

## Example Query Syntax and Operations
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

### Comprehensive Query Example
Here is an example query that utilizes multiple operations:
```
project[lname, fname](
  ((rename[ssn](project[mgrssn](department))
    join
    rename[ssn](project[essn](dependent))
   )
  join
  employee
  )
);

```
- **Explanation:**
    - `project[mgrssn](department)`: Projects the `mgrssn` column from the `department` table.
    - `rename[ssn](project[mgrssn](department))`: Renames `mgrssn` to `ssn` for consistency.
    - `project[essn](dependent)`: Projects the `essn` column from the `dependent` table.
    - `rename[ssn](project[essn](dependent))`: Renames `essn` to `ssn` for matching purposes.
    - `join`: Joins the renamed projections to match `ssn` values.
    - Final `join` with `employee`: Combines the result with the `employee` table to match `ssn` with employee records.
    - `project[lname, fname]`: Final projection to display only the `lname` and `fname` columns of the matching managers

## Troubleshooting
### Common Issues and Solutions
1. **Schema Mismatch:**
    - **Verify Database Schema:** Confirm that the columns and table structures in your query match the database schema.
2. **Errors on Query Submission:**
    - **Syntax Check:** Review your query for correct relational algebra syntax.
3. **Database Selection:**
    - **Ensure the Correct Database is Selected:** Double-check that the database displayed at the top of the left panel is the one you intended to use. If not, use the dropdown menu to select the correct .db file.
    - **Verify Database Contents:** Make sure the selected database contains the necessary tables and columns for your query.



