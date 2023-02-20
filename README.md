# FSND_Linux_Server_Config
This repo is used to complete the linux server configuration project for the Udacity Full Stack Nanodegree.

## Project Requirements

### User Management

| Criteria | Meets Specifications |
|----------|----------------------|
| Are users prompted for their password at least once when using sudo commands? | sudo commands prompt for user password at least once. |
| Is remote login of the root user disabled? | Remote login of the root user has been disabled. |
| Is a remote user given sudo access? | A remote user is given sudo access. |
| Do users have good/secure passwords? | Users have good/secure passwords. |

### Security

| Criteria | Meets Specifications |
|----------|----------------------|
| Is the firewall configured to only allow for SSH, HTTP, and NTP? | Only allow connections for SSH (port 2200), HTTP (port 80), and NTP (port 123). |
| Are users required to authenticate using RSA keys? | Key-based SSH authentication is enforced. |
| Are the applications up-to-date? | Applications have been updated to most recent updates. |
| Is SSH hosted on non-default port? | SSH is hosted on non-default port. |

### Application Functionality

| Criteria | Meets Specifications |
|----------|----------------------|
| Has the database server been configured to properly serve data? | Database server has been configured to serve data (postresql is recommended). |
| Can the VM (AWS Server) be remotely logged into? | VM can be remotely logged into. |
| Has the web-server been configured to serve the Item Catalog application? | Web-server has been configured to serve the Item Catalog application as a wsgi app. |

### Documentation

| Criteria | Meets Specifications |
|----------|----------------------|
| Is a README file included in the GitHub repo containing all specified information? | A README file is included in the GitHub repo containing the following information: IP address, URL, summary of software installed, summary of configurations made, and a list of third-party resources used to completed this project. |

## Project Documentation

We are deploying a flask application on to AWS Light Sail.  This document will give you steps that I used in creating the instance.

### IP Address

IP address: 34.205.85.140
Port: 2200

### URL

