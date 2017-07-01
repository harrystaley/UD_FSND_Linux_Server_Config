# FSND_Item_Catalog
This project utilizes Flask, SQL Alchemy, JQUERY, CSS, Java Script, and OAUTH 2 to create an Item catalog website.

# Dependencies
1. Virtual Box
2. Vagrant
3. vagrant image with the following installed
  * Python 2.7
  * Flask
  * git

# setting up OAuth2.0
you will need to sign up for a google account and set up a client id and secret.

Visit: [http://console.developers.google.com](http://console.developers.google.com)

# setting up the enviornment.
1. clone this repo to '<Virtual Box VM Folder>/vagrant/restaurant' folder.
2. Run 'python db_setup.py'
3. Run 'python lotsofmenus.py'
4. Run 'python project.py'
5. Open your web browser and visit [http://localhost:5000](http://localhost:5000)
6. The applications main page will open and you will need to click on login and then use Google+ or Facebook to login.