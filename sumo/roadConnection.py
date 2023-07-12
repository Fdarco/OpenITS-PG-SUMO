from rich import print
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from collections import defaultdict


@dataclass
class baseConnection:
    fromEdge: str
    toEdge: str


@dataclass
class Trip:
    trip_id: int
    path: str


class RoadConnection:
    def __init__(self, netFile: str) -> None:
        self.netFile = netFile
        self.roadConnection: dict[
            str, dict[str, list[baseConnection]]
        ] = defaultdict(dict)
        self.roads: set[str] = set()
        self.getConnection()

    def getConnection(self):
        etree = ET.parse(self.netFile)
        root = etree.getroot()
        for child in root:
            if child.tag == 'connection':
                fromEdge = child.attrib['from']
                fromRoad = fromEdge.split('_')[0]
                toEdge = child.attrib['to']
                toRoad = toEdge.split('_')[0]
                '''
                ----这里由于车辆可以掉头，所以当 fromRoad==toRoad 的时候可以有两个
                    `baseConnection`。
                ----Since vehicles can make a U-turn, when fromRoad==toRoad, 
                    there can be two `baseConnection`.
                '''
                try:
                    self.roadConnection[fromRoad][toRoad].append(
                        baseConnection(fromEdge, toEdge)
                    )
                except KeyError:
                    self.roadConnection[fromRoad][toRoad] = [
                        baseConnection(fromEdge, toEdge)
                    ]
                self.roads.add(fromRoad)
                self.roads.add(toRoad)

    def getEdges(self, fromRoad: str, toRoad: str, fromEdge: str):
        try:
            if fromEdge:
                connections = self.roadConnection[fromRoad][toRoad]
                for connection in connections:
                    if connection.fromEdge == fromEdge:
                        toEdge = connection.toEdge
                        break
            else:
                '''
                ----用于起始两条路段不一样时获得 `fromEdge` 和 `toEdge`
                ----Used to obtain fromEdge and toEdge 
                    when the first two road sections are different.
                '''
                connection = self.roadConnection[fromRoad][toRoad][0]
                fromEdge = connection.fromEdge
                toEdge = connection.toEdge
        except KeyError:
            print(
                'KeyError: There is no valid connection between {} and {}'.format(
                    fromRoad, toRoad
                )
            )
            raise KeyError
        return fromEdge, toEdge

    def getTriEdges(self, originRoad: str, secondRoad: str, thirdRoad: str):
        if thirdRoad == secondRoad:
            raise ValueError
        midEdge, lastEdge = self.getEdges(secondRoad, thirdRoad, None)
        connections = self.roadConnection[originRoad][secondRoad]
        for c in connections:
            if c.toEdge == midEdge:
                originEdge = c.fromEdge
                break
        return originEdge, midEdge, lastEdge

    def getRoutes(self, Path: str):
        path = Path.split('-')
        if len(path) == 1:
            if Path in self.roads:
                print(f'[yellow]One edge path({Path}).[/yellow]')
                return [Path + '_sa']
            else:
                print(f'[red]There is no road named {Path}[/red]')
                raise KeyError
        '''
        ----在前两条路段有回头路的情况下，需要根据第三条路段来判断正确的起始方向。
        ----In the case where the first two road sections have a U-turn, 
            it is necessary to determine the correct starting direction 
            based on the third road section.
        '''
        originRoad = path[0]
        secondRoad = path[1]
        if originRoad == secondRoad:
            if len(path) == 2:
                fromEdge, toEdge = self.getEdges(
                    originRoad, secondRoad, None
                )
                routeEdges = [fromEdge, toEdge]
                return routeEdges
            else:
                thirdRoad = path[2]
                try:
                    originEdge, midEdge, lastEdge = self.getTriEdges(
                        originRoad, secondRoad, thirdRoad
                    )
                except ValueError:
                    raise ValueError('The first three roads are the same.')
                routeEdges = [originEdge, midEdge, lastEdge]
                for i in range(2, len(path)-1):
                    fromRoad = path[i]
                    toRoad = path[i+1]
                    fromEdge, toEdge = self.getEdges(fromRoad, toRoad, toEdge)
                    routeEdges.append(fromEdge)
                if len(path) > 3:
                    _, toEdge = self.getEdges(
                        path[-2], path[-1], fromEdge)
                    routeEdges.append(toEdge)
                return routeEdges

        else:
            routeEdges = []
            fromEdge, toEdge = self.getEdges(originRoad, secondRoad, None)
            routeEdges.append(fromEdge)
            for i in range(1, len(path)-1):
                fromRoad = path[i]
                toRoad = path[i+1]
                fromEdge, toEdge = self.getEdges(fromRoad, toRoad, toEdge)
                routeEdges.append(fromEdge)
            if len(path) > 2:
                _, toEdge = self.getEdges(path[-2], path[-1], fromEdge)
                routeEdges.append(toEdge)
            return routeEdges
