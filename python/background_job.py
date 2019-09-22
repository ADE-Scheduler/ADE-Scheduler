# BACKGROUND JOBS
# To be run every 24 hours:
# schedule a job using the cron command on the server.

import requests
import json

from lxml import etree
from datetime import timedelta
from redis import Redis
from hidden import get_token, user, password
from pandas import DataFrame


redis = Redis(host='localhost', port=6379)


def update_projects():
    token = redis.get('ADE_WEBAPI_TOKEN')
    if not token:
        token, expiry = get_token()
        if expiry > 10:
            redis.setex('ADE_WEBAPI_TOKEN', timedelta(seconds=expiry - 10), value=token)
    else:
        token = token.decode()
    headers = {'Authorization': 'Bearer ' + token}
    url = 'https://api.sgsi.ucl.ac.be:8243/ade/v0/api?login=' + user + '&password=' + password + \
          '&function=getProjects&detail=2'
    r = requests.get(url, headers=headers)
    root = etree.fromstring(r.content)
    ids = root.xpath('//project/@id')
    years = root.xpath('//project/@name')

    ade_projects = list()
    for year, id_ in zip(years, ids):
        ade_projects.append({'year': year, 'id': int(id_)})

    redis.set('ADE_PROJECTS', json.dumps(ade_projects))


def update_resources_ids():
    if not redis.exists('ADE_PROJECTS'):
        update_projects()

    token = redis.get('ADE_WEBAPI_TOKEN')
    if not token:
        token, expiry = get_token()
        if expiry > 10:
            redis.setex('ADE_WEBAPI_TOKEN', timedelta(seconds=expiry - 10), value=token)
    else:
        token = token.decode()

    for id_ in map(lambda x: x['id'], json.loads(redis.get('ADE_PROJECTS'))):
        headers = {'Authorization': 'Bearer ' + token}
        url = 'https://api.sgsi.ucl.ac.be:8243/ade/v0/api?login=' + user + '&password=' + password + '&projectId=' + \
              str(id_) + '&function=getResources&detail=2'
        r = requests.get(url + 'getResources&detail=2', headers=headers)
        root = etree.fromstring(r.content)
        df = DataFrame(data=root.xpath('//resource/@id'), index=map(lambda x: x.upper(), root.xpath('//resource/@name'))
                       , columns=['id'])
        hash_table = df.groupby(level=0).apply(lambda x: '|'.join(x.to_dict(orient='list')['id'])).to_dict()
        redis.hmset('{Project=' + str(id_) + '}' + 'ade_webapi_id', hash_table)
        redis.expire('{Project=' + str(id_) + '}' + 'ade_webapi_id', timedelta(days=1))


if __name__ == '__main__':
    update_projects()
    update_resources_ids()