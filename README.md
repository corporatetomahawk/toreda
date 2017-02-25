# Setting up Google App Engine
## Step 1:
	- [ ] Make sure MySQL is installed.
	- [ ] Download from: [MySQL :: Download MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
	- [ ] Install and start the server with:
            `sudo /usr/local/mysql/support-files/mysql.server start`


## Step 2:
	- [ ] Follow the instructions here: [Running Django on App Engine standard environment](https://cloud.google.com/python/django/appengine)
	- [ ] Then install the cloud sql proxy
	- [ ] `sudo /usr/local/mysql/support-files/mysql.server stop` to stop server if necessary.
	- [ ] [Google Application Default Credentials](https://developers.google.com/identity/protocols/application-default-credentials) Possibly create credentials as outlined here.

1. Create new project.
2. Navigate to  [Google Application Default Credentials](https://developers.google.com/identity/protocols/application-default-credentials) and create credentials names cloud-services with Cloud SQL Editor privileges.
3. Run `gcloud auth application-default login`to login.
4. Clone toreda repository `git clone …..`
5. Follow instructions to set up proxy here: [Running Django on App Engine standard environment](https://cloud.google.com/python/django/appengine)
6. Run `gcloud init` and verify the default settings are correct.
7. `sudo /usr/local/mysql/support-files/mysql.server stop` to stop server if necessary.
8. Start the proxy: `./cloud_sql_proxy -instances='atai-toreda:us-central1:polls-instance'=tcp:3306`
9. Connect to the proxy: `mysql -h 127.0.0.1 -u root -p` 
10. Run `python manage.py runserver`to check local connection.

[mac OS X - MySQL server PID file could not be found - Server Fault](http://serverfault.com/questions/480889/mysql-server-pid-file-could-not-be-found)

## Static Files
[google app engine - How to use static files with django nonrel - Stack Overflow](http://stackoverflow.com/questions/7779683/how-to-use-static-files-with-django-nonrel)