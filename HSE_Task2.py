from datetime import datetime
from xml.dom.minidom import parse, parseString
import sys
import csv

import cpp_module

def main():
    #time_start = datetime.now()

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    dom1 = parse(input_file)
    schematics = dom1.getElementsByTagName("schematics")[0]

    nets_map = create_nets(schematics)
    num_nets = len(nets_map.keys())

    edges = create_edges(nets_map, num_nets, schematics)

    res_matrix = calculate_resistances(num_nets, edges)
    write_csv(output_file, res_matrix)
    #time_finish = datetime.now()
    #print (time_finish - time_start)


def create_nets(schematics):
    nets = schematics.getElementsByTagName("net")
    net_set = set([])
    nets_map = {}

    for net in nets:
        id = net.attributes['id'].value
        net_set.add(int(id))

    net_list = sorted(list(net_set))

    for i in range(len(net_list)):
        nets_map.update({net_list[i]: i})

    return nets_map


def create_edges(nets_map, length, schematics):
    num_notes = length
    edges = [[list([]) for x in range(num_notes)] for x in range(num_notes)]
    add_resistors(nets_map, schematics, edges)
    add_capactors(nets_map, schematics, edges)
    add_diods(nets_map, schematics, edges)

    return edges


def add_resistors(nets_map, schematics, edges):
    resistors = schematics.getElementsByTagName("resistor")

    for resistor in resistors:
        net_from = int(resistor.attributes['net_from'].value)
        net_to = int(resistor.attributes['net_to'].value)
        res = float(resistor.attributes['resistance'].value)

        edges[nets_map[net_from]][nets_map[net_to]].append(res)
        edges[nets_map[net_to]][nets_map[net_from]].append(res)


def add_capactors(nets_map, schematics, edges):
    capactors = schematics.getElementsByTagName("capactor")

    for capactor in capactors:
        net_from = int(capactor.attributes['net_from'].value)
        net_to = int(capactor.attributes['net_to'].value)
        res = float(capactor.attributes['resistance'].value)

        edges[nets_map[net_from]][nets_map[net_to]].append(res)
        edges[nets_map[net_to]][nets_map[net_from]].append(res)


def add_diods(nets_map, schematics, edges):
    diods = schematics.getElementsByTagName("diode")

    for diod in diods:
        net_from = int(diod.attributes['net_from'].value)
        net_to = int(diod.attributes['net_to'].value)
        res = float(diod.attributes['resistance'].value)
        res_reverse = float(diod.attributes['reverse_resistance'].value)

        edges[nets_map[net_from]][nets_map[net_to]].append(res)
        edges[nets_map[net_to]][nets_map[net_from]].append(res_reverse)


def calculate_resistances(num_notes, edges):

    print("Python time: ", end="")


    Inf = float('inf')
    d = [[Inf for x in range(num_notes)] for x in range(num_notes)]

    for i in range(num_notes):
        d[i][i] = 0.0

    for i in range(num_notes):
        for j in range(num_notes):
            for edge in edges[i][j]:

                try:
                    d[i][j] = 1 / (1 / d[i][j] + 1 / edge)
                except ZeroDivisionError:
                    d[i][j] = Inf

    time_start = datetime.now()
    dCXX = [x.copy() for x in d]

    for k in range(num_notes):
        for i in range(num_notes):
            for j in range(num_notes):
                if (i != j):
                    try:
                        d[i][j] = 1 / (1 / d[i][j] + 1 / (d[i][k] + d[k][j]))
                    except ZeroDivisionError:
                        d[i][j] = Inf

    time_finish = datetime.now()
    python_time = time_finish - time_start
    print(python_time)
    print("C time:", end="")

    start_time = datetime.now()

    cpp_module.Cycle(dCXX)

    cxx_time = datetime.now() - start_time
    print(cxx_time)
    print('\n')

    try:
        print("Python was slower by %f",python_time/cxx_time)
    except ZeroDivisionError:
        print("Python was slower by INF because cxx_time=0")
    for i in range(num_notes):
        for j in range(num_notes):
            if d[i][j] != dCXX[i][j]:
                print("Failed")
                #break;

    return d


def write_csv(filename, res_matrix):
    csv_writer = csv.writer(open(filename, "w", newline=''), delimiter=',')

    for row in res_matrix:
        formatted_row = ["%.6f" % x for x in row]
        csv_writer.writerow(formatted_row)

main()
