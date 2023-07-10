import os
import yaml
import json
import psycopg
import getpass
import subprocess
from rich import print
from copy import deepcopy
from dataclasses import dataclass


@dataclass
class Node:
    id: str
    x: float
    y: float


@dataclass
class Edge:
    id: int
    fnode: str
    tnode: str
    lanenum: int
    shape: str


if os.path.exists('../databaseConfig.yaml'):
    config = yaml.load(open('../databaseConfig.yaml'), Loader=yaml.FullLoader)
else:
    user = input('Username: ')
    password = getpass.getpass('Password: ')
    config = {
        'USER': user,
        'PASSWORD': password
    }

conn = psycopg.connect(
    'dbname=OPENITS user={} password={}'.format(
        config['USER'], config['PASSWORD']
    )
)

'''
----由于 `.shp` 文件中只提供了一个方向的形状，因此需要自行确定对向道路的形状.
    `.shp` 文件中所有道路的都是双向四车道，这对于部分高速公路来说是不可思议的,
    但是我也只能按照原始数据来进行路网构建。
----Since the .shp file only provides the shape of one direction, 
    it is necessary to determine the shape of the opposite road by oneself. 
    All roads in the .shp file are two-way four-lane, 
    which is incredible for some highways. 
    But I can only build the road network according to the original data.
'''
cur = conn.execute(
    """select objectid, fnode, tnode, 
    lanenum, lanenum_sa, lanenum_op, 
    st_asgeojson((st_transform(st_setsrid(geom, 4326), 900913))) 
    from topo_centerroad;"""
)
NodesInfo: dict[str, Node] = {}
EdgesInfo: dict[str, Edge] = {}
for data in cur.fetchall():
    edgeid = int(data[0])
    fnode = str(int(data[1]))
    tnode = str(int(data[2]))
    lanenum = int(data[3])
    '''
    ----部分道路只提供了 `lanenum` 字段，`lanenum_sa` 和 `lanenum_op` 都是 None.
        但是查看数据库，在 fnode 和 tnode 之间仍然只有一条道路，
        所以反向的道路仍然需要我们手动补充。
    ----Some roads only provide the `lanenum` field, 
        both `lanenum_sa` and `lanenum_op` are None. 
        However, when checking the database, 
        there is still only one road between fnode and tnode, 
        so the reverse road still needs to be manually supplemented by us.
    '''
    try:
        lanenum_sa = int(data[4])
    except TypeError:
        lanenum_sa = 2
    try:
        lanenum_op = int(data[5])
    except TypeError:
        lanenum_op = 2
    geom = json.loads(data[6])
    coordinates = geom['coordinates'][0]
    fnodeCoord = coordinates[0]
    tnodeCoord = coordinates[-1]

    NodesInfo[fnode] = Node(fnode, fnodeCoord[0], fnodeCoord[1])
    NodesInfo[tnode] = Node(tnode, tnodeCoord[0], tnodeCoord[1])

    coordinates_op = deepcopy(coordinates)
    coordinates_op.reverse()
    edgeShape = ' '.join(
        ','.join(coordstr)
        for coordstr in [
            list(map(str, coord)) for coord in coordinates
        ])
    edgeShape_op = ' '.join(
        ','.join(coordstr)
        for coordstr in [
            list(map(str, coord)) for coord in coordinates_op
        ])
    edge_sa_id = str(edgeid) + '_sa'
    edge_op_id = str(edgeid) + '_op'

    EdgesInfo[edge_sa_id] = Edge(
        edge_sa_id, fnode, tnode, lanenum_sa, edgeShape)
    EdgesInfo[edge_op_id] = Edge(
        edge_op_id, tnode, fnode, lanenum_op, edgeShape_op)

conn.close()


with open('./simulationFiles/xuancheng.nod.xml', 'w') as nf:
    print('<nodes>', file=nf)
    for nk, nv in NodesInfo.items():
        print('    <node id="{}" x="{}" y="{}"/>'.format(
            nk, nv.x, nv.y
        ), file=nf)
    print('</nodes>', file=nf)

with open('./simulationFiles/xuancheng.edg.xml', 'w') as ef:
    print('<edges>', file=ef)
    for ek, ev in EdgesInfo.items():
        print('    <edge id="{}" from="{}" to="{}" numLanes="{}" spreadType="right" shape="{}"/>'.format(
            ek, ev.fnode, ev.tnode, ev.lanenum, ev.shape
        ), file=ef)
    print('</edges>', file=ef)

subprocess.run([
    'netconvert', '-n', 'simulationFiles/xuancheng.nod.xml',
    '-e', 'simulationFiles/xuancheng.edg.xml',
    '-o', 'simulationFiles/xuancheng.net.xml'
])
