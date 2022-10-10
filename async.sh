#!/bin/bash
# Call the RQL async query endpoint
# Requires curl for submitting HTTP requests  and jq for parsing and pretty-printing JSON output

# Stop for errors
#set -e

INSECURE=-k
CURL_DEBUG=-v

#
# Login
#

SERVER_IP=https://api.prismacloud.io
CUSTOMER="hsdkjshdfkj"
USER=""
PASSWORD=""
RQL="config from cloud.resource where cloud.type = \'aws\' AND api.name = \'aws-describe-vpc-endpoints\' AND json.rule = _DateTime.daysBetween($.x,$.y) equals 4"
SEARCHNAME="Test search demo  $( date )"

echo "login as $CUSTOMER"
TOKEN=$( curl $INSECURE --silent --location --request POST ''${SERVER_IP}'/login' \
                   --header 'Content-Type: application/json' \
                   --data-raw '{
                       "customerName": "'"${CUSTOMER}"'",
                       "username": "'${USER}'",
                       "password": "'${PASSWORD}'"
                   }' | jq .token | sed 's/\"//g' )

if [ $? -ne 0 ]; then echo "error logging in $?"; exit 1; fi
echo "Login complete"

#
# Asynchronous RQL query
#
echo "Submitting RQL job"
JSON_RESULT=$( curl $INSECURE --silent --location --request POST "${SERVER_IP}/search/config/jobs" \
--header 'Content-Type: application/json' \
--header 'x-redlock-auth: '${TOKEN}'' \
--data-raw '{
    "limit": 10,
    "sort": [
        {
            "direction": "desc",
            "field": "insertTs"
        }
    ],
    "withResourceJson": false,
    "query": "'"${RQL}"'",
    "timeRange": {
        "type": "relative",
        "value": {
            "unit": "hour",
            "amount": 24
        },
        "relativeTimeType": "BACKWARD"
    },
    "searchName": "'"${SEARCHNAME}"'"
}' )

if [ $? -ne 0 ]; then echo "error submitting job $?"; exit 1; fi

echo "Job with ID $( echo $JSON_RESULT | jq .id)  and URI for download $( echo $JSON_RESULT | jq .downloadUri ) submitted..."
DOWNLOADURI=$( echo $JSON_RESULT | jq .downloadUri | sed 's/\"//g' )

#
# Check for download
#
echo "Check for downloadUri $DOWNLOADURI"

HTTP_STATUS=0
while [ $HTTP_STATUS -lt 400 ]
do
  # creates a new file descriptor 3 that redirects to 1 (STDOUT)
  exec 3>&1
  # Run curl in a separate command, capturing output of -w "%{http_code}" into HTTP_STATUS
  # and sending the content to this command's STDOUT with -o >(cat >&3)
  #HTTP_STATUS=$(curl -w "%{http_code}" -o >(cat >&3) 'http://example.com')

  HTTP_STATUS=$( curl $INSECURE --silent  -w "%{http_code}" -o >(cat >&3)  "${SERVER_IP}${DOWNLOADURI}" \
    -H 'Connection: keep-alive' \
    -H 'sec-ch-ua: "Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"' \
    -H 'x-redlock-auth: '${TOKEN} \
    -H 'sec-ch-ua-mobile: ?1' \
    -H 'User-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36' \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/plain, */*' \
    -H 'x-redlock-request-id: aaaaaaaaaaaa91548' \
    -H 'sec-ch-ua-platform: "Android"' \
    -H 'Origin: '"http://${SERVER_IP}/" \
    -H 'Sec-Fetch-Site: same-site' \
    -H 'Sec-Fetch-Mode: cors' \
    -H 'Sec-Fetch-Dest: empty' \
    -H 'Referer: '"http://${SERVER_IP}/" \
    -H 'Accept-Language: en-US,en;q=0.9' \
    --compressed )

  echo "HTTP status (202 in progress, 200 done, other error) = $HTTP_STATUS"

  if [ $HTTP_STATUS -eq 200 ]
  then
    echo "Downloading file rql-async-job.csv"
    curl $INSECURE -o rql-async-job.csv  "${SERVER_IP}${DOWNLOADURI}" \
      -H 'Connection: keep-alive' \
      -H 'sec-ch-ua: "Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"' \
      -H 'x-redlock-auth: '${TOKEN} \
      -H 'sec-ch-ua-mobile: ?1' \
      -H 'User-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36' \
      -H 'Content-Type: application/json' \
      -H 'Accept: application/json, text/plain, */*' \
      -H 'x-redlock-request-id: aaaaaaaaaaaa91548' \
      -H 'sec-ch-ua-platform: "Android"' \
      -H 'Origin: '"http://${SERVER_IP}/" \
      -H 'Sec-Fetch-Site: same-site' \
      -H 'Sec-Fetch-Mode: cors' \
      -H 'Sec-Fetch-Dest: empty' \
      -H 'Referer: '"http://${SERVER_IP}/" \
      -H 'Accept-Language: en-US,en;q=0.9' \
      --compressed

      # Successful download done.
      exit 0
  fi
  echo "Waiting to retry download"
  sleep 10
done
