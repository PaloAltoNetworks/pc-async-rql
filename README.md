# Scripts for starting RQL jobs

# Python

## Installation

```bash
pip3 install -r requirements.txt
```

## Running

The script has 2 main use cases that use different command line arguments. Single RQL and multi RQL from csv file

### Single RQL with relative time in hours. Format: -time <time_in_hours>
```bash
python3 async.py -rql "config from iam where cloud.account != 'hats'" -name my_search -time 24
```

### Single RQL with absolute time in epoch time. Format: -time_range "<start_time_epoch>,<end_time_epoch>"
```bash
python3 async.py -rql "config from iam where cloud.account != 'hats'" -name my_search -time_range "166187406700,1662046867000"
```

### Multi RQL from file

```bash
python3 async.py rql_file <path_to_file>
python3 async.py rql_file input/my_rqls.csv
python3 async.py rql_file rqls.csv
```
CSV file format:

**An example RQL CSV is included. Named "rqls.csv"**

- Relative Time  
"\<rql>",<name_of_search>,relative,<time_in_hours>
EX:  
```"config from iam where cloud.account != 'hats'",My FIRSTs search,relative,24```
- Absolute Time
"\<rql>",<name_of_search>,absolute,"\<start_time_epoch>,\<end_time_epoch>"
EX:  
```"config from iam where cloud.account != 'shirts'",My SECONDs search,absolute,"166187406700,1662046867000"```


# Bash

## Requirements for Bash 

Bash

JQ 

```
brew install jq
```

The shell script execs jq commands so ensure jq program is included in the path of the user running the script.

## Setup for Bash

Configure in the script:
SERVER_IP=
CUSTOMER=""
USER=""
PASSWORD=""

## Running the Bash script

```
bash async.sh
```