[restaurant database](http://34.205.85.140/venuefinder/)

### Software Installed



### Configuration steps


Please view this [github](https://) to use the application

## Creating your LightSail Instance for ubuntu

1. Login into [AWS Light Sail](https://lightsail.aws.amazon.com) using your provided email and password to amazon

2. Once you are login into the site, there is a button called create Instance. Click that button.
![Create Instance](/README_images/create_instance.png)

3. You'll be given two options: App+OS, OS only.
![Create Instance Image](/README_images/create_instance_image.png)

4. Choose OS only and ubuntu

![OS Only](/README_images/os_only.png)

5. Choose the instance plan and then click the button

![Choose Instance Plan](/README_images/choose_instance_plan.png)

You can name your instance or just leave the default name provided by AWS .  They give an option to change the instance name.

Once we have created our ubuntu image, now we need to start configuring the server to deploy our flask application.

## Accessing the instance

Before setting up the server, we need to download the lightsail pem file from the LightSail website.  In order to get the file, you need to go the accounts page.
Once you are in the accounts page, there is an option to download the default private key.

![Light Sail Private Key](/README_images/lightsail_private_key.png)

To see if you can login into instance. Two things need to be done:

1. You need to change permission of the downloaded lightsail private key.
`chmod 400 LightsailDefaultPrivateKey.pem` or `chmod 600 LightsailDefaultPrivateKey.pem`

2. To login:
`ssh user@PublicIP -i LightsailDefaultPrivateKey`

**Please make sure your private key is the same directory. The default port for SSH is 22 but we'll change it later on to meet nanodegree requirements.**

To check your PublicIP, LightSail has manage option on the instance. Click the icon that has 3 dots

![Three Dot Icon](/README_images/threedoticon.png)

Click the manage option.  You'll go to a screen looking this:

Management Console

![Management Console](/README_images/managementconsole.png)

Once you are able to access the instance, lets update our system and then create our new user.

## Updating the server
Since you are running ubuntu, its only two commands:

```
sudo apt-get update
sudo apt-get upgrade
```

## Creating the New user with sudo permissions
You are login into the instance. Lets create a new user called grader:
```
sudo adduser grader
```
It will prompt for a password. Add any password to that field.
After the user gets created, run this command to give the grader sudo priviledges:
```
sudo visudo
```
Once your in the visudo file, go to the section user privilege specification
```
root    ALL=(ALL:ALL) ALL
```
You've noticed the root user in the file. You need add the grader user to same section.  It should look like this:
```
grader  ALL=(ALL:ALL) ALL
```
If you want to login into the account, check to see if works: `sudo login grader`.
We've created our new user, lets configure our ssh to non-default port

## Configuring SSH to a non-default port

SSH default port is 22. We want to configure it to non default port.  Since we are using LightSail, we need to open the non default port through the web interface. If you don't do this step, you'll be locked out of the instance. Go to the networking tab on the management console. Then, the firewall option

![LightSail firewall](/README_images/lightsailfirewall.png)

Go into your sshd config file: `sudo nano /etc/ssh/sshd_config`
Change the following options. # means commented out

```
# What ports, IPs and protocols we listen for
# Port 22
Port 2200

# Authentication:
LoginGraceTime 120
#PermitRootLogin prohibit-password
PermitRootLogin no
StrictModes yes

# Change to no to disable tunnelled clear text passwords
PasswordAuthentication No
```
Once these changes are made, restart ssh: `sudo service restart ssh`
Any user can login into the machine using a specify port: `sudo user@PublicIP -p 2200`
### Creating the ssh keys
```
LOCAL MACHINE:~$ ssh-keygen
```
Two things will happen:
1. You can name the file whatever you want.  Keep in mind when you name the file it will give you a private key and public key
2. It will prompt you for a pass phrase. You can enter one or leave it blank

Once the keys are generated, you'll need to login to the user account aka grader here:
You'll make a directory for ssh and store the public key in an authorized_keys files

```
mkdir .ssh
cd .ssh
```
When you are in the directory, create an authorized_keys file. This where you paste the public key that you generated on your local machine.
```
sudo nano authorized_keys
```
Please double check your path by pwd. You should be in your `/home/grader/.ssh/` when creating the file. You should be login with grader account using the private key from local machine into the server: `ssh user@PublicIP -i ~/.ssh/whateverfile_id_rsa`

## Configuring Firewall rules using UFW
We need to configure firewall rules using UFW. Check to see if ufw is active: `sudo ufw status`. If not active, lets add some rules
```
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2200/tcp
sudo ufw allow 80/tcp or sudo ufw allow www (either one of these commands will work)
sudo ufw allow 123/udp
```
Now, you enable the rules: `sudo ufw enable` and re check the status to see what rules are activity

## Configure timezone for server
```
sudo dpkg-reconfigure tzdata
```
Choose none of the above and choose UTC.  The server by default is on UTC.

## Install Apache, Git, and flask

### Apache
We will be installing apache on our server. To do that:

```
sudo apt-get install apache2
```
If apache was setup correctly, a welcome page will come up when you use the PublicIP. We are going to install mod wsgi, python setup tools, and python-dev
```
sudo apt-get install libapache2-mod-wsgi python-dev
```
We need to enable mod wsgi if it isn't enabled: `sudo a2enmod wsgi`

Let's setup wsgi file and sites-available conf file for our application.
Create the WSGI file in `path/to/the/application directory`
```
WSGI file

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/restaurant')

from project import app as application
application.secret_key='super_secret_key'
```
Please note project.py is my python file. Wherever you housed your application logic.

To setup a virtual host file: `cd /etc/apache2/sites-available/restaurant.conf`:
```
Virtual Host file
<VirtualHost *:80>
     ServerName  PublicIP
     ServerAdmin email address
     #Location of the restaurant WSGI file
     WSGIScriptAlias / /var/www/restaurant/restaurant.wsgi
     #Allow Apache to serve the WSGI app from our restaurant directory
     <Directory /var/www/restaurant>
          Order allow,deny
          Allow from all
     </Directory>
     #Allow Apache to deploy static content
     <Directory /var/www/restaurant/static>
        Order allow,deny
        Allow from all
     </Directory>
      ErrorLog ${APACHE_LOG_DIR}/error.log
      LogLevel warn
      CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

```
### Git
`sudo apt-get install git`

Clone repository into the apache directory. In the `cd /var/www`

```
mkdir itemsCatalog
cd /var/www/itemsCatalog

sudo git clone https://github.com/harushimo/fullstack-nanodegree-vm.git  itemsCatalog
```

### Flask
Do these commands:

```
sudo apt-get install python-pip python-flask python-sqlalchemy python-psycopg2
sudo pip install oauth2client requests httplib2
```

## Install PostGreSql
Install PostGreSql `sudo apt-get install postgresql`
To make sure remote are not allowed, please check the following configuration file: `sudo nano /etc/postgresql/9.5/main/pg_hba.conf`

### Create database
`sudo su - postgres`
Type in `psql` as postgres user

Do following the commands:
```
postgres=# CREATE USER restaurant WITH PASSWORD 'restaurant';
postgres=# ALTER USER restaurant CREATEDB;
postgres=# CREATE DATABASE restaurant WITH OWNER restaurant;
```
Connect to the catalog database: `\c restaurant`
```
catalog=# REVOKE ALL ON SCHEMA public FROM public;
catalog=# GRANT ALL ON SCHEMA public TO restaurant;
```
Exit postgres and postgres user
```
postgres=# \q
postgres@PublicIP~$ exit
```

We need to update our database setup and application python files to illustrate the new engine connection
`engine = create_engine('postgresql://restaurant:restaurant@localhost/restaurant')`

Run `sudo python database_setup.py`

## Oauth Client Login

To setup it up. Update the path in the application.py program. Update the client id and oauth_flow

```
CLIENT_ID = json.loads(
    open('/var/www/restaurant/client_secrets.json', 'r').read())['web']['client_id']

oauth_flow = flow_from_clientsecrets('/var/www/restaurant/client_secrets.json', scope='')
```


### Resources Used

1. [Setting Permissions for LightSail Pem file](http://unix.stackexchange.com/questions/115838/what-is-the-right-file-permission-for-a-pem-file-to-ssh-and-scp)
2. [Abhishek Ghosh](https://github.com/ghoshabhi/P5-Linux-Config)
3. [Digital Ocean setting VPS on ubuntu](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)
4. [Oauth Error on apache2](https://discussions.udacity.com/t/oauth-error-on-apache2-linux-server/235498/7)
5. [Cannot SSH into ports](https://discussions.udacity.com/t/cannot-ssh-after-changing-ports/224971/14)
6. [Abigail Matthews](https://github.com/AbigailMathews/FSND-P5)
7. [Steven Wooding](https://github.com/SteveWooding/fullstack-nanodegree-linux-server-config)
8. [Flask Config](http://flask.pocoo.org/docs/0.12/config/)

