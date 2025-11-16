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
In vm, create /etc/systemd/system/flaskapp.service:
"
[Unit]
Description=Flask App
After=network.target

[Service]
User=David
WorkingDirectory=/home/David/projectapp
Environment="PATH=/home/David/projectapp/venv/bin"
Environment="DB_HOST=groupmysql.mysql.database.azure.com"
Environment="DB_USER=groupmysql"
Environment="DB_PASSWORD=Abc123456789"
Environment="DB_NAME=groupdatabase"
Environment="DB_PORT=3306"
Environment="SSL_CA=/home/groupvm/DigiCertGlobalRootG2.crt.pem"
Environment="AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=groupblob;AccountKey=Xc0LDYPWjFwJukTt8OE6UfanHi5aZfbQXqDxgeYv+hABJnOPffe5qOihjkKEzmXQ2kCuZsMGhcFX+AStVcvGSQ==;EndpointSuffix=core.windows.net"
Environment="FLASK_SECRET_KEY=mysupersecretkey"
ExecStart=/home/David/projectapp/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
"

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


## My VM history
David@testvmapp:~$ history
    1  sudo apt update
    2  ssh-keygen -t rsa -b 4096 -C "DavidLivm"
    3  cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
    4  chmod 600 ~/.ssh/authorized_keys
    5  cat ~/.ssh/authorized_keys
    6  sudo journalctl -u ssh
    7  ssh -i ~/.ssh/id_rsa David@4.233.76.170
    8  cat ~/.ssh/id_rsa
    9  ls -a
   10  chmod 700 ~/.ssh
   11  chmod 600 ~/.ssh/authorized_keys
   12  sudo nano /etc/ssh/sshd_config
   13  cat /etc/ssh/sshd_config
   14  sudo nano /etc/ssh/sshd_config
   15  cat /etc/ssh/sshd_config
   16  chmod 700 ~/.ssh
   17  chmod 600 ~/.ssh/authorized_keys
   18  ls -ld ~/.ssh
   19  ls -l ~/.ssh/authorized_keys
   20  sudo systemctl restart ssh
   21  cd projectapp/
   22  ls -a
   23  python3 -m venv venv
   24  source venv/bin/activate
   25  pip install -r requirements.txt
   26  sudo apt update
   27  sudo apt install python3.10-venv -y
   28  pip install -r requirements.txt
   29  sudo apt install python3-pip -y
   30  sudo apt install python3-venv -y
   31  python3 -m venv venv
   32  source venv/bin/activate
   33  pip install -r requirements.txt
   34  flask run --host=0.0.0.0 --port=5000
   35  export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=xxxx;AccountKey=xxxx;EndpointSuffix=core.windows.net"
   36  sudo systemctl daemon-reload
   37  sudo systemctl restart flaskapp
   38  sudo nano /etc/systemd/system/flaskapp.service
   39  sudo systemctl daemon-reload
   40  sudo systemctl start flaskapp
   41  sudo systemctl status flaskapp
   42  journalctl -u flaskapp -n 50 --no-pager
   43  sudo nano /etc/systemd/system/flaskapp.service
   44  sudo systemctl daemon-reload
   45  sudo systemctl status flaskapp
   46  journalctl -u flaskapp -n 50 --no-pager
   47  sudo nano /etc/systemd/system/flaskapp.service
   48  sudo systemctl daemon-reload
   49  systemctl show -p Environment flaskapp
   50  systemctl show flaskapp | grep Environment
   51  nano --version
   52  nano ~/projectapp/.env
   53  sudo nano /etc/systemd/system/flaskapp.service
   54  sudo systemctl daemon-reload
   55  systemctl show flaskapp -p Environment --no-pager
   56  cd ~/projectapp
   57  source venv/bin/activate
   58  export $(grep -v '^#' .env | xargs)
   59  flask run --host=0.0.0.0 --port=5000
   60  cd ~/projectapp
   61  git remote -v
   62  nano app.py
   63  nano templates/login.html
   64  flask run --host=0.0.0.0 --port=5000
   65  nano app.py
   66  git add .
   67  git commit -m "修改说明"
   68  git push origin main
   69  git remote set-url origin git@github.com:DavidLi2465/vmflaskapp.git
   70  git push origin main
   71  ssh-keygen -t ed25519 -C "keyvm"
   72  cat ~/.ssh/id_ed25519.pub
   73  ssh -T git@github.com
   74  git push origin main
   75  git remote -v
   76  cd ~/projectapp
   77  git remote set-url origin git@github.com:DavidLi2465/vmflaskapp.git
   78  ssh -T git@github.com
   79  git push origin main
   80  nano app.py
   81  git push origin main
   82  git add .
   83  git commit -m "change app.py"
   84  git push origin main
   85  git fetch origin
   86  git status
   87  git remote -v
   88  git remote set-url origin git@github.com:DavidLi2465/vmflaskapp.git
   89  git remote -v
   90  ssh -T git@github.com
   91  git fetch origin
   92  git pull origin main
   93  git log --oneline --graph --decorate -n 5
   94  git fetch origin
   95  git diff origin/main
   96  nano app.py
   97  git status
   98  git add app.py
   99  git commit -m "update app.py"
  100  git push origin main
  101  flask run --host=0.0.0.0 --port=5000
  102  nano app.py
  103  git add app.py
  104  git commit -m "update app.py"
  105  git push origin main
  106  git remote set-url origin git@github.com:DavidLi2465/vmflaskapp.git
  107  ssh -T git@github.com
  108  git push origin main
  109  nano app.py
  110  cd ~/projectapp
  111  source venv/bin/activate
  112  flask run --host=0.0.0.0 --port=5000
  113  export $(grep -v '^#' .env | xargs)
  114  flask run --host=0.0.0.0 --port=5000
  115  sudo systemctl status flaskapp
  116  sudo systemctl enable flaskapp
  117  sudo systemctl start flaskapp
  118  sudo systemctl status flaskapp
  119  sudo nano /etc/systemd/system/flaskapp.service
  120  sudo systemctl daemon-reload
  121  flask run --host=0.0.0.0 --port=5000
  122  ps aux | grep flask
  123  sudo journalctl -u flaskapp -f
  124  cd ~/projectapp
  125  source venv/bin/activate
  126  export $(grep -v '^#' .env | xargs)
  127  flask run --host=0.0.0.0 --port=5000
  128  ps aux | grep flask
  129  cd ~/projectapp
  130  source venv/bin/activate
  131  export $(grep -v '^#' .env | xargs)
  132  ps aux | grep flask
  133  apt list --installed
  134  dpkg --get-selections | grep -v deinstall
  135  pip list
  136  pip show Pillow
  137  cd ~/projectapp
  138  source venv/bin/activate
  139  export $(grep -v '^#' .env | xargs)
  140  flask run --host=0.0.0.0 --port=5000
  141  cat compress.log
  142  crontab -l
  143  ls
  144  sudo apt-get update
  145  sudo apt-get install cron -y
  146  sudo systemctl enable cron
  147  sudo systemctl start cron
  148  sudo systemctl status cron
  149  crontab -e
  150  cat ~/projectapp/compress.log
  151  nano compress.log
  152  crontab -l
  153  tail -f ~/projectapp/compress.log
  154  tail -n 20 ~/projectapp/compress.log
  155  cat ~/projectapp/compress.log
  156  flask run --host=0.0.0.0 --port=5000
  157  cat .env
  158  flask run --host=0.0.0.0 --port=5000
  159  ls -a
  160  cd projectapp/
  161  ls -a
  162  history
  163  history | grep git
  164  git remote -v
  165  cat /etc/systemd/system/flaskapp.service
  166  sudo systemctl status flaskapp
  167  sudo journalctl -u flaskapp -n 30 --no-pager
  168  sudo cat /etc/systemd/system/flaskapp.service
  169  cat ~/.ssh/authorized_keys
  170  whoami
  171  cat ~/.ssh/authorized_keys
  172  ssh-keygen -y -f ~/.ssh/id_rsa
  173  ls -l ~/.ssh/
  174  cat ~/.ssh/id_rsa
  175  sudo systemctl status ssh
  176  sudo nano /etc/ssh/sshd_config
  177  sudo systemctl restart ssh
  178  sudo nano /etc/ssh/sshd_config
  179  sudo systemctl status ssh
  180  sudo cat /etc/ssh/sshd_config | grep PubkeyAcceptedAlgorithms
  181  cd projectapp/
  182  source venv/bin/activate
  183  python app.py
  184  sudo lsof -i :5000
  185  sudo systemctl restart flaskapp
  186  sudo systemctl status flaskapp
  187  history
  188  sudo nano /etc/ssh/sshd_config
  189  sudo cat /etc/ssh/sshd_config
  190  history
  191  sudo systemctl status flaskapp
  192  cd projectapp/
  193  sudo systemctl status flaskapp
  194  cat /etc/systemd/system/flaskapp.service
  195  ps aux | grep flask
  196  systemctl status flaskapp.service
  197  cd projectapp/
  198  ls -a
  199  tail -f ~/projectapp/compress.log
  200  sudo systemctl status flaskapp
  201  cat /etc/systemd/system/flaskapp.service