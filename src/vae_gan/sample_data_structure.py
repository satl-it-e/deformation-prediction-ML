import math
import glob
import pandas as pd
import json

def get_surface_nodes(file_ids=(1,385)):
    X_nodes = []
    sample_filenames = glob.glob('./data/sample_model/model/*.json')
    for sample_filename in sample_filenames[:len(file_ids)]:
        with open(sample_filename, 'r') as file:
            data = json.load(file)
            surface_node_ids = {d['node_id'] for d in data['surf_elements']}

            surface_nodes = {int(node['node_id']): tuple((math.floor(float(value))+1) for (key,value) in node.items() if key in ['x', 'y', 'z']) for node in data['nodes'] if node['node_id'] in surface_node_ids}
        X_nodes.append(surface_nodes)
    return X_nodes


def get_voxel_shapes_from_nodes_dicts(surface_nodes):
    X = []
    for i in range(len(surface_nodes)):
        surface_nodes_coords = set(surface_nodes[i].values())
        voxel_grid = [[[int((x,y,z) in surface_nodes_coords) for x in range(100)] for y in range(100)] for z in range(600)]
        X.append(voxel_grid)
    return X


def get_conditions(file_ids=range(1,385)):
    X_conditions = []
    filenames = glob.glob('cleared_data/pre_*.csv')

    for filename in filenames[:len(file_ids)]:
        x_cond = dict()
        df = pd.read_csv(filename)
        x_cond['box_thickness'] = df['a_thickness'][0]
        x_cond['volume_relation'] = df['r_l'][0] * df['r_w'][0] * df['r_h'][0]
        x_cond['force_application_coord_l'] = df['r_cm_l'][0]  # dist from box-top center to the main point of force application / dist from center to ende along length
        x_cond['force_application_coord_w'] = df['r_cm_w'][0]  # ... along  width

        X_conditions.append(x_cond)
    return X_conditions


def get_surface_nodes_dispositions(file_ids=(1,385)):
    GT_disps = []  # ground truth
    filenames = glob.glob('data/sample_gt/gt/*.csv')
    for i, filename in enumerate(filenames[:len(file_ids)]):
        df = pd.read_csv(filename)
        surface_nodes_dispositions = {row['node_id']:(row['dx'], row['dy'], row['dz']) for (index, row) in df.iterrows()}
        GT_disps.append(surface_nodes_dispositions)
    return GT_disps


def get_disposed_nodes(initial_surface_nodes, surface_nodes_dispositions):
    GT_nodes = []
    for i in range(len(initial_surface_nodes)):
        surface_nodes = dict()
        for node_id in initial_surface_nodes[i].keys():
            if node_id in initial_surface_nodes[i] and node_id in surface_nodes_dispositions[i]:
                surface_nodes[node_id] = tuple(math.ceil(sum(x)) for x in zip(initial_surface_nodes[i][node_id], surface_nodes_dispositions[i][node_id]))
        GT_nodes.append(surface_nodes)
    return GT_nodes


def get_arr_shape(arr):
    shape = []
    while isinstance(arr, list):  # enh: use Iterable but fix it for str
        print(arr)
        shape.append(len(arr))
        arr = arr[0]
    return tuple(shape)


def reshape_voxel_grid_into_np(x_arr):
    return [np.reshape(x, get_arr_shape(x)) for x in x_arr]