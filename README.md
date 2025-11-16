# Flask App Deployment Guide

## Project Overview
This project is a Flask web application that supports user registration, login, and file upload.  
It uses Azure MySQL Database and Azure Blob Storage for backend services.  
Deployment is automated with GitHub Actions (CI/CD), while systemd manages the Flask service and cron runs scheduled tasks every two minutes.

---

## Tech Stack
1. Python 3 and Flask  
2. Azure MySQL  
3. Azure Blob Storage  
4. GitHub Actions (CI/CD)  
5. systemd  
6. cron  

---

## File Structure
1. app.py , a Flask main program.
2. requirements.txt , a dependencies to install in iaas vm.
3. templates/  , a Frontend HTML templates folder include login, register and index.
4. compress.py is a scheduled task script to compress all picture to upload to Thumbnail Blob.
5. .env a environment variables which need to nano create in vm.
6. DigiCertGlobalRootG2.crt.pem ,a database SSL certificate.
7. .github/workflows/deploy.yml ,an CI/CD configuration
8. flaskapp.service – systemd service configuration file, used to run the Flask application in the background on the VM and automatically restart it after code updates.
9. .env required variables:
     1 DB_HOST – MySQL host address 
     2 DB_USER – MySQL username 
     3 DB_PASSWORD – MySQL password 
     4 DB_NAME – Database name 
     5 DB_PORT – MySQL port 
     6 SSL_CA – Path to SSL certificate 
     7 AZURE_STORAGE_CONNECTION_STRING – Azure Blob connection string
     8 FLASK_SECRET_KEY – Flask session key 
10. flaskapp.service Key sections:
     1 [Unit] – Service description and dependencies
     2 [Service] –
     3 User – VM username 
     4 Environment – Environment variables (same as .env values)
     5 ExecStart – Command to start Flask app
     6 Restart=always , Ensures service restarts automatically if it fails
     7 [Install] – Target for enabling service 

## SSH Setup and GitHub Secrets

### Generate and Configure SSH Key on VM

vm linux instruct:
"
ssh-keygen -t rsa -b 4096 -C "vm-deploy-key"
cat ~/.ssh/id_rsa.pub
"

Add the public key to:
"
nano ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
"

---

### Update SSH Configuration
Edit:
"
sudo nano /etc/ssh/sshd_config
"

Ensure the settings inside config are:
"
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
KbdInteractiveAuthentication no
PubkeyAcceptedAlgorithms +ssh-rsa
"

Now restart SSH:
"
sudo systemctl restart ssh
"

### Configure GitHub Secrets
In GitHub repository , Settings , Secrets and variables , Actions , New repository secret, add:

VM_HOST = VM public IP(4.233.76.170)
VM_USER = VM login username (David)
VM_SSH_KEY = VM private key (~/.ssh/id_rsa content)

VM private key can be found in vm , please edit:
"
cat ~/.ssh/id_rsa
"

Copy the VM private key from -----BEGIN OPENSSH PRIVATE KEY----- to -----END OPENSSH PRIVATE KEY-----,and paste it to VM_SSH_KEY value.
After these secrets are configured, GitHub Actions will automatically connect to your VM using the values above. Based on the instructions in .github/workflows/deploy.yml, every time you push changes to the repository, the workflow will run and deploy the updated code to your VM. This means deployment is fully automated: you only need to commit and push your changes, and GitHub Actions will handle the rest.

---

## Initial Code Deployment
Before setting up the environment, you need to deploy the code to your VM for the first time:
"
git clone https://github.com/DavidLi2465/vmflaskapp projectapp
cd projectapp
"
This is a one-time setup. After this initial deployment, all subsequent code updates will be handled automatically by GitHub Actions CI/CD.

---

## Environment Preparation
On VM:
"
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv cron -y
"

Initialize virtual environment:
"
cd ~/projectapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
"

Create .env file in vm. Copy the code from .env in zip folder and paste it in vm's .env.

---

## systemd Service Configuration
The flaskapp.service file is included as an example systemd configuration. In actual deployment, copy it to /etc/systemd/system/ on the VM and replace environment variable values with real credentials.
In vm, create /etc/systemd/system/flaskapp.service:
"
sudo nano /etc/systemd/system/flaskapp.service
"

copy and paste the code in Flaskapp services

Enable and start:
"
sudo systemctl daemon-reload
sudo systemctl enable flaskapp
sudo systemctl start flaskapp
sudo systemctl status flaskapp
"

The Flask app remains running at all times, even if you close the SSH session or reboot the VM.
When new code is pushed to GitHub, GitHub Actions automatically deploys the changes to the VM according to the .github/workflows/deploy.yml file.
After deployment, the workflow restarts the flaskapp service, ensuring the application is always running and updated to the latest version.

---

## cron Job Configuration
Edit crontab:
"
crontab -e
"

Choose:
"
1
"

Add:
"
*/2 * * * * /home/David/projectapp/venv/bin/python /home/David/projectapp/compress.py >> /home/David/projectapp/compress.log 2>&1
"
Now compress.py would be run to compress the picture and generate the information each 2 minutes.

## Live Web Application
Live Application: http://4.233.76.170:5000/register
