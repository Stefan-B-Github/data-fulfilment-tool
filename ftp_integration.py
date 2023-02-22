import os
import platform
from ftplib import FTP, FTP_TLS
import ftp_scraper
import urllib.request
import paramiko
import openpyxl
import email_sender
import subprocess
import re
import time

SERVICE_ACCOUNT_FILE = ''
if (platform.system() == 'Windows'):
    RCN_KEY = "C:\\Users\\Stefan\\Downloads\\keys\\key.pem" #temp
else:
    RCN_KEY = "key.pem" ## MUST HAVE CHMOD 600

class ftp_integration:

    def prepare_ftp_send(ftp_mode, foldername):
        output = False
        try:
            if ftp_mode == 'RCN':
                output = ftp_integration.rcn_upload(foldername)
                return output
            elif ftp_mode == "Dogs":
                output = ftp_integration.dogs_upload(foldername)
                return output
            elif ftp_mode == "ABS":
                output = ftp_integration.abs_upload(foldername)
                return output
            elif ftp_mode == "DSB":
                output =  ftp_integration.scraper_upload(foldername, "DSB")
                return output
            elif ftp_mode == "Amaze":
                output =  ftp_integration.scraper_upload(foldername, "Amaze")
                return output
            elif ftp_mode == "Future":
                output =  ftp_integration.abs_upload_OLD(foldername)
                return output
            elif ftp_mode == "Future_Frees":
                output =  ftp_integration.future_frees(foldername)
                return output
            elif ftp_mode == "Life_Insurance":
                output =  ftp_integration.life_insurance(foldername)
                return output
            elif ftp_mode == "Investors":
                output =  ftp_integration.investors_upload(foldername)
                return output
        except Exception as e7:
            email_sender.send_error_message("FTP prepration", foldername, e7)
        return output

    def dogs_upload(foldername): #Dogs Trust
        command = "lftp -u user,pass1# -e 'cd \"Suppliers/Example\";put FILENAME;exit' ftps://example.ftp.com"
        if (platform.system() == 'Windows'):
            command = "bash " + command
        for name in os.listdir(foldername):
            localpath = os.path.join(foldername, name)
            if os.path.isfile(localpath):
                try:
                    print(localpath)
                    print(command.replace("FILENAME",localpath))
                    os.system(command.replace("FILENAME",localpath))
                    print("Success")
                    return True
                    break
                except Exception as e:
                    print("Error: " + str(e))
                    return False
        print("Error: no files")
        return False

  
    def abs_upload_OLD(foldername): #ABS OLD
            #This requires GCloud to be authenticated, so that the shell script in the container connects.
            print("Loading ABS File")
            filesToLoad = []
            outputs = ""
            for fileName in os.listdir(foldername):
                if ".txt" in fileName:
                    filesToLoad.append(fileName)
            for fileToLoad in filesToLoad:
                print("found: " + fileToLoad + " to load.")
                sshkey = "sshkey.txt" #local
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    ssh.connect('104.199.196.64', username='stefan', key_filename=sshkey)
                    sftp = ssh.open_sftp()
                    sftp.put(foldername + "/" + fileToLoad, '/home/stefan/' + fileToLoad)
                    time.sleep(1)
                    stdin, stdout, stderr = ssh.exec_command('./connect_to_abs.sh ' + fileToLoad)
                    time.sleep(1)
                    print("ran: " + str(stdout.readlines()))
                    time.sleep(1)
                    ssh.close()
                except Exception as p:
                    print("Error: " + str(p))
                    #email_sender.send_error_message("Future Upload", fileToLoad, p)
            print("Done")
            return True

    def abs_upload(foldername): #ABS
            print("Loading ABS File")
            filesToLoad = []
            for fileName in os.listdir(foldername):
                if ".txt" in fileName or ".csv" in fileName:
                    filesToLoad.append(fileName)
                    print("found: " + fileName + " to load.")
            outputs = ""
            for fileToLoad in filesToLoad:
                try:
                    print("Loading: " + fileToLoad)
                    fileToLoadRenamed = fileToLoad.replace(" ","_")
                    os.rename(foldername + "/" + fileToLoad, foldername + "/" + fileToLoadRenamed)
                    paramiko.util.log_to_file("paramiko.log")
                    host,port = "HOST",22
                    transport = paramiko.Transport((host,port))
                    username,password = "USER", "PASS"
                    transport.connect(None,username,password)
                    sftp = paramiko.SFTPClient.from_transport(transport)
                    localpath = foldername + "/" + fileToLoadRenamed
                    remotepath = "/" + fileToLoadRenamed
                    sftp.put(localpath, remotepath)
                    if sftp: sftp.close()
                    if transport: transport.close()
                except Exception as e:
                    email_sender.send_error_message("ABS Upload", foldername, e)
                    return False
            print("Success")
            return True

    def investors_upload(foldername): #CDS
            print("Loading Investors File")
            filesToLoad = []
            for fileName in os.listdir(foldername):
                if ".xls" in fileName:
                    filesToLoad.append(fileName)
                    print("found: " + fileName + " to load.")
            outputs = ""
            for fileToLoad in filesToLoad:
                try:
                    print("Loading: " + fileToLoad)
                    fileToLoadRenamed = fileToLoad.replace(" ","_")
                    os.rename(foldername + "/" + fileToLoad, foldername + "/" + fileToLoadRenamed)
                    host,port = "HOST",22
                    transport = paramiko.Transport((host,port))
                    username,password = "USER", "PASS"
                    transport.connect(None,username,password)
                    sftp = paramiko.SFTPClient.from_transport(transport)
                    localpath = foldername + "/" + fileToLoadRenamed
                    remotepath = "/Incoming/" + fileToLoadRenamed
                    sftp.put(localpath, remotepath)
                    if sftp: sftp.close()
                    if transport: transport.close()
                except Exception as e:
                    print("Problem: " + str(e))
                    return False
            print("Success")
            return True

    def rcn_upload(foldername): #RCN New
            print("Loading RCN File")
            fileToLoad = ""
            for fileName in os.listdir(foldername):
                if ".zip" in fileName:
                    print("found: " + fileName + " to load.")
                    fileToLoad = fileName
                    break
            fileToLoadRenamed = fileToLoad.replace(" ","_")
            os.rename(foldername + "/" + fileToLoad, foldername + "/" + fileToLoadRenamed)
            outputs = ""
            try:
                print("Loading: " + fileToLoadRenamed)
                paramiko.util.log_to_file("paramiko.log")
                host,port = "HOST",22
                transport = paramiko.Transport((host,port))
                username,password = "USER","PASS"
                transport.connect(None,username,password)
                sftp = paramiko.SFTPClient.from_transport(transport)
                localpath = foldername + "/" + fileToLoadRenamed
                remotepath = "/Upload/" + fileToLoadRenamed
                sftp.put(localpath, remotepath)
                if sftp: sftp.close()
                if transport: transport.close()
            except Exception as e:
                email_sender.send_error_message("RCN Upload", foldername, e)
                return False
            print("Success")
            return True


    def rcn_upload_OLD(foldername): #RCN OLD
        print("Loading RCN File")
        fileToLoad = ""
        for fileName in os.listdir(foldername):
            if ".zip" in fileName:
                print("found: " + fileName + " to load.")
                fileToLoad = fileName
                break
        fileToLoadRenamed = fileToLoad.replace(" ","_")
        os.rename(foldername + "/" + fileToLoad, foldername + "/" + fileToLoadRenamed)
        command = "sftp -i " + RCN_KEY + " example@sftp.host.com:local <<< $'put " + foldername +"/" + fileToLoadRenamed + "'"
        print("Command is: " + command)
        shellscript = "rcn.sh"
        f = open(shellscript, "w")
        f.write("#/bin/bash")
        f.write("\n")
        f.write(command)
        f.close()
        os.system("chmod +x " + shellscript)
        output = os.system("bash  ./" + shellscript)
        print("output is: " + str(output))
        os.remove(shellscript)
        if output == 0:
            print("Success")
            return True
        else:
            print("Failure")
            return False

    def scraper_upload(foldername, type): #Web scrapers
        print("Loading " + type + " File")
        fileToLoad = ""
        scraper_output = True
        for fileName in os.listdir(foldername):
            if ".xls" in fileName:
                print("found: " + fileName + " to load.")
                fileToLoad = fileName       
                fileToLoadRenamed = fileToLoad.replace(" ","_")
                scraper_output = ftp_scraper.ftp_scraper.sendfile(foldername, fileName, type)
                if scraper_output is False:
                    email_sender.send_error_message("type", foldername, "scraper error")
        return scraper_output

    def life_insurance(foldername): 
        fileToLoad = ''
        for fileName in os.listdir(foldername):
            if "NO EMAIL" not in fileName:
                print("found: " + fileName + " to load.")
                fileToLoad = fileName
                break
        index = 0
        file1 = open(foldername + "/" + fileToLoad, 'r')
        Lines = file1.readlines()
        for line in Lines:
            index = index + 1
            if index > 1:
                list = line.split(",")
                if len(list) < 6:
                    continue
                title = list[0].replace(" ","+")
                firstname = list[1].replace(" ","+")
                lastname = list[2].replace(" ","+")
                address1 = list[3].replace(" ","+")
                address2 = list[4].replace(" ","+")
                address3 = list[5].replace(" ","+")
                town = list[6].replace(" ","+")
                county = list[7].replace(" ","+")
                postcode = list[8].replace(" ","+")
                telephone = list[9].replace(" ","+")
                email = list[10].replace(" ","+")
                answer = list[11].replace(" ","+")
                mtref = '6220750528315392'
                url = "https://example.com/action?mtid=0&mtref=" + mtref  + "&firstname=" + firstname + "&lastname=" + lastname + "&address1=" + address1 + "&address2=" + address2 + "&address3=" + address3 + "&town=" + town + "&county=" + county + "&postcode=" + postcode + "&telephone=" + telephone + "&email=" + email + "&answer=" + answer 
                try:
                    mtrequest = urllib.request.urlopen(url).read()
                    print("curled: " + email)
                except Exception as e:
                    print("Error sending to MT: " + str(e))
                    return False
        print("Success")
        return True

    def future_frees(foldername): 
        fileToLoad = ''
        for fileName in os.listdir(foldername):
            if "NO EMAIL" not in fileName:
                print("found: " + fileName + " to load.")
                fileToLoad = fileName
                break
        index = 0
        file1 = open(foldername + "/" + fileToLoad, 'r')
        Lines = file1.readlines()
        for line in Lines:
            index = index + 1
            if index > 0:
                list = line.split(",")
                if len(list) < 6:
                    continue
                firstname = list[2].replace(" ","+")
                lastname = list[1].replace(" ","+")
                email = list[4].replace(" ","+")
                magtitle = list[5]
                mtref = '6280218131693568'
                if "deal" in magtitle:
                    print("sending option 1")
                    mtref = '6337646307180544'
                elif "week" in magtitle:
                    mtref = '5653747893665792'
                    print("sending option 2")
                elif "times" in magtitle:
                    print("sending option 3")
                    mtref = '6107913036365824'
                else:
                    print("sending option 4")
                url = "https://example.com/action?mtid=0&mtref=" + mtref + "&email=" + email + "&firstname=" + firstname + "&lastname=" + lastname
                try:
                    mtrequest = urllib.request.urlopen(url).read()
                    print("curled: " + email)
                except Exception as e:
                    print("Error sending to MT: " + str(e))
                    return False
        print("Success")
        return True

    def investors_download(foldername):
        host,port = "host",22
        transport = paramiko.Transport((host,port))
        username,password = "USER","PASS"
        transport.connect(None,username,password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        remotepath = "/Outgoing"
        for file in sftp.listdir(remotepath):
            print("Found: " + str(file))
            if 'ditus' in str(file) and '.csv' in str(file):
                sftp.get(remotepath + "/" + str(file), foldername + "/tempfile.csv")
                if sftp: sftp.close()
                if transport: transport.close()
                break
        try:
            tempfile = open(foldername + '/tempfile.csv', encoding="latin-1")
            print("Processing file")
            Lines = tempfile.readlines()
            customerArray = []
            for line in Lines:
                splitLine = line.split(",")
                try:
                    checkerLine = str(splitLine[10] + splitLine[18]).upper().replace(" ","").replace('"','')
                    customerArray.append(checkerLine)
                except Exception as e5:
                    continue
            os.remove(foldername + '/tempfile.csv')
            print("done! " + customerArray[5] +"," + customerArray[10])
            return customerArray
        except Exception as e4:
            email_sender.send_error_message("Investors Download", foldername, e4)
        return []


 