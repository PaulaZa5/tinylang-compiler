from tiny_scanner import TinyScanner
from tiny_parser import TinyParser
from errors import clear_errors
import sys

Tokenize = TinyScanner.tokenize
Parse = TinyParser.parse

def exit():
    sys.exit(
'''
Usage: tinycompiler <single-command> [<args>]

Available commands are:
    -s  : Work as a scanner
    -p  : Work as a parser

Arguments must contain at least the input file, you could supply an output file if you want to save the program's results to the desk.

For example:
    `tinycompiler -s in_file.ext`
    `tinycompiler -s in_file.ext out_file.ext`
    `tinycompiler -p in_file.ext`
    `tinycompiler -p in_file.ext out_file.ext`
''')

if '-h' in sys.argv:
	exit()

if len(sys.argv) is 4:
    try:
        infile = open(sys.argv[2], 'r')
        example = infile.read()
        infile.close()
        outfile = True
    except:
        sys.exit('No such input file exist')
elif len(sys.argv) is 3:
    try:
        infile = open(sys.argv[2], 'r')
        example = infile.read()
        infile.close()
        outfile = False
    except:
        sys.exit('No such input file exist')
else:
    print('Couldn\'t comprehend input arguments\n\n')
    exit()

if sys.argv[1].lower() == '-s':
    if outfile:
        outfile = open(sys.argv[3], 'w')
    
    for elm in Tokenize(example):
        if outfile:
            outfile.write(str(elm[0]) + ', ' + str(elm[1]) + '\n')
        else:
            print(elm[0], elm[1], sep=', ')

    if outfile:
        outfile.close()

elif sys.argv[1].lower() == '-p':
    if outfile:
        outfile = sys.argv[3]

    tree, root_id = Parse(example)

    import pydot as pd
    out_graph = pd.Dot()
    drawn_nodes = set()

    import random
    r = lambda: random.randint(0, 255)
    colors = []

    def recursively_print_tree(root_id, tree, reached_height, reached_width, row_space, column_space, level, caller_node_id=False, constraint=True):
        if len(colors) <= level:
            colors.append('#%02X%02X%02X' % (r(),r(),r()))
        color = colors[level]
            
        if tree[root_id].data['label'] != 'stmt_sequence':
            out_graph.add_node(pd.Node(root_id, pos=(str(reached_height) + ', ' + str(reached_width) + '!'), color=color, **tree[root_id].data))
            reached_height, reached_width = reached_height + row_space, reached_width + column_space
            if caller_node_id is not False:
                out_graph.add_edge(pd.Edge(caller_node_id, root_id, constraint=constraint))
            for node_id in tree.expand_tree():
                if node_id not in drawn_nodes:
                    drawn_nodes.add(node_id)
                    reached_height, reached_width = recursively_print_tree(node_id, tree.subtree(node_id), reached_height, reached_width, row_space, column_space, level+1, root_id)
        else:
            out_graph.add_node(pd.Node(root_id, pos=(str(reached_height) + ', ' + str(reached_width) + '!'), style='invis'))
            if caller_node_id is not False:
                out_graph.add_edge(pd.Edge(caller_node_id, root_id, constraint=constraint, style='invis'))
            reached_height, reached_width = reached_height + row_space, reached_width + column_space
            past_node = caller_node_id
            for node_id in tree.expand_tree():
                if node_id not in drawn_nodes:
                    drawn_nodes.add(node_id)
                    constraint = False
                    if past_node is caller_node_id:
                        constraint = True
                    reached_height, reached_width = recursively_print_tree(node_id, tree.subtree(node_id), reached_height, reached_width, row_space, column_space, level, past_node, constraint=constraint)
                    out_graph.add_edge(pd.Edge(root_id, node_id, style='invis'))
                    past_node = node_id
        return reached_height, reached_width

    recursively_print_tree(root_id, tree, 0, 0, 1, 1, 0)

    import sys, os
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    prog = os.path.join(base_path, 'graphviz-2.38\\bin\\dot.exe')
    
    if outfile:
        out_graph.write_png(outfile, prog=prog)
    else:
        png_str = out_graph.create_png(prog=prog)
        
        from io import BytesIO
        sio = BytesIO()
        sio.write(png_str)
        sio.seek(0)
        
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        img = mpimg.imread(sio)
        imgplot = plt.imshow(img, aspect='equal')
        plt.show()
else:
    print('Couldn\'t comprehend input arguments\n\n')
    exit()

clear_errors()
