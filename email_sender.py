import os
from os.path import basename
from googleapiclient.discovery import build
from apiclient import errors
from httplib2 import Http
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import mimetypes
import base64
from google.oauth2 import service_account
import platform

class email_sender:
    def prepare_email(recipients, foldername, titleName, password):
        tolist = recipients.split("|")[0]
        cclist = recipients.split("|")[1]
        attachments = []
        message_body = ""
        passwordMode = False
        if password is None or password == "":
            print("No attachments")
            message_body = "<p>Hello again.</p><p>The latest orders for " + titleName + " have been uploaded via FTP.</p>"
        else:     
            passwordMode = True
            message_body = "<p>Hello again.</p><p>Please find attached the latest orders for " + titleName + ".</p>"
            for fileName in os.listdir(foldername):
                print("Checking for Zip: " + fileName)
                if (".zip" in fileName):
                    print("Found zip file: " + fileName)
                    attachments.append(foldername + "/" + fileName)
        for fileName2 in os.listdir(foldername):
           print("Checking for HTML: " + fileName2)
           if (".html" in fileName2):
            print("Found HTML file: " + fileName2)
            message_body = message_body + "<p>The pivots are as follows:</p>"
            f = open(foldername + "/" + fileName2, 'r')
            file_contents = f.read()
            message_body = file_contents.replace('"<','<').replace('>"','>').replace("PivotTable", message_body)
        message_body = message_body + "<p>Kind regards,</p><p>Fulfilment team</p>"
        # Call the Gmail API
        EMAIL_FROM =  'fulfilment@m-t.io' #sender
        EMAIL_SUBJECT = "Aditus Orders - " + titleName
        service = service_account_login(EMAIL_FROM)
        message = create_message_with_attachment(EMAIL_FROM, tolist, cclist, EMAIL_SUBJECT, message_body, attachments)
        send_message(service, EMAIL_FROM, message)
        #create_draft(service,EMAIL_FROM, message)

        if passwordMode == True:
            print("Preparing password send")
            EMAIL_SUBJECT2 = "Password"
            message_body2 = "<p>Hello again.</p><p>The password is:</p><p><i>" + password + "</i></p><p>Kind regards</p><p>Fulfilment team</p>"
            message2 = create_message_with_attachment(EMAIL_FROM, tolist, cclist, EMAIL_SUBJECT2, message_body2, [])
            send_message(service, EMAIL_FROM, message2)

            

def create_message_with_attachment(
    sender, to, cc, subject, message_text, files):
  message = MIMEMultipart()
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  message['cc'] = cc
  body = MIMEText(message_text, 'html')

  message.attach(body) # attach it to your main message

  for f in files:
    with open(f, "rb") as file:
        part = MIMEApplication(
                file.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        message.attach(part)
  try:
      filename = os.path.basename(files[0])
      message.add_header('Content-Disposition', 'attachment', filename=filename)
  except Exception as e:
       print("No attachment to add: " + str(e))
  return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

def send_message(service, user_id, message): #Sending message
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  except Exception as e:
    print('An error occurred: ' + str(e))


def send_error_message(type, option, error):
    emailaddress = 'fulfilment@m-t.io'
    service = service_account_login(emailaddress)
    message = create_message_with_attachment(emailaddress, "stefan@m-t.io", "gemma@m-t.io", "Error with " + type + " in " + option, ". Error is: " + str(error), [])
    send_message(service, emailaddress, message)


def create_draft(service, user_id, message): #Drafting message #service.users().drafts().create
  try:
       draft = (service.users().drafts().create(userId=user_id, body=message)
               .execute())
       print('Draft id: %s\nDraft message: %s' % (draft['id'], draft['message']))
       return draft
  except Exception as e:
        print('An error occurred: ' + str(e))
        return None


def service_account_login(EMAIL_FROM):
  SCOPES = ['https://www.googleapis.com/auth/gmail.send']
  if (platform.system() == 'Windows'):
    SERVICE_ACCOUNT_FILE = "C:\\Users\\Stefan\\Downloads\\keys\\gmailkey.json" #temp
  else:
    SERVICE_ACCOUNT_FILE = "gmailkey.json"
  credentials = service_account.Credentials.from_service_account_file(
          SERVICE_ACCOUNT_FILE, scopes=SCOPES)
  delegated_credentials = credentials.with_subject(EMAIL_FROM)
  service = build('gmail', 'v1', credentials=delegated_credentials)
  return service




