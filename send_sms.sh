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
MSG="/tmp/sms_sent"

# hostname > $MSGBODY
# echo Aint got time for this >> $MSGBODY

# if file exists and is not empty
if [ -s ${MSGBODY} ]; then
    # prepend hostname
    hostname > $MSG
    cat < $MSGBODY >> $MSG
    rm -f ${MSGBODY}
    # erase MSGBODY so it does not get resent
    # leave $MSG around for debugging
    
    curl > /dev/null --silent \
      -X POST https://api.twilio.com/2010-04-01/Accounts/$ACCOUNT_SID/Messages.json \
      --data-urlencode "From=${SENDER}" \
      --data-urlencode "To=+${RECIPIENT}" \
      --data-urlencode Body@${MSG} \
      -u $ACCOUNT_SID:$AUTH_TOKEN
fi

# Uncomment this and crontab email will be generated when nothing is wrong
#echo Nothing to send
exit 0

