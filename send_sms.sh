#!/bin/bash
#
#   Write some output from a file to an SMS message.
#   So in my case from a crontab I do this
#
#   cd THISFOLDER && ./my_script.py 1>/dev/null 2>/tmp/sms_message && ./send_sms.sh
#
#   Run the python script and throw away its normal yackity output
#   Save the error messages to a file
#
#   If the file is not empty, then send it via SMS
#
#  Sample crontab entry:
#  # Test redirecting STDERR to an SMS text message and STDOUT to a file
#   * * * * * cd /home/bwilson/corona_collector && ./test.py 2>/tmp/sms_message || ./send_sms.sh
#
source .env

MSGBODY="/tmp/sms_message"

# date > $MSGBODY
# echo Aint got time for this >> $MSGBODY

# if file exists and is not empty
if [ -s ${MSGBODY} ]; then

    curl > /dev/null --silent \
      -X POST https://api.twilio.com/2010-04-01/Accounts/$ACCOUNT_SID/Messages.json \
      --data-urlencode "From=${SENDER}" \
      --data-urlencode "To=+${RECIPIENT}" \
      --data-urlencode Body@${MSGBODY} \
      -u $ACCOUNT_SID:$AUTH_TOKEN

    rm -f ${MSGBODY}
fi

# Uncomment this and crontab email will be generated when nothing is wrong
#echo Nothing to send
exit 0

