django_deployer
===============

Django Projects Deployer tries to automate deploying of Django projects/apps into an
existing Apache/WSGI server.

You should prepare your apache httpd to serve WSGI scripts from a certain directory (default: /var/www/wsgi).
Then you could edit a config file like this:

    [deploy]
    name = myproject
    src = http://source/of/your/repo/myproject
    scm = svn


Quick Usage
-----------
    # only the first time
    pip install django_deployer
    # where the wsgi scripts are served
    cd /var/www/wsgi
    # edit config (see below)
    vim myproject.conf
    # deploy
    djdeploy.py myproject
    # reload apache
    systemctl reload httpd


Available config keywords
-------------------------

###### `name`
The Name of the project or application to deploy (*mandatory*)

###### `src`
The URL of the source code of the project (*mandatory*).

###### `scm`
The source code management used (`svn` or `git` for the moment).
_Default `svn`_.
