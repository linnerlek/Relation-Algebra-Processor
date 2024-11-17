import sys
import sqlite3
import ply.yacc as yacc
import ply.lex as lex

reserved = {
    'project': 'PROJECT', 'rename': 'RENAME', 'union': 'UNION', 'intersect': 'INTERSECT',
    'minus': 'MINUS', 'join': 'JOIN', 'times': 'TIMES', 'select': 'SELECT', 'and': 'AND', 'like': 'LIKE',
    'sum': 'SUM', 'count': 'COUNT'
}

tokens = [
    'SEMI', 'COMPARISION', 'LPARENT', 'RPARENT', 'COMMA', 'NUMBER', 'ID', 'STRING',
    'LBRACKET', 'RBRACKET'
] + list(reserved.values())

t_SEMI = r';'
t_AND = r'[Aa][Nn][Dd]'
t_LPARENT = r'\('
t_RPARENT = r'\)'
t_PROJECT = r'[Pp][Rr][Oo][Jj][Ee][Cc][Tt]'
t_RENAME = r'[Rr][Ee][Nn][Aa][Mm][Ee]'
t_UNION = r'[Uu][Nn][Ii][Oo][Nn]'
t_MINUS = r'[Mm][Ii][Nn][Uu][Ss]'
t_INTERSECT = r'[Ii][Nn][Tt][Ee][Rr][Ss][Ee][Cc][Tt]'
t_JOIN = r'[Jj][Oo][Ii][Nn]'
t_TIMES = r'[Tt][Ii][Mm][Ee][Ss]'
t_SELECT = r'[Ss][Ee][Ll][Ee][Cc][Tt]'
t_COMMA = r','
t_COMPARISION = r'<>|<=|>=|<|>|='
t_RBRACKET = r'\]'
t_LBRACKET = r'\['

t_ignore = ' \t'


def t_STRING(t):
    r"'[^']*'"
    t.value = t.value.strip()[1:-1]
    t.type = 'STRING'
    return t


def t_NUMBER(t):
    r'[-+]?[1-9][0-9]*(\.([0-9]+)?)?'
    # t.value = float(t.value)
    t.type = 'NUMBER'
    return t


def t_ID(t):
    r'[a-zA-Z][_a-zA-Z0-9]*'
    t.type = reserved.get(t.value.lower(), 'ID')
    t.value = t.value.upper()
    return t


t_ignore_COMMENT = r'\#.*'


def t_newline(t):
    r'[\r\n]+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal Character '%s'" % t.value[0])
    t.lexer.skip(1)
    # raise Exception("Lexer Error")


lexer = lex.lex()

# data = '''project[dname](
# select[dnumber="25"](department)
# );'''
#
# lexer.input(data)
#
# while True:
#    tok = lexer.token()
#    if not tok:
#        break
#    print(tok)
# from Node import *
# from RALexer import tokens

precedence = (
    ('right', 'UNION', 'MINUS', 'INTERSECT'),
    ('right', 'TIMES', 'JOIN'),
)


def p_query(p):
    'query : expr SEMI'
    p[0] = p[1]


def p_expr(p):
    '''expr : proj_expr
            | rename_expr
            | union_expr
            | minus_expr
            | intersect_expr
            | join_expr
            | times_expr
            | paren_expr
            | select_expr '''
    p[0] = p[1]


def p_ID(p):
    'expr : ID'
    n = Node("relation", None, None)
    n.set_relation_name(p[1])
    p[0] = n


def p_proj_expr(p):
    'proj_expr : PROJECT LBRACKET attr_list RBRACKET LPARENT expr RPARENT'
    n = Node("project", p[6], None)
    n.set_columns(p[3])  # attr_list may contain aggregates like SUM or COUNT
    p[0] = n



def p_rename_expr(p):
    'rename_expr : RENAME LBRACKET attr_list RBRACKET LPARENT expr RPARENT'
    n = Node("rename", p[6], None)
    n.set_columns(p[3])
    p[0] = n


