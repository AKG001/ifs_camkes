from camkes.ast import Instance, Connection, Component, Uses, Provides
import ctypes
import networkx as nx
import matplotlib.pyplot as plt

global_id = 1
component_list = dict()
connections_list = dict()
interfaces_list = dict()

logging_file = "ifc_policy_log"

def print_list (list_obj, list_name):
    """Prints the list contents with its list names """
    file = open(logging_file, 'a+')
    file.write ("\n"+list_name+"\n\n")
    for key, value in list_obj.items():
        file.write ("(" + str(key) + " -> " + str(value) +")\n" )
    file.close()

def generate_adjacency_control_matrix(assembly):
    """Finds the component names and connections and \
    calculate the adjacency matrix."""
    global global_id

    """Finding and saving the component names which will \
    act as subjects. Format for saving (Name->(Object, ID, Type))"""

    for name, obj in assembly.composition._mapping.items():
        if isinstance(obj, Instance) and name.encode("ascii")!='rwfm_monitor':
            component_list[name.encode("ascii")] = (obj.type, global_id, type(obj.type))
            global_id = global_id + 1
    
    print_list(component_list, "component_list")

    number_of_subjects = len(component_list)
    access_control_matrix = [[0 for i in range(number_of_subjects)] \
                            for j in range(number_of_subjects)]

    for i in range(number_of_subjects):
        access_control_matrix[i][i] = 1

    for interfaces in assembly.composition.connections:
        for from_end in interfaces.from_ends:
            if from_end._instance._name.encode("ascii") != 'rwfm_monitor' \
               and from_end._parent._to_ends[0]._instance._name.encode("ascii") != 'rwfm_monitor':
                row_id = component_list[from_end._instance.name.encode("ascii")][1]
                column_id = component_list[from_end._parent._to_ends[0]._instance._name.encode("ascii")][1]
                access_control_matrix[row_id-1][column_id-1] = 1
                interfaces_list[from_end] = (from_end.interface.name.encode("ascii"), 
                                            global_id, 
                                            type(from_end.interface), 
                                            from_end.instance.name.encode("ascii"))
                global_id = global_id + 1

        for to_end in interfaces.to_ends:
            if to_end._instance._name.encode("ascii") != 'rwfm_monitor' \
               and to_end._parent._from_ends[0]._instance._name.encode("ascii") != 'rwfm_monitor':
                interfaces_list[to_end] = (to_end.interface.name.encode("ascii"), 
                                            global_id, 
                                            type(to_end.interface),
                                            to_end.instance.name.encode("ascii"))
                global_id = global_id + 1

    print_list (interfaces_list, "interface_list")
    print(access_control_matrix)
    print_graph(access_control_matrix)

def print_graph(access_control_matrix):
    """Create the flow graph and saves it."""
    
    number_of_nodes = len(component_list)

    DG = nx.DiGraph()
    for node in component_list:
        DG.add_node(node)
    
    for start in component_list:
        for end in component_list:
            row = component_list[start][1]
            column   = component_list[end][1]
            if access_control_matrix[row-1][column-1] == 1:
                DG.add_edges_from([(start, end)])
    
    print (DG.nodes()) #print nodes in graph
    print (DG.edges()) #print edges in graph
    nx.draw(DG, node_color = 'Y', node_size=2000, edge_color='r', with_labels=True)
    plt.savefig("path_graph1.png")
    #plt.show()
