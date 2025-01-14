import argparse
import os
import base64
import random

class CC_solver:
    def __init__(self):
        self.raw_input = ""
        self.encoded_graph = ""
        self.iterations = 1
        self.show_solution = False
        self.adj_matrix = None
        self.result_cliques = []

    def decode_graph(self):
        '''
        Function for changing rogal's graph string into matrix of adjacency
        BgAONgo= --> [adj matrix]
        '''
        buff = base64.b64decode(self.encoded_graph)
        n = int.from_bytes(buff[:2], byteorder='little')
        self.adj_matrix = [[0]*n for _ in range(n)]

        index = 2
        mask = 1
        for i in range(n):
            for j in range(i, n):
                if (buff[index] & mask) != 0:
                    self.adj_matrix[i][j] = 1
                    self.adj_matrix[j][i] = 1

                mask <<= 1
                if mask == 256 and index < len(buff):
                    index += 1
                    mask = 1

    def parse_args(self):
        '''
        Parses arguments
        Handles both rogal's string and path of file with rogal's string
        as an input
        '''
        # Parsing
        parser = argparse.ArgumentParser()
        parser.add_argument("input", help="path of file with data or data string")
        parser.add_argument("-i", "--iterations", help="set number of iterations", type=int, default=1)
        parser.add_argument("-s", "--solution", help="show solution in readable form", action="store_true")
        args = parser.parse_args()
        self.raw_input = args.input
        self.iterations = args.iterations
        self.show_solution = args.solution

        # Handling input string
        if os.path.exists(self.raw_input):
            with open(self.raw_input, 'r') as input_file:
                self.encoded_graph = input_file.readline()
        else:
            self.encoded_graph = self.raw_input

    def find_solution(self):
        '''
        Finding solution to CC problem
        Random vertex is being chosen. If there is clique it can be added to, it will be.
        Otherwise new clique with this vertex will be created.
        '''
        def can_form_clique(clique, new_vertex):
            # Checks if a clique will still be a clique after adding new vertex to it
            return all(self.adj_matrix[i][new_vertex] == 1 for i in clique)

        buf_cliques = [] # temporary buffer for cliques
        vertices = list(range(len(self.adj_matrix)))

        while vertices: # repeating for all vertices in random order
            random_vertex = random.choice(vertices)
            found_matching_clique = False

            for i, clique in enumerate(buf_cliques):
                if can_form_clique(clique, random_vertex):
                    found_matching_clique = True
                    clique.append(random_vertex)
                    while i != 0:
                        if len(buf_cliques[i]) > len(buf_cliques[i-1]):
                            tmp = buf_cliques[i]
                            buf_cliques[i] = buf_cliques[i-1]
                            buf_cliques[i-1] = tmp
                            i -= 1
                        else:
                            break
                    break

            if not found_matching_clique:
                buf_cliques.append([random_vertex])

            vertices.remove(random_vertex)
        if not self.result_cliques:
            self.result_cliques = buf_cliques.copy()
        else:
            self.result_cliques = min(self.result_cliques, buf_cliques, key=len) # choosing answer containing least cliques

    def output_solution(self):
        '''
        Outputs solution in Jakub's format:
        [clique1] [clique2] ...
        '''
        def jakub_format(clique):
            n = len(clique)
            a = bytearray()
            a.extend(n.to_bytes(2, byteorder='little', signed=False))
            for vertex in sorted(clique):
                a.extend(vertex.to_bytes(2, byteorder='little', signed=False))
            return base64.b64encode(a).decode("utf-8")

        for clique in self.result_cliques:
            print(jakub_format(clique), end=' ')

    def run(self):
        self.parse_args()
        self.decode_graph()
        for _ in range(self.iterations):
            self.find_solution()
        self.output_solution()
        if self.show_solution:
            print(self.result_cliques)
            print(f"Len: {len(self.result_cliques)}")


if __name__ == '__main__':
    solver = CC_solver()
    solver.run()