def p_attr_list(p):
    '''attr_list : ID
                 | COUNT LPARENT ID RPARENT
                 | SUM LPARENT ID RPARENT'''
    if len(p) == 2:
        p[0] = [p[1].upper()]
    else:
        p[0] = [f"{p[1].upper()}({p[3].upper()})"]


def p_attr_list_2(p):
    '''attr_list : attr_list COMMA ID
                 | attr_list COMMA COUNT LPARENT ID RPARENT
                 | attr_list COMMA SUM LPARENT ID RPARENT'''
    if len(p) == 4:
        p[0] = p[1] + [p[3].upper()]
    else:
        p[0] = p[1] + [f"{p[3].upper()}({p[5].upper()})"]


def p_union_expr(p):
    'union_expr : expr UNION expr'
    n = Node("union", p[1], p[3])
    p[0] = n


def p_minus_expr(p):
    'minus_expr : expr MINUS expr '
    n = Node("minus", p[1], p[3])
    p[0] = n


def p_intersect_expr(p):
    'intersect_expr : expr INTERSECT expr'
    n = Node("intersect", p[1], p[3])
    p[0] = n


def p_join_expr(p):
    'join_expr : expr JOIN expr'
    n = Node("join", p[1], p[3])
    p[0] = n


def p_times_expr(p):
    'times_expr : expr TIMES expr'
    n = Node("times", p[1], p[3])
    p[0] = n


def p_paren_expr(p):
    'paren_expr : LPARENT expr RPARENT'
    p[0] = p[2]


def p_select_expr(p):
    'select_expr : SELECT LBRACKET condition RBRACKET LPARENT expr RPARENT'
    n = Node("select", p[6], None)
    n.set_conditions(p[3])
    p[0] = n


def p_condition(p):
    'condition : simple_condition'
    p[0] = [p[1]]


def p_condition_2(p):
    'condition : condition AND simple_condition'
    p[0] = p[1] + [p[3]]


def p_simple_condition(p):
    '''simple_condition : operand COMPARISION operand
                        | operand LIKE operand'''
    p[0] = [p[1][0], p[1][1], p[2].upper(), p[3][0], p[3][1]]


def p_operand_1(p):
    'operand : ID'
    p[0] = ['col', p[1].upper()]


def p_operand_2(p):
    'operand : STRING'
    p[0] = ['str', p[1]]


def p_operand_3(p):
    'operand : NUMBER'
    p[0] = ['num', float(p[1])]


def p_error(p):
    raise TypeError("Syntax error: '%s'" % p.value)
    # print("Syntax error: '%s'" % p.value)


parser = yacc.yacc()


class SQLite3():

    def __init__(self):
        self.relations = []
        self.attributes = {}
        self.domains = {}
        self.conn = None

    def open(self, dbfile):
        self.conn = sqlite3.connect(dbfile)
        query = "select name from sqlite_schema where type='table'"
        c = self.conn.cursor()
        c.execute(query)
        records = c.fetchall()
        for record in records:
            self.relations.append(record[0].upper())
        for rname in self.relations:
            query = "select name,type from pragma_table_info('"+rname+"')"
            c.execute(query)
            records = c.fetchall()
            attrs = []
            doms = []
            for record in records:
                attrs.append(record[0].upper())
                if record[1].upper().startswith("INT") or record[1].upper().startswith("NUM"):
                    doms.append("INTEGER")
                elif record[1].upper().startswith("DEC"):
                    doms.append("DECIMAL")
                else:
                    doms.append("VARCHAR")
            self.attributes[rname] = attrs
            self.domains[rname] = doms

    def close(self):
        self.conn.close()

    def relationExists(self, rname):
        return rname in self.relations

    def getAttributes(self, rname):
        return self.attributes[rname]

    def getDomains(self, rname):
        return self.domains[rname]

    def displayDatabaseSchema(self):
        print("*********************************************")
        for rname in self.relations:
            print(rname+"(", end="")
            attrs = self.attributes[rname]
            doms = self.domains[rname]
            for i, (aname, atype) in enumerate(zip(attrs, doms)):
                if i == len(attrs)-1:
                    print(aname+":"+atype+")")
                else:
                    print(aname+":"+atype+",", end="")
        print("*********************************************")

    def displayQueryResults(self, query, tree):
        print("\nANSWER(", end="")
        nCols = len(tree.get_attributes())
        for i, col in enumerate(tree.get_attributes()):
            if i == (nCols-1):
                print(col+":"+tree.get_domains()[i]+")")
            else:
                print(col+":"+tree.get_domains()[i]+",", end="")
        # execute the query against sqlite3 database
        c = self.conn.cursor()
        # print("Executing query:",query)
        c.execute(query)
        records = c.fetchall()
        rowCount = len(records)
        print("Number of tuples = "+str(rowCount)+"\n")
        for record in records:
            for val in record:
                print(str(val)+":", end="")
            print()
        print()
        c.close()

    def isQueryResultEmpty(self, query):
        c = self.conn.cursor()
        records = c.execute(query)
        c.close()
        return len(records) == 0


