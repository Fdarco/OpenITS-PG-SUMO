import os
import yaml
import psycopg
import getpass
from rich import print
from collections import defaultdict
from datetime import datetime, timedelta

from roadConnection import Trip, baseConnection, RoadConnection


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

start_time = datetime.strptime('2019-08-12 17:00:00', '%Y-%m-%d %H:%M:%S')
# start_time = datetime.strptime('2019-08-13 17:00:00', '%Y-%m-%d %H:%M:%S')
# start_time = datetime.strptime('2019-08-14 17:00:00', '%Y-%m-%d %H:%M:%S')
end_time = start_time + timedelta(hours=1)

cur = conn.execute(
    """select Trip_ID, Departure_time, Path
        from the_synthetic_individual_level_trip_dataset
        where departure_time between '{}' and '{}'
        order by departure_time;""".format(
        start_time.strftime('%Y-%m-%d %H:%M:%S'),
        end_time.strftime('%Y-%m-%d %H:%M:%S')
    )
)

'''
----原数据中 `departure_time` 只精确到分钟，每分钟内有多辆车出发。
    我们要让车辆平均分配在这一分钟内。
----In the original data, the departure_time is only accurate to the minute, 
    and multiple vehicles depart within each minute. 
    We need to evenly distribute the vehicles within this minute.
'''
minutes_trips: dict[str, list[Trip]] = defaultdict(list)
totalTrips = 0
for data in cur.fetchall():
    trip_id = data[0]
    depart_time = data[1].replace(tzinfo=None)
    time_diff = int((depart_time - start_time).total_seconds() / 60)
    path = data[2]
    minutes_trips[time_diff].append(Trip(trip_id, path))
    totalTrips += 1

conn.close()

rc = RoadConnection('./simulationFiles/xuancheng.net.xml')
with open('./simulationFiles/xuancheng.rou.xml', 'w') as rf:
    print('''<routes>''', file=rf)
    validTrips = 0
    for mk, mv in minutes_trips.items():
        tripNums = len(mv)
        for i in range(tripNums):
            try:
                edges = ' '.join(rc.getRoutes(mv[i].path))
            except Exception as e:
                print(f'There is no valid path for trip {mv[i].trip_id}')
                continue
            print('''    <vehicle id="{}" depart="{}" departLane="random">'''.format(
                'veh_' + str(mv[i].trip_id), mk + i/tripNums,
            ), file=rf)
            print(f'''        <route edges="{edges}"/>''', file=rf)
            print('''    </vehicle>''', file=rf)
            validTrips += 1

    print('''</routes>''', file=rf)

print(
    f'[green]There are {validTrips}/{totalTrips} vehicles are generated.[/green]'
)
