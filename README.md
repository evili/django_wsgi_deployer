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
##### `name`
The Name of the project or application to deploy (*mandatory*)
##### `src`
The URL of the source code of the project (*mandatory*).
##### `scm`
The source code management used (`svn` or `git` for the moment).
_Default_: `'svn'`.
##### `dst`
Destination directory.
##### `settings`
Settings module name.
_Default_: `name+'_production'`.
##### `url`
Relative URL where the project will be deployed
_Default_: `name`.
##### `build': 
Build script used to prepare your project (relative to the projects code base).
_Default_: `'build/build.sh'`.
##### `wsgi`:
WSGI script name.
_Default_:`'wsgi.py'`
##### `allowed_hosts`
Hosts allowed to run the deployed project.
_Default_: `os.environ['HTTPD_HOST']`
##### `secret_key`
Secret key to use as SECRET_KEY in django settings.
_Default_: Automatically generated on deploy.
##### `media_root`
Where your media files will be stored.
_Default_: `os.path.join(HTTPD_MEDIA_BASE, name),`
##### `static_root`
Where your static files will be collected
_Default_: `os.path.join(HTTPD_STATIC_BASE, name)`
##### `settings_append`
Additional settings that will go into the final `settings` module (tipically DATABASES definition, etc).
_Default_:

    LOGGING = {
      'version': 1,
      'disable_existing_loggers': False,
      'handlers': {
        'file': {
          'level': 'DEBUG',
          'class': 'logging.FileHandler',
          'filename': '/var/tmp/%(name)-wsgi.log',
        },
      },
      'loggers': {
        '': {
          'handlers': ['file'],
          'level': 'WARNING',
          'propagate': True,
        }
      }
    }
    