class Node:

    def __init__(self, ntype, lc, rc):
        self.node_type = ntype		# "relation", "select", "project", "times",...
        self.left_child = lc		# left child
        self.right_child = rc		# right child
        self.columns = None			# list of column names for RENAME and PROJECT
        # list of conditions for SELECT [(lop,lot,c,rop,rot)..]
        self.conditions = None

        # the following variables are populated in RA.py
        # relation name at node (tempN interior, regular leaf)
        self.relation_name = None
        self.attributes = None		# holds schema attributes at node
        self.domains = None			# holds schema domains of attributes at node
        self.join_columns = []		# holds common column names for join

    def get_attributes(self):
        return self.attributes

    def get_columns(self):
        return self.columns

    def get_conditions(self):
        return self.conditions

    def get_right_child(self):
        return self.right_child

    def get_left_child(self):
        return self.left_child

    def get_domains(self):
        return self.domains

    def get_node_type(self):
        return self.node_type

    def get_relation_name(self):
        return self.relation_name

    def get_join_columns(self):
        return self.join_columns

    def set_attributes(self, attributes):
        self.attributes = attributes

    def set_conditions(self, conditions):
        self.conditions = conditions

    def set_right_child(self, right_node):
        self.right_child = right_node

    def set_left_child(self, left_node):
        self.left_child = left_node

    def set_columns(self, cols):
        self.columns = cols

    def set_domains(self, doms):
        self.domains = doms

    def set_node_type(self, n_type):
        self.node_type = n_type

    def set_relation_name(self, r_name):
        self.relation_name = r_name

    def set_join_columns(self, jc):
        self.join_columns = jc

    def print_tree(self, n):
        if self.node_type == "relation":
            print(" "*n, end="")
            print("NODE TYPE: " + self.node_type + "  ")
            print(" "*n, end="")
            print("Relation Name is : " + self.relation_name)
            if self.attributes != None:
                print(" "*n, end="")
                print("Schema is : " + str(self.attributes))
            if self.domains != None:
                print(" "*n, end="")
                print("Datatypes is : " + str(self.domains)+"\n")
        elif self.node_type == "project" or self.node_type == "rename":
            print(" "*n, end="")
            print("NODE TYPE: " + self.node_type + "  ")
            print(" "*n, end="")
            print("Atributes are : "+str(self.columns))
            if self.relation_name != None:
                print(" "*n, end="")
                print("Relation Name is : " + self.relation_name)
            if self.attributes != None:
                print(" "*n, end="")
                print("Schema is : " + str(self.attributes))
            if self.domains != None:
                print(" "*n, end="")
                print("Datatypes is : " + str(self.domains)+"\n")
            self.left_child.print_tree(n+4)
        elif self.node_type == "select":
            print(" "*n, end="")
            print("NODE TYPE: " + self.node_type + "  ")
            for cond in self.conditions:
                print(" "*n, end="")
                print(cond[0], end="")
                print(":", end="")
                print(cond[1], end="")
                print(":", end="")
                print(cond[2], end="")
                print(":", end="")
                print(cond[3], end="")
                print(":", end="")
                print(cond[4])
            if self.relation_name != None:
                print(" "*n, end="")
                print("Relation Name is : " + self.relation_name)
            if self.attributes != None:
                print(" "*n, end="")
                print("Schema is : " + str(self.attributes))
            if self.domains != None:
                print(" "*n, end="")
                print("Datatypes is : " + str(self.domains)+"\n")
            self.left_child.print_tree(n+4)
        elif self.node_type in ["union", "minus", "join", "intersect", "times"]:
            print(" "*n, end="")
            print("NODE TYPE: "+self.node_type+"  ")
            if self.relation_name != None:
                print(" "*n, end="")
                print("Relation Name is : " + self.relation_name)
            if self.attributes != None:
                print(" "*n, end="")
                print("Schema is : " + str(self.attributes))
            if self.domains != None:
                print(" "*n, end="")
                print("Datatypes is : " + str(self.domains)+"\n")
            self.left_child.print_tree(n+4)
            self.right_child.print_tree(n+4)
        else:
            pass


# from RAParser import parser
# from Node import *
# from SQLite3 import *

# Global variable used for setting temporary table names
count = 0


def execute_file(filename, db):
    try:
        with open(filename) as f:
            data = f.read().splitlines()
        result = " ".join(
            list(filter(lambda x: len(x) > 0 and x[0] != "#", data)))
        try:
            tree = parser.parse(result)
            set_temp_table_names(tree)
            msg = semantic_checks(tree, db)
            if msg == 'OK':
                query = generateSQL(tree, db)
                db.displayQueryResults(query, tree)
            else:
                print(msg)
        except Exception as inst:
            print(inst.args[0])
    except FileNotFoundError:
        print("FileNotFoundError: A file with name " + "'" +
              filename + "' cannot be found")


def read_input():
    result = ''
    data = input('RA: ').strip()
    while True:
        if ';' in data:
            i = data.index(';')
            result += data[0:i+1]
            break
        else:
            result += data + ' '
            data = input('> ').strip()
    return result


def set_temp_table_names(tree):
    if tree != None and tree.get_node_type() != 'relation':
        global count
        set_temp_table_names(tree.get_left_child())
        tree.set_relation_name('TEMP_' + str(count))
        count += 1
        if tree.right_child != None:
            set_temp_table_names(tree.get_right_child())

# perform semantic checks; set tree.attributes and tree.domains along the way
# return "OK" or ERROR message


def semantic_checks(tree, db):
    if tree.get_node_type() == 'relation':
        rname = tree.get_relation_name()
        if not db.relationExists(rname):
            return "Relation '" + rname + "' does not exist"
        tree.set_attributes(db.getAttributes(rname))
        tree.set_domains(db.getDomains(rname))
        return 'OK'

    if tree.get_node_type() == 'select':
        status = semantic_checks(tree.get_left_child(), db)
        if status != 'OK':
            return status
        conditions = tree.get_conditions()
        attrs = tree.get_left_child().get_attributes()
        doms = tree.get_left_child().get_domains()

        for condition in conditions:
            lot = condition[0]
            lop = condition[1]
            rot = condition[3]
            rop = condition[4]
            if lot == "col" and lop not in attrs:
                return "SEMANTIC ERROR (SELECT): Invalid Attribute: " + lop
            if rot == "col" and rop not in attrs:
                return "SEMANTIC ERROR (SELECT): Invalid Attribute: " + rop
            if lot == "col":
                ltype = "str" if doms[attrs.index(lop)] == "VARCHAR" else "num"
            else:
                ltype = lot
            if rot == "col":
                rtype = "str" if doms[attrs.index(rop)] == "VARCHAR" else "num"
            else:
                rtype = rot
            if ltype != rtype:
                return "SEMANTIC ERROR (SELECT): Invalid type comparison " + \
                       lop+":"+ltype+" vs "+rop+":"+rtype
        tree.set_attributes(attrs)
        tree.set_domains(doms)
        return 'OK'

    if tree.get_node_type() == 'times':
        status = semantic_checks(tree.get_left_child(), db)
        if status != 'OK':
            return status
        status = semantic_checks(tree.get_right_child(), db)
        if status != 'OK':
            return status

        lattrs = tree.get_left_child().get_attributes()
        rattrs = tree.get_right_child().get_attributes()
        ldoms = tree.get_left_child().get_domains()
        rdoms = tree.get_right_child().get_domains()

        t_attrs = []
        t_doms = []

        for i, attr in enumerate(lattrs):
            if attr in rattrs:
                t_attrs.append(tree.get_left_child(
                ).get_relation_name() + "." + attr)
            else:
                t_attrs.append(attr)
            t_doms.append(ldoms[i])

        for i, attr in enumerate(rattrs):
            if attr in lattrs:
                t_attrs.append(tree.get_right_child(
                ).get_relation_name() + "." + attr)
            else:
                t_attrs.append(attr)
            t_doms.append(rdoms[i])

        tree.set_attributes(t_attrs)
        tree.set_domains(t_doms)
        return 'OK'

    if tree.get_node_type() in ['union', 'intersect', 'minus']:
        status = semantic_checks(tree.get_left_child(), db)
        if status != 'OK':
            return status
        status = semantic_checks(tree.get_right_child(), db)
        if status != 'OK':
            return status

        lattrs = tree.get_left_child().get_attributes()
        rattrs = tree.get_right_child().get_attributes()
        ldoms = tree.get_left_child().get_domains()
        rdoms = tree.get_right_child().get_domains()

        if len(lattrs) != len(rattrs):
            return "SEMANTIC ERROR (UNION): Incompatible Relations - different number of columns"

        for i, dom in enumerate(ldoms):
            if dom != rdoms[i]:
                return "SEMANTIC ERROR (UNION): " + lattrs[i] + " and " + rattrs[i] + \
                       " have different data types: " + \
                    ldoms[i] + " and " + rdoms[i]

        tree.set_attributes(lattrs)
        tree.set_domains(ldoms)
        return 'OK'

    if tree.get_node_type() == 'join':
        status = semantic_checks(tree.get_left_child(), db)
        if status != 'OK':
            return status
        status = semantic_checks(tree.get_right_child(), db)
        if status != 'OK':
            return status

        lattrs = tree.get_left_child().get_attributes()
        rattrs = tree.get_right_child().get_attributes()
        ldoms = tree.get_left_child().get_domains()
        rdoms = tree.get_right_child().get_domains()

        j_attrs = []
        j_doms = []
        jcols = []

        for i, attr in enumerate(lattrs):
            j_attrs.append(attr)
            j_doms.append(ldoms[i])
            if attr in rattrs:
                jcols.append(attr)

        for i, attr in enumerate(rattrs):
            if attr not in lattrs:
                j_attrs.append(attr)
                j_doms.append(rdoms[i])

        tree.set_join_columns(jcols)
        tree.set_attributes(j_attrs)
        tree.set_domains(j_doms)
        return 'OK'

    if tree.get_node_type() == 'project':
        status = semantic_checks(tree.get_left_child(), db)
        if status != 'OK':
            return status

        p_attrs = tree.get_columns()
        attrs = tree.get_left_child().get_attributes()
        doms = tree.get_left_child().get_domains()

        for attr in p_attrs:
            if '(' in attr and ')' in attr:
                func_name, col_name = attr.split('(')
                col_name = col_name.strip(')')

                if func_name.upper() not in ['COUNT', 'SUM']:
                    return f"SEMANTIC ERROR (PROJECT): Unsupported aggregate function {func_name}"

                if col_name != '*' and col_name not in attrs:
                    return f"SEMANTIC ERROR (PROJECT): Attribute {col_name} does not exist for aggregate {func_name}({col_name})"
            else:
                if attr not in attrs:
                    return f"SEMANTIC ERROR (PROJECT): Attribute {attr} does not exist"
        tree.set_attributes(p_attrs)
        tree.set_domains(["INTEGER" for _ in p_attrs])
        return 'OK'


    if tree.get_node_type() == 'rename':
        status = semantic_checks(tree.get_left_child(), db)
        if status != 'OK':
            return status
        r_attrs = tree.get_columns()
        attrs = tree.get_left_child().get_attributes()
        doms = tree.get_left_child().get_domains()

        # Check for attribute length mismatch
        if len(r_attrs) != len(attrs):
            return "SEMANTIC ERROR (RENAME): " + str(r_attrs) + " and " + str(attrs) + " are of different sizes"

        # Check for duplicate attributes
        if len(list(set(r_attrs))) != len(r_attrs):
            return "SEMANTIC ERROR (RENAME): " + str(r_attrs) + " has duplicates!"

        # Set attributes and domains
        r_doms = doms[:]
        tree.set_attributes(r_attrs)
        tree.set_domains(doms)

        # Map original attributes to renamed ones for recognition in parent nodes
        renamed_attr_map = {attrs[i]: r_attrs[i] for i in range(len(attrs))}
        tree.set_join_columns(
            [renamed_attr_map.get(col, col)
             for col in tree.get_left_child().get_join_columns()]
        )

        return 'OK'

