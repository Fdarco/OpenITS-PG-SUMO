import os
import csv
import yaml
import psycopg
import getpass
from rich import print
from psycopg import sql


if os.path.exists('databaseConfig.yaml'):
    config = yaml.load(open('databaseConfig.yaml'), Loader=yaml.FullLoader)
else:
    user = input('Username: ')
    password = getpass.getpass('Password: ')
    config = {
        'USER': user,
        'PASSWORD': password
    }

print('[yellow]Connection to database: OPENITS.[/yellow]')
conn = psycopg.connect(
    'dbname=OPENITS user={} password={}'.format(
        config['USER'], config['PASSWORD']
    )
)

print('[yellow]Create table zone_roads.[/yellow]')
conn.execute(
    """CREATE TABLE IF NOT EXISTS zone_roads(
    Zone_ID TEXT PRIMARY KEY,
    Longitude REAL,
    Latitude REAL,
    Roads TEXT)"""
)

print('[yellow]Create table The_synthetic_individual_level_trip_dataset.[/yellow]')
conn.execute(
    """CREATE TABLE IF NOT EXISTS The_synthetic_individual_level_trip_dataset(
    Trip_ID INT PRIMARY KEY,
    Traveller_ID TEXT,
    Traveller_type TEXT,
    Departure_time TIMESTAMPTZ,
    Time_slot TEXT,
    O_zone TEXT,
    D_zone TEXT,
    Path TEXT,
    Duration REAL)"""
)

conn.commit()

print('[yellow]Insert data into zone_roads.[/yellow]')
with open('../openits/zone_roads.csv', 'r', encoding='utf-8') as zrFile:
    next(zrFile)
    zData = csv.reader(zrFile)
    for row in zData:
        zone_id = row[0]
        longitue = float(row[1])
        latitude = float(row[2])
        roads = row[3]
        conn.execute("""INSERT INTO zone_roads VALUES(%s, %s, %s, %s);""",
                     (zone_id, longitue, latitude, roads))
print('[green]zone_roads: data insert successfully.[/green]')

conn.commit()

print('[yellow]Insert data into The_synthetic_individual_level_trip_dataset.[/yellow]')
with open('../openits/The_synthetic_individual-level_trip_dataset.csv', 'r', encoding='utf-8') as tFile:
    next(tFile)
    tData = csv.reader(tFile)
    trip_id = 0
    for row in tData:
        traveller_id = row[0]
        traveller_type = row[1]
        date = row[2]
        time = row[3]
        departure_time = date + ' ' + time
        time_slot = row[4]
        o_zone = row[5]
        d_zone = row[6]
        path = row[7]
        duration = float(row[8])
        conn.execute("""INSERT INTO the_synthetic_individual_level_trip_dataset VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                     (
                         trip_id, traveller_id, traveller_type, departure_time,
                         time_slot, o_zone, d_zone, path, duration
                     ))
        trip_id += 1

print('[green]The_synthetic_individual_level_trip_dataset: data insert successfully.[/green]')

conn.commit()
print('[green]Data commit successfully![/green]')
