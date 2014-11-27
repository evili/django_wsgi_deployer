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
<dl>
<dt>name</dt>
<dd>The Name of the project or application to deploy (_mandatory_).</dd>
<dt>src</dt>
<dd>The URL of the source code of the project (_mandatory_).</dd>
<dt>scm</dt>
<dd>The source code management used (`svn` or `git` for the moment).<br/>_Default `svn`_.</dd>
</dl>
