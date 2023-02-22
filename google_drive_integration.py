from oauth2client.service_account import ServiceAccountCredentials
import os
import platform
import pydrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import calendar
from datetime import datetime, timezone

SERVICE_ACCOUNT_FILE = ''
if (platform.system() == 'Windows'):
    SERVICE_ACCOUNT_FILE = "C:\\Users\\Stefan\\Downloads\\keys\\drivekey.json" #temp
else:
    SERVICE_ACCOUNT_FILE = "drivekey.json"

gauth = GoogleAuth()
scope = ['https://www.googleapis.com/auth/drive']
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
drive = GoogleDrive(gauth)

class google_drive_integration:

    baseFolderId = '1qn6xiroQGv6UE3UqoxCmMiXZ6jydgb_h'  #Folder to use. Share with driveaccess@tech-essence.iam.gserviceaccount.com beforehand.


    def make_folder(foldername, subfolderID):
        f = drive.CreateFile({'title': foldername, 
        "parents":  [{"id": subfolderID}], 
        "mimeType": "application/vnd.google-apps.folder"})
        f.Upload()

    def list_folders(folderId):
        f = drive.ListFile({"q": "'"+ folderId +"' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
        return f

    def is_folder_in_location(folderName, folderToCheck):
        folderList = []
        for f in google_drive_integration.list_folders(folderToCheck):
            folderList.append(f['title'])
        if folderName in folderList:
            return True
        else:
            print("No folder found.")
            return False

    def load_file(folderId, filePath, fileName):
        f = drive.CreateFile({
        'title': fileName,
        'parents': [{
            'id': folderId
            }]
        })
        f.SetContentFile(filePath)
        f.Upload()

    def get_id_of_folder(folderName, baseId):
        if google_drive_integration.is_folder_in_location(folderName, baseId):
            for f in google_drive_integration.list_folders(baseId):
                if folderName == f['title']:
                    print("Found folder ID: " + f['id'])
                    return f['id']
            return "No file"
        else:
            return "No folder"


    def perform_upload(folder, optionfoldername):
        
        monthfoldername = datetime.now(timezone.utc).strftime('%B %Y')
        dayfoldername = datetime.now(timezone.utc).strftime('%d%m%y')

        print("Checking Month Folder")

        if google_drive_integration.is_folder_in_location(monthfoldername,google_drive_integration.baseFolderId) == False:
            google_drive_integration.make_folder(monthfoldername, google_drive_integration.baseFolderId)
            print("Month Folder Made")
        else:
            print("Month Folder exists")

        monthfolderid = google_drive_integration.get_id_of_folder(monthfoldername,google_drive_integration.baseFolderId)

        print("trying to make Day Folder")

        if google_drive_integration.is_folder_in_location(dayfoldername, monthfolderid) == False:
            google_drive_integration.make_folder(dayfoldername, monthfolderid)
            print("Day folder made")
        else:
            print("Day folder already exists")

        dayfolderid = google_drive_integration.get_id_of_folder(dayfoldername,monthfolderid)

        if google_drive_integration.is_folder_in_location(optionfoldername, dayfolderid) == False:
            google_drive_integration.make_folder(optionfoldername, dayfolderid)
            print("Option Folder Made")
        else:
            print("Option Folder already exists")

        optionfolderid = google_drive_integration.get_id_of_folder(optionfoldername,dayfolderid)

        print("Loading Files from " + folder)
        for fileName in os.listdir(folder):  
            print("Found file: " + fileName)
            google_drive_integration.load_file(optionfolderid,folder + "/" + fileName,fileName)
        print("Files Loaded")




  