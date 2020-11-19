import os
from twilio.rest import Client

class SendNotification(object):

    def __init__(self):
        account_sid = os.environ['ACCOUNT_SID']
        auth_token  = os.environ['AUTH_TOKEN']
        self.client = Client(account_sid, auth_token)
        return

    def send(self, message):
        service_sid = os.environ['MESSAGING_SID']
        recipient   = os.environ['RECIPIENT']
        return self.client.messages.create(
            body=message,
            messaging_service_sid=service_sid,
            to=recipient,
        )

if __name__ == "__main__":

    sms = SendNotification()
    response = sms.send('This is a short pithy message.')
    print(response)
