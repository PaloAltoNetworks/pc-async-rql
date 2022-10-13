from pcpi import session_loader
from loguru import logger
import sys
import csv
import time as time_module
import os
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
        time = time.split(',')
        payload = {
            "limit":100,
            "withResourceJson":False,
            "query":rql,
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
def wait_on_jobs(session):
    download_urls = []
    with open('local/urls.csv', 'r') as infile:
        for line in infile:
            download_urls.append(line.strip().split(','))

    while len(download_urls) > 0:
        for index, url in enumerate(download_urls):
            res = session.request('GET', url[0])
            if res.status_code == 200:
                session.logger.info(f'Search: {url[1]} completed.')
                download_file(session,url[0],url[1])
                download_urls.pop(index)
            else:
                session.logger.info(f'Search: {url[1]} in progress.')

#==============================================================================
def download_file(session,url,name):
    
    session.logger.info(f"Downloading: {name}")
    curl = f"""
    curl -k -o output/{name}.csv  "{session.api_url}{url}" \\
      -H 'Connection: keep-alive' \\
      -H 'sec-ch-ua: "Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"' \\
      -H 'x-redlock-auth: '{session.token} \\
      -H 'sec-ch-ua-mobile: ?1' \\
      -H 'User-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36' \\
      -H 'Content-Type: application/json' \\
      -H 'Accept: application/json, text/plain, */*' \\
      -H 'x-redlock-request-id: aaaaaaaaaaaa91548' \\
      -H 'sec-ch-ua-platform: "Android"' \\
      -H 'Origin: '"{session.api_url}/" \\
      -H 'Sec-Fetch-Site: same-site' \\
      -H 'Sec-Fetch-Mode: cors' \\
      -H 'Sec-Fetch-Dest: empty' \\
      -H 'Referer: '"{session.api_url}/" \\
      -H 'Accept-Language: en-US,en;q=0.9' \\
      --compressed
    """
    os.system(curl)
    
#==============================================================================
if __name__ == '__main__':
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


    session_man = session_loader.load_from_file(logger=logger)
    session = session_man.create_cspm_session()

    download_urls = []
    if rql_file_path:
        with open(rql_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                rql_query = row[0]
                name = row[1]
                #Updated name with current time
                name += '_' + str(time_module.time())
                name = name.replace(' ', '_')
                name = name.replace('.','_')
                time_type = row[2]
                time = row[3]
                download_urls.append(submit_rql_job(session, rql_query, name, time_type, time))
    else:
        name += '_' + str(time_module.time())
        name = name.replace(' ', '_')
        name =name.replace('.','_')
        submit_rql_job(session, rql, name, time_type, time)

    with open('local/urls.csv', 'w') as outfile:
        for el in download_urls:
            outfile.write(el[0] + ',' + el[1])
            outfile.write('\n')
  
    wait_on_jobs(session)