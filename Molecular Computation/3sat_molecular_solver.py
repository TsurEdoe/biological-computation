import random

# Consts for moleclar computetian

NUCLEOBASES = ['A', 'G', 'C', 'T']
CHANCE_FOR_PCR = 0.9
CHANCE_FOR_TWO_MOLECULES_TO_CONNECT = 0.8

# Consts for 3-SAT algorithm

NUMBER_OF_VARIABLES = 3
VERTEX_DNA_STRAND_LENGTH = 20
FULL_PATH_LEGTH = (2 * NUMBER_OF_VARIABLES + 1) * VERTEX_DNA_STRAND_LENGTH
NUMBER_OF_CLAUSES = 3

class DNADoubleHelix:
    def __init__(self, leading_strand='', lagging_strand='', primer='', start_index=0):
        if not primer:
            lagging_strand = invert_dna(leading_strand)
            self.dna_data = list(zip(leading_strand, lagging_strand))
        elif not lagging_strand:
            template_lagging_strand = '-' * start_index + primer + '-' * (len(leading_strand) - len(primer) - start_index)
            self.dna_data = list(zip(leading_strand, template_lagging_strand))
        elif not leading_strand:
            template_leading_strand = '-' * start_index + primer + '-' * (len(lagging_strand) - len(primer) - start_index)
            self.dna_data = list(zip(template_leading_strand, lagging_strand))
        else:
            raise "Bad DNA helix input. 2 of these should be inputted: leading strand, lagging strand, primer."

    def __len__(self):
        return len(self.dna_data)
    
    def __str__(self):
        to_print = ''
        for nucleobases in self.dna_data:
            to_print += nucleobases[0]
        to_print += '\n'
        for nucleobases in self.dna_data:
            to_print += '|' if nucleobases[1] != '-' else ' '
        to_print += '\n'
        for nucleobases in self.dna_data:
            to_print += nucleobases[1]
        to_print += '\n'
        return to_print

    def seperate_strands(self):
        first_strands_data, second_strands_data = list(zip(*self.dna_data))
        strands_data = list(filter(None, ''.join(first_strands_data).split('-') + ''.join(second_strands_data).split('-')))
        strands = [DNAStrand(x) for x in strands_data]
        return strands

    def run_ligase_enzyme(self):
        for i in range(len(self.dna_data)):
            if self.dna_data[i][0] == '-':
                self.dna_data[i] = (invert_nucleobase(self.dna_data[i][1]), self.dna_data[i][1])
            elif self.dna_data[i][1] == '-':
                self.dna_data[i] = (self.dna_data[i][0], invert_nucleobase(self.dna_data[i][0]))

class DNAStrand(str):
    def __init__(self, strand_data = ''):
        self.strand_data = list(strand_data)
    
    @staticmethod
    def random_strand(strand_length = 0):
        return DNAStrand(''.join([random.choice(NUCLEOBASES) for _ in range(strand_length)]))

# Molecular computations laboratoty actions

def nucleobases_match(first_nucleobase, second_nucleobase):
    return  (first_nucleobase == 'A' and second_nucleobase == 'T') or \
            (first_nucleobase == 'G' and second_nucleobase == 'C') or \
            (first_nucleobase == 'C' and second_nucleobase == 'G') or \
            (first_nucleobase == 'T' and second_nucleobase == 'A')

def invert_nucleobase(nucleobase):
    if nucleobase == 'A':
        return 'T'
    elif nucleobase == 'G':
        return 'C'
    elif nucleobase == 'C':
        return 'G'
    elif nucleobase == 'T':
        return 'A'

def invert_dna(dna_data):
    inverted = ''
    for nucleobase in dna_data:
        inverted += invert_nucleobase(nucleobase)
    return DNAStrand(inverted)

