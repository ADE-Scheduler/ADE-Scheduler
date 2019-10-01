#!/home/technics/ADE-Scheduler/venv/bin/python3.6
# BACKGROUND JOBS
# To be run every 24 hours:
# schedule a job using the cron command on the server.

import json
import pickle
from datetime import timedelta
from redis import Redis
from pandas import DataFrame
from ade import ade_request


redis = Redis(host='localhost', port=6379)


def update_projects():
    root = ade_request(redis, 'function=getProjects', 'detail=2')
    ids = root.xpath('//project/@id')
    years = root.xpath('//project/@name')

    ade_projects = list()
    for year, id_ in zip(years, ids):
        ade_projects.append({'year': year, 'id': int(id_)})

    redis.set('ADE_PROJECTS', json.dumps(ade_projects))


def update_resources_ids():
    if not redis.exists('ADE_PROJECTS'):
        update_projects()

    for project_id in map(lambda x: x['id'], json.loads(redis.get('ADE_PROJECTS'))):
        root = ade_request(redis, 'projectId=%d' % project_id, 'function=getResources', 'detail=2')
        df = DataFrame(data=root.xpath('//resource/@id'), index=map(lambda x: x.upper(), root.xpath('//resource/@name'))
                       , columns=['id'])
        hash_table = df.groupby(level=0).apply(lambda x: '|'.join(x.to_dict(orient='list')['id'])).to_dict()
        h_map = '{Project=%d}ADE_WEBAPI_ID' % project_id
        redis.hmset(h_map, hash_table)
        redis.expire(h_map, timedelta(days=1))


def update_classrooms():
    if not redis.exists('ADE_PROJECTS'):
        update_projects()

    def __location__(address):
        location = ''
        if address['type'] != '':
            location += address['type']
        if address['size'] != '':
            if location == '':
                location += 'Taille :' + address['size']
            else:
                location += ', taille :' + address['size']
        if address['address_2'] != '':
            location += '\n' + address['address_2']
        if address['address_1'] != '':
            if location != '' and ['address_2'] != '':
                location += ' ' + address['address_1']
            else:
                location += '\n' + address['address_1']
        if address['zipCode'] != '':
            location += '\n' + address['zipCode']
        if address['city'] != '':
            if location != '' and address['zipCode'] != '':
                location += ' ' + address['city']
            else:
                location += '\n' + address['city']
        if address['country'] != '':
            location += '\n' + address['country']

        return location

    for project_id in map(lambda x: x['id'], json.loads(redis.get('ADE_PROJECTS'))):
        h_map = '{Project=%d}ADE_WEBAPI_ID' % project_id
        if not redis.exists(h_map):
            update_resources_ids()  # should be called max once

        root = ade_request(redis, 'projectId=%d' % project_id, 'function=getResources',
                           'detail=13', 'tree=false', 'category=classroom')

        names = root.xpath('//room/@name')
        codes = root.xpath('//room/@code')
        types = root.xpath('//room/@type')
        sizes = root.xpath('//room/@size')
        zip_codes = root.xpath('//room/@zipCode')
        countries = root.xpath('//room/@country')
        addresses_1 = root.xpath('//room/@address1')
        addresses_2 = root.xpath('//room/@address2')
        cities = root.xpath('//room/@city')

        d = {'name': names, 'code': codes, 'type': types, 'size': sizes, 'zipCode': zip_codes,
             'country': countries, 'address_1': addresses_1, 'address_2': addresses_2, 'city': cities}

        df = DataFrame(data=d, dtype=str)
        df.drop_duplicates('name', inplace=True)
        df.sort_values('name', inplace=True)
        df.reset_index(inplace=True, drop=True)

        h_map = '{Project=%d}ADDRESSES' % project_id
        redis.setex(h_map, timedelta(days=1), value=pickle.dumps(df))

        df.set_index('name', inplace=True)
        hash_table = {key: __location__(values) for key, values in df.to_dict('index').items()}
        h_map = '{Project=%d}CLASSROOMS' % project_id

        redis.hmset(h_map, hash_table)
        redis.expire(h_map, timedelta(days=1))


if __name__ == '__main__':
    update_projects()
    update_resources_ids()
    update_classrooms()
