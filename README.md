# Scripts for starting RQL jobs

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