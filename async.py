from symbol import except_clause
from pcpi import session_loader
from loguru import logger
import sys
import csv

#==============================================================================
def submit_rql_job(session, rql, name, time_type, time):
    payload = {}

    if time_type == 'relative':
        payload = {
            "limit": 100,
            "sort": [
                {
                    "direction": "desc",
                    "field": "insertTs"
                }
            ],
            "withResourceJson": False,
            "query": rql,
            "timeRange": {
                "type": "relative",
                "value": {
                    "unit": "hour",
                    "amount": time
                },
                "relativeTimeType": "BACKWARD"
            },
            "searchName": name
        }

        res = session.request('POST', 'search/config/jobs', json=payload)
        if res.status_code in session.success_status:
            return [res.json().get('downloadUri'), name]
        else:
            return ['bad','bad']

    elif time_type == 'absolute':
        payload = {
            "limit":100,
            "withResourceJson":False,
            "query":"config from cloud.resource where api.name = 'alibaba-cloud-action-trail' ",
            "id":"ec63118b-4560-41e3-909a-4258f6c700d0",
            "timeRange":{
                "type":"absolute",
                "value":{
                    "endTime":time[0],
                    "startTime":time[1]
                }
            },
            "heuristicSearch":False,
            "searchName": name
        }

        res = session.request('POST', 'search/config/jobs', json=payload)
        if res.status_code in session.success_status:
            return [res.json().get('downloadUri'), name]
        else:
            return ['bad','bad']
    else:
        return ['bad','bad']

#==============================================================================
def wait_on_jobs():
    download_urls = []
    with open('local/urls.csv', 'r') as infile:
        for line in infile:
            download_urls.append(line.strip().split(','))
    print(download_urls)
    



#==============================================================================
if __name__ == '__main__':
    session_man = session_loader.load_from_file()
    session = session_man.create_cspm_session()

    time = None
    time_type = None
    rql = ''
    name = ''
    rql_file_path = ''

    if '-name' in sys.argv and 'rql_file' not in sys.argv:
        try:
            name = sys.argv[sys.argv.index('-name') + 1]
        except:
            print('ERROR. No name specified. Exiting...')
            exit()

    if '-name' not in sys.argv and 'rql_file' not in sys.argv:
        print('ERROR. Missing -name argument. Exiting...')
        exit()

    if 'rql' in sys.argv:
        try:
            rql = sys.argv[sys.argv.index('rql') + 1]
        except:
            print('ERROR. No RQL specified. Exiting...')
            exit()
    
    if 'rql_file' in sys.argv:
        try:
            rql_file_path = sys.argv[sys.argv.index('rql_file') + 1]
        except:
            print('ERROR. Missing file path. Exiting...')
            exit()

    if 'time' in sys.argv:
        try:
            time_in_hours = sys.argv[sys.argv.index('time') + 1]
            time_type = 'relative'
        except:
            print('ERROR. No time specified. Exiting...')
            exit()

    if 'time_range' in sys.argv:
        try:
            time_range = sys.argv[sys.argv.index('time_range') + 1].split(',')
            time_type = 'absolute'
            if len(time_range) != 2:
                print('ERROR. Invalid time range format. Exiting...')
                exit()
        except:
            print('ERROR. No time range specified. Exiting...')
            exit()

    if 'rql' not in sys.argv and 'rql_file' not in sys.argv:
        print('No \'rql\' or \'rql_file\' argument specified. Exiting...')
        exit()
    
    if 'time' not in sys.argv and 'time_range' not in sys.argv and 'rql_file' not in sys.argv:
        print('No \'time\' or \'time_range\' argument specified. Exiting...')
        exit()

    download_urls = []
    if rql_file_path:
        with open(rql_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                rql_query = row[0]
                name = row[1]
                time_type = row[2]
                time = row[3]
                download_urls.append(submit_rql_job(session, rql_query, name, time_type, time))
    else:
        submit_rql_job(session, rql, name, time_type, time)

    with open('local/urls.csv', 'w') as outfile:
        for el in download_urls:
            outfile.write(el[0] + ',' + el[1])
            outfile.write('\n')

    wait_on_jobs()