def can_strands_create_double_helix(first_strand, second_strand, start_index=0, print_match=False):
    smaller_strand, larger_strand = sorted([first_strand, second_strand], key=len)
    for j in range(len(smaller_strand)):
        if not nucleobases_match(larger_strand[start_index + j], smaller_strand[j]):
            return False
    if print_match:
        print(smaller_strand + " matches " + larger_strand[:start_index] + "-" + 
        larger_strand[start_index:start_index + len(smaller_strand)] + "-" + 
        larger_strand[start_index + len(smaller_strand):])
    return True

def run_through_gel(dna_helixes):
    return sorted(dna_helixes, key=lambda x:len(x.dna_data))

def filter_by_size(dna_helixes, wanted_size):
    return [wanted_helix for wanted_helix in run_through_gel(dna_helixes) if len(wanted_helix) == wanted_size]

def pcr(dna_starter, primer, num_of_iterations):
    dna_length = dna_starter.__sizeof__()
    dna_collection = [dna_starter]
    inverted_primer = invert_dna(primer)
    for iteration in range(1, num_of_iterations + 1):
        print("Running PCR iteration " + str(iteration))
        temp_dna_collection = []
        for dna in dna_collection:
            leading_strand, lagging_strand = dna.seperate_strands()
            attach_indexes = list(range(dna_length - len(primer) + 1))
            random.shuffle(attach_indexes)

            for i in attach_indexes:
                if leading_strand and can_strands_create_double_helix(leading_strand, primer, i):
                    if random.random() < CHANCE_FOR_PCR:
                        new_dna_helix = DNADoubleHelix(leading_strand=leading_strand, primer=primer, start_index=i)
                        new_dna_helix.run_ligase_enzyme()
                        temp_dna_collection.append(new_dna_helix)
                    leading_strand = None
                if lagging_strand and can_strands_create_double_helix(lagging_strand, inverted_primer, i):
                    if random.random() < CHANCE_FOR_PCR:
                        new_dna_helix = DNADoubleHelix(lagging_strand=lagging_strand, primer=inverted_primer, start_index=i)
                        new_dna_helix.run_ligase_enzyme()
                        temp_dna_collection.append(new_dna_helix)
                    lagging_strand = None
        dna_collection = temp_dna_collection
        print("Finished PCR iteration " + str(iteration) + ". DNA pool size: " + str(len(dna_collection)))
    return dna_collection

def select_molecules_by_sequence(dna_helixes, sequence_to_match):
    filtered_molecules = []
    for dna_molecule in dna_helixes:
        dna_strands = dna_molecule.seperate_strands()
        # The lagging strand (dna_strands[1]) is the strand containing the vertices data, therefore holds the sequence should be searched there
        if sequence_to_match in dna_strands[1]:
            filtered_molecules.append(dna_molecule)
    return filtered_molecules

# SAT problem helper functions

def create_SAT_graph(number_of_variables = NUMBER_OF_VARIABLES, vertice_dna_strand_legth = VERTEX_DNA_STRAND_LENGTH):
    variable_vertices = []
    connection_vertices = [DNAStrand.random_strand(vertice_dna_strand_legth)]
    edges = []
    for _ in range(number_of_variables):
        current_variable_vertex = DNAStrand.random_strand(vertice_dna_strand_legth)
        while current_variable_vertex in variable_vertices or current_variable_vertex in connection_vertices:
            current_variable_vertex = DNAStrand.random_strand(vertice_dna_strand_legth)
        variable_vertices.append(current_variable_vertex)
        variable_vertices.append(invert_dna(current_variable_vertex))

        current_connection_vertex = DNAStrand.random_strand(vertice_dna_strand_legth)
        while current_connection_vertex in variable_vertices or current_connection_vertex in connection_vertices:
            current_connection_vertex = DNAStrand.random_strand(vertice_dna_strand_legth)
        connection_vertices.append(current_connection_vertex)

    # The starting edges of the paths in the graph. Like Adelman's hamiltonian path solution, 
    # the representation will be the whole first vertex and the first half of the second vertex
    edges.append(invert_dna(connection_vertices[0] + variable_vertices[0][:int(VERTEX_DNA_STRAND_LENGTH/2)]))
    edges.append(invert_dna(connection_vertices[0] + variable_vertices[1][:int(VERTEX_DNA_STRAND_LENGTH/2)]))

    for i in range(1, number_of_variables):
        # Forward edges from x and x~ to a1
        edges.append(invert_dna(variable_vertices[2*(i-1)][int(VERTEX_DNA_STRAND_LENGTH/2):] + connection_vertices[i][:int(VERTEX_DNA_STRAND_LENGTH/2)]))
        edges.append(invert_dna(variable_vertices[2*(i-1)+1][int(VERTEX_DNA_STRAND_LENGTH/2):] + connection_vertices[i][:int(VERTEX_DNA_STRAND_LENGTH/2)]))

        # Forward edges from a0 to x and ~x
        edges.append(invert_dna(connection_vertices[i][int(VERTEX_DNA_STRAND_LENGTH/2):] + variable_vertices[2*i][:int(VERTEX_DNA_STRAND_LENGTH/2)]))
        edges.append(invert_dna(connection_vertices[i][int(VERTEX_DNA_STRAND_LENGTH/2):] + variable_vertices[2*i+1][:int(VERTEX_DNA_STRAND_LENGTH/2)]))
        

    # The ending edges of the paths in the graph. Like Adelman's hamiltonian path solution, 
    # the representation will be the second half of the  first vertex and the whole second vertex
    edges.append(invert_dna(variable_vertices[-1][int(VERTEX_DNA_STRAND_LENGTH/2):] + connection_vertices[-1]))
    edges.append(invert_dna(variable_vertices[-2][int(VERTEX_DNA_STRAND_LENGTH/2):] + connection_vertices[-1]))

    return {
        "variables":    variable_vertices,
        "connections":  connection_vertices,
        "edges" :       edges
        }

def find_all_paths_in_graph(graph):
    vertices = graph["connections"] + graph["variables"]
    starting_edges = graph["edges"][:2]
    ending_edges = graph["edges"][-2:]
    middle_edges = graph["edges"][2:-2]
    number_of_paths = 2**len(graph["variables"])
    
    # Generating enough dna strands to create all of the possible paths though the given graph
    edges_dna_strands = number_of_paths * middle_edges
    starting_edges_dna_strands = number_of_paths * starting_edges
    ending_edges_dna_strands = number_of_paths * ending_edges
    vertices_dna_strands = number_of_paths * vertices

    paths_edge_strands = set()
    while edges_dna_strands and starting_edges_dna_strands and ending_edges_dna_strands:
        # Randomly selecting first edge
        path_strand = random.choice(starting_edges_dna_strands)
        starting_edges_dna_strands.remove(path_strand)
        for _ in range(len(vertices)):
            # Selecting the next vertex randomly only from the ones that can complete the current edge
            next_possible_vertex = [vertex for vertex in vertices if vertex.startswith(invert_dna(path_strand[-int(VERTEX_DNA_STRAND_LENGTH/2):]))]
            next_vertex = random.choice(next_possible_vertex)
            # Selecting the next edge randomly only from the ones that can complete the next vertex selected
            possible_next_edges = [next_edge for next_edge in edges_dna_strands if next_edge.startswith(invert_dna(next_vertex[-int(VERTEX_DNA_STRAND_LENGTH/2):]))]
            if not possible_next_edges:
                # We didn't reach the ending edge on this path, scrubbing it 
                break
            new_edge = random.choice(possible_next_edges)
            path_strand += new_edge
            edges_dna_strands.remove(new_edge)

        path_strand += ending_edges[0] if ending_edges[0].startswith(path_strand[:int(VERTEX_DNA_STRAND_LENGTH/2)]) else ending_edges[1]
        paths_edge_strands.add(path_strand)
        
    paths = []
    for path_edge_strands in paths_edge_strands:
        path_leading_strand = DNAStrand(path_edge_strands)
        for vertex in vertices_dna_strands:
            if can_strands_create_double_helix(path_leading_strand, vertex) and random.random() < CHANCE_FOR_TWO_MOLECULES_TO_CONNECT:
                new_path = DNADoubleHelix(path_leading_strand, vertex)
                new_path.run_ligase_enzyme()
                paths.append(new_path)
                vertices_dna_strands.remove(vertex)
                break
    return paths

def create_satisfiable_3cnf_boolean_formula(variables, number_of_clauses=NUMBER_OF_CLAUSES):
    '''
        This formula should always return True
    '''
    return [[variables[0], variables[1], variables[0]]] + [random.sample(variables, 3) for _ in range(number_of_clauses-1)]

def create_non_satisfiable_3cnf_boolean_formula(variables, number_of_clauses=NUMBER_OF_CLAUSES):
    '''
        This formula should always return False
    '''
    return [[variables[0], variables[0], variables[0]], [variables[1], variables[1], variables[1]]] \
            + [random.sample(variables, 3) for _ in range(number_of_clauses-2)]

def create_3cnf_boolean_formula(variables, number_of_clauses=NUMBER_OF_CLAUSES):
    ''' 
        Returns a list of lists. Each inner list is clause and its variables are connected by OR.
        All of the lists are connected via AND. Thus creating a 3-cnf boolean formula
    ''' 
    return [random.sample(variables, 3) for _ in range(number_of_clauses)]

def filter_assignments_that_satisfy_clause(assigments, clause):
    '''
        Returns the assignments that satisfy at least one of the variables in the given clause
    '''
    assigments_that_satisfy_clause = set()
    for variable in clause:
        assigments_that_satisfy_clause.update(select_molecules_by_sequence(assigments, variable))
    return [*assigments_that_satisfy_clause]

def three_SAT(formula, all_possible_assigments):
    '''
        Each 3-cnf formula is composed as follows: F = ( C1 ^ C2 ^ C3 ..... ^ Cn).
        Therefore in order to filter out the solutions that satiafy the formula we must go through all of the clauses in the formula
        and for each one leave in the possible assignments pool only the ones that satisfy said clause, hence in the end we will
        be left only with the assigments that satisfy all of the clauses and the formula itself. 
    '''
    for clause in formula:
      all_possible_assigments = filter_assignments_that_satisfy_clause(all_possible_assigments, clause)
    
    # The problem is solved if after all filters some dna material is left in the test tube
    return len(all_possible_assigments) > 0

def printable_formula(formula):
    ret = '('
    for clause in formula:
        ret += '(' + ' V '.join(clause) + ') ^ '
    return ret[:-3] + ')'

def printable_assigment(assignment):
    vertices_data = assignment.seperate_strands()[1]
    vertices = [vertices_data[i : i + VERTEX_DNA_STRAND_LENGTH] for i in range(0, len(vertices_data), VERTEX_DNA_STRAND_LENGTH)]
    # Only odd vertices are variables
    variables = vertices[1::2]
    return ', '.join(variables)        

def main():
    graph=create_SAT_graph()
    all_possible_assigments = find_all_paths_in_graph(graph)
    full_paths = filter_by_size(all_possible_assigments, FULL_PATH_LEGTH)
    print("The assigments are: " + "\n".join([printable_assigment(assigment) for assigment in full_paths]))
 
    formula = create_3cnf_boolean_formula(graph["variables"])
    satisfiable_formula_test = create_satisfiable_3cnf_boolean_formula(graph["variables"])
    non_satisfiable_formula_test = create_non_satisfiable_3cnf_boolean_formula(graph["variables"])

    print("The random formula created is: " + printable_formula(formula))
    print(three_SAT(formula, full_paths))

    print("The satisfiable formula created is: " + printable_formula(satisfiable_formula_test))
    print(three_SAT(satisfiable_formula_test, full_paths))

    print("The non satisfiable formula created is: " + printable_formula(non_satisfiable_formula_test))
    print(three_SAT(non_satisfiable_formula_test, full_paths))

if __name__ == '__main__':
    main()