from datetime import datetime
from xml.dom.minidom import parse
import sys
import csv


def main():
    time_start = datetime.now()

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    dom1 = parse(input_file)
    schematics = dom1.getElementsByTagName("schematics")[0]

    nets_map = create_nets(schematics)
    num_nets = len(list(nets_map.keys()))

    edges = create_edges(nets_map, num_nets, schematics)

    res_matrix = calculate_resistances(num_nets, edges)
    write_csv(output_file, res_matrix)
    time_finish = datetime.now()
    print(time_finish - time_start)


def create_nets(schematics):
    nets = schematics.getElementsByTagName("net")
    net_set = set([])
    nets_map = {}

    for net in nets:
        id_ = net.attributes['id'].value
        net_set.add(int(id_))

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
    inf = float('inf')
    distances = [[inf for x in range(num_notes)] for x in range(num_notes)]

    for i in range(num_notes):
        distances[i][i] = 0.0

    for i in range(num_notes):
        for j in range(num_notes):
            for edge in edges[i][j]:

                try:
                    distances[i][j] = 1 / (1 / distances[i][j] + 1 / edge)
                except ZeroDivisionError:
                    distances[i][j] = inf

    for k in range(num_notes):
        for i in range(num_notes):
            for j in range(num_notes):
                if i != j and j != k and i != k:
                    try:
                        distances[i][j] = 1 / (1 / distances[i][j] +
                                               1 / (distances[i][k] + distances[k][j]))
                    except ZeroDivisionError:
                        distances[i][j] = inf

    return distances


def write_csv(filename, res_matrix):
    csv_writer = csv.writer(open(filename, "w", newline=''), delimiter=',')

    for row in res_matrix:
        formatted_row = ["%.6f" % x for x in row]
        csv_writer.writerow(formatted_row)

main()