# given the relational algebra expression tree, generate an equivalent
# sqlite3 query.


def generateSQL(tree, db):
    if tree.get_node_type() == 'relation':
        return "select * from "+tree.get_relation_name()
    elif tree.get_node_type() == "union":
        lquery = generateSQL(tree.get_left_child(), db)
        rquery = generateSQL(tree.get_right_child(), db)
        return lquery+" union "+rquery
    elif tree.get_node_type() == "times":
        lquery = generateSQL(tree.get_left_child(), db)
        if tree.get_left_child().get_node_type() == "union":
            lquery = "("+lquery+")"
        rquery = generateSQL(tree.get_right_child(), db)
        if tree.get_right_child().get_node_type() == "union":
            rquery = "("+rquery+")"
        return "select * from " + \
               "(("+lquery+") "+tree.get_left_child().get_relation_name()+"), " + \
               "(("+rquery+") "+tree.get_right_child().get_relation_name()+")"
    elif tree.get_node_type() == "project":
        lquery = generateSQL(tree.get_left_child(), db)
        query = "select "

        for attr in tree.get_columns():
            query += f"{attr}, "

        query = query[:-2] 
        query += f" from ({lquery})"

        non_aggregate_cols = [col for col in tree.get_columns() if '(' not in col]
        if non_aggregate_cols:
            query += f" group by {', '.join(non_aggregate_cols)}"

        return query

    elif tree.get_node_type() == "rename":
        lquery = generateSQL(tree.get_left_child(), db)
        if tree.get_left_child().get_node_type() == "union":
            lquery = "("+lquery+")"
        query = "select "
        for i, attr in enumerate(tree.get_attributes()):
            query += tree.get_left_child().get_attributes()[i]+" "+attr+", "
        query = query[:-2]
        query += " from ("+lquery+") " + \
            tree.get_left_child().get_relation_name()
        return query
    elif tree.get_node_type() == "select":
        lquery = generateSQL(tree.get_left_child(), db)
        if tree.get_left_child().get_node_type() == "union":
            lquery = "("+lquery+")"
        query = "select * from (("+lquery+") " + \
            tree.get_left_child().get_relation_name()+") where "
        for condition in tree.get_conditions():
            c1 = condition[1]
            if condition[0] == 'str':
                c1 = '\''+c1+'\''
            c4 = condition[4]
            if condition[3] == 'str':
                c4 = '\''+c4+'\''
            if condition[2] == 'LIKE':
                query += f"{c1} LIKE {c4} and "
            else:
                query += str(c1)+str(condition[2])+str(c4)+" and "

        query = query[:-5] 
        return query

    elif tree.get_node_type() == "join":
        lquery = generateSQL(tree.get_left_child(), db)
        if tree.get_left_child().get_node_type() == "union":
            lquery = "("+lquery+")"
        rquery = generateSQL(tree.get_right_child(), db)
        if tree.get_right_child().get_node_type() == "union":
            rquery = "("+rquery+")"
        query = "select distinct "
        for attr in tree.get_attributes():
            if attr in tree.get_join_columns():
                query += tree.get_left_child().get_relation_name()+"."+attr+", "
            else:
                query += attr+", "
        query = query[:-2]
        query += " from " + \
                 "("+lquery+") "+tree.get_left_child().get_relation_name()+", " + \
                 "("+rquery+") "+tree.get_right_child().get_relation_name()
        if len(tree.get_join_columns()) == 0:
            return query
        query += " where "
        for col in tree.get_join_columns():
            query += tree.get_left_child().get_relation_name()+"."+col+"=" + \
                tree.get_right_child().get_relation_name()+"."+col+" and "
        query = query[:-5]
        return query
    elif tree.get_node_type() == "intersect":
        lquery = generateSQL(tree.get_left_child(), db)
        if tree.get_left_child().get_node_type() == "union":
            lquery = "("+lquery+")"
        rquery = generateSQL(tree.get_right_child(), db)
        if tree.get_right_child().get_node_type() == "union":
            rquery = "("+rquery+")"
        query = "select * from ("+lquery+") "+tree.get_left_child().get_relation_name() + \
                " where ("
        for attr in tree.get_attributes():
            query += attr+", "
        query = query[:-2] + ") in "
        query += "(select * from ("+rquery+") " + \
            tree.get_right_child().get_relation_name()
        query += ")"
        return query
    else:
        lquery = generateSQL(tree.get_left_child(), db)
        if tree.get_left_child().get_node_type() == "union":
            lquery = "("+lquery+")"
        rquery = generateSQL(tree.get_right_child(), db)
        if tree.get_right_child().get_node_type() == "union":
            rquery = "("+rquery+")"
        query = "select * from ("+lquery+") "+tree.get_left_child().get_relation_name() + \
                " where ("
        for attr in tree.get_attributes():
            query += attr+", "
        query = query[:-2] + ") not in "
        query += "(select * from ("+rquery+") " + \
            tree.get_right_child().get_relation_name()
        query += ")"
        return query

# ------------------------ Dash app Functions -------------------------------
# Convert the tree to a JSON object for visualization.


def tree_to_json(node, db, node_counter=[0]):
    if node is None:
        return None

    relation_name = node.get_relation_name() if node.get_relation_name() else "UNKNOWN"
    node_id = f"node_{node_counter[0]}"
    node_counter[0] += 1

    node_json = {
        'node_id': node_id,
        'node_type': node.get_node_type(),
        'relation_name': relation_name,
        'left_child': tree_to_json(node.get_left_child(), db, node_counter),
        'right_child': tree_to_json(node.get_right_child(), db, node_counter),
        'attributes': node.get_attributes()
    }

    # Include columns, conditions, and join columns with full qualification if needed
    if node.get_node_type() == 'project':
        node_json['columns'] = node.get_columns()
    elif node.get_node_type() == 'rename':
        node_json['new_columns'] = node.get_columns()
    elif node.get_node_type() == 'select':
        node_json['conditions'] = node.get_conditions()
    elif node.get_node_type() == 'join':
        node_json['join_columns'] = node.get_join_columns()
        # Ensure join attributes are qualified
        node_json['attributes'] = node.get_attributes()

    return node_json

# Generate a tree from the given query and perform semantic checks.


def generate_tree_from_query(query, db, node_counter=[0]):
    try:
        tree = parser.parse(query)

        # Set temporary table names as done in the backend
        set_temp_table_names(tree)

        validation_msg = semantic_checks(tree, db)
        if validation_msg != 'OK':
            return {'error': f"Semantic check failed: {validation_msg}"}

        # print("Generated Tree Structure:")
        # tree.print_tree(0)

        json_tree = tree_to_json(tree, db, node_counter)

        return json_tree
    except Exception as e:
        return {'error': str(e)}


# Recursively traverse the JSON tree to find the node with the given node_id.
def get_node_by_id(json_tree, node_id):
    if json_tree is None:
        return None

    if json_tree.get('node_id') == node_id:
        return json_tree

    left_result = get_node_by_id(json_tree.get('left_child'), node_id)
    if left_result:
        return left_result

    right_result = get_node_by_id(json_tree.get('right_child'), node_id)
    return right_result


# Reconstruct a Node object from a JSON representation.
def json_to_node(json_node):
    if json_node is None:
        return None

    node = Node(json_node['node_type'],
                json_to_node(json_node.get('left_child')),
                json_to_node(json_node.get('right_child')))

    if node.get_node_type() == 'rename':
        if 'new_columns' in json_node:
            new_cols = json_node['new_columns']
            node.set_columns(new_cols)
            node.set_relation_name(new_cols[0])

    node.set_relation_name(json_node.get('relation_name'))
    node.set_attributes(json_node.get('attributes'))

    if 'columns' in json_node:
        node.set_columns(json_node['columns'])

    if 'conditions' in json_node:
        node.set_conditions(json_node['conditions'])
    if 'join_columns' in json_node:
        node.set_join_columns(json_node.get('join_columns', []))

    # print("Node relation name:", node.get_relation_name())
    # print("Node columns:", node.get_columns())
    # print("Node join columns:", node.get_join_columns())
    return node


def get_node_info_from_db(node_id, json_tree, db):
    try:
        node_json = get_node_by_id(json_tree, node_id)

        if node_json is None:
            return {'error': 'Node not found in the tree.'}

        node = json_to_node(node_json)
        query = generateSQL(node, db)

        c = db.conn.cursor()
        c.execute(query)
        records = c.fetchall()

        columns = [desc[0] for desc in c.description]

        qualified_columns = []
        for col in columns:

            if col.startswith('TEMP_'):
                col_name = col.split('.')[-1]
                qualified_columns.append(col_name)
            else:
                qualified_columns.append(col)

        return {'columns': qualified_columns, 'rows': records}

    except Exception as e:
        return {'error': str(e)}


def fetch_schema_info(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        schema_info = {}
        for table_name in tables:
            table_name = table_name[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            schema_info[table_name] = []
            for col in columns:
                base_type = col[2].split('(')[0]
                schema_info[table_name].append({
                    'attribute': col[1],
                    'domain': base_type
                })

        conn.close()
        return schema_info

    except sqlite3.Error as e:
        return f"Error retrieving schema: {str(e)}"


# ---------------------- Main  ----------------------
def main():
    db = SQLite3()
    db.open(sys.argv[1])

    while True:
        data = read_input()
        if data == 'schema;':
            db.displayDatabaseSchema()
            continue
        if data.strip().split()[0] == "source":
            filename = data.strip().split()[1][:-1]
            execute_file(filename, db)
            continue
        if data == 'help;' or data == "h;":
            print("\nschema; 		# to see schema")
            print("source filename; 	# to run query in file")
            print("query terminated with ;	# to run query")
            print("exit; or quit; or q; 	# to exit\n")
            continue
        if data == 'exit;' or data == "quit;" or data == "q;":
            break
        try:
            tree = parser.parse(data)
        except Exception as inst:
            print(inst.args[0])
            continue
        # print("********************************")
        # tree.print_tree(0)
        # print("********************************")
        set_temp_table_names(tree)
        msg = semantic_checks(tree, db)
        # print("********************************")
        # tree.print_tree(0)
        # print("********************************")
        if msg == 'OK':
            # print('Passed semantic checks')
            query = generateSQL(tree, db)
            db.displayQueryResults(query, tree)
        else:
            print(msg)
    db.close()


if __name__ == '__main__':
    main()
