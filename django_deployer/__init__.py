#!/usr/bin/env python
"""
 Deploy Django Applications into HTTPD Wsgi Container
"""
from __future__ import print_function

import os
import sys
import subprocess
import virtualenv
import re
import platform
import logging

from ConfigParser import SafeConfigParser
from lockfile import LockFile

logger = logging.getLogger(__name__)

SCM_DEFAULT_CHECKOUT = {
    'svn': 'co',
    'git': 'clone',
    'hg': 'clone',
}

CFG_SECTION = 'deploy'

WSGI_TEMPLATE = """
import os
import sys

_BASE_DIR = os.path.dirname(__file__)

# Add local paths
sys.path.insert(0, _BASE_DIR)
sys.path.insert(1, os.path.join(_BASE_DIR, '%(dst)s'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%(settings)s")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
"""

DJANGO_SETTINGS_TEMPLATE = """
from %(name)s.settings import *

DEBUG=False
TEMPLATE_DEBUG=DEBUG

ALLOWED_HOSTS = ['%(allowed_hosts)s']
SECRET_KEY='%(secret_key)s'

MEDIA_ROOT='%(media_root)s'
STATIC_ROOT='%(static_root)s'

%(settings_append)s

"""

HTTPD_CONF_TEMPLATE = """
WSGIDaemonProcess %(name)s processes=1 threads=4 display-name=%%{GROUP} python-path=%(site_libs)s umask=002
<Directory %(app_base)s>
WSGIProcessGroup %(name)s
</Directory>
WSGIScriptAlias %(url)s %(app_base)s/%(wsgi)s
"""

WSGI_PYTHON_PATH = u'^%s.*site-packages$'

def deploy_django_app(app):
    """
    Deploy a Django application
    """


    # logger.debug('ENVIRONMENT:')
    # for k in ('WSGI_BASE_PATH', 'HTTPD_CONF_DIR',):
    #     logger.debug('  %s=%s', k, os.environ.get(k, None))

    WSGI_BASE_PATH = os.environ.get('WSGI_BASE_PATH',
                                    '/var/www/wsgi')
    HTTPD_CONF_DIR = os.environ.get('HTTPD_CONF_DIR',
                                    '/etc/httpd/locations.d')
    HTTPD_HOST = os.environ.get('HTTPD_HOST',
                                platform.node())
    HTTPD_MEDIA_BASE = os.environ.get('HTTPD_MEDIA_BASE',
                                      '/var/www/html/media')
    HTTPD_STATIC_BASE = os.environ.get('HTTPD_STATIC_BASE',
                                       '/var/www/html/static')
    SECRET_KEY_GEN = os.environ.get('SECRET_KEY_GEN',
                                    '/usr/bin/pwgen -c -n -y 78 1')

    app_base = os.path.join(WSGI_BASE_PATH, app)
    path = lambda p: os.path.join(app_base, p)


    app_defaults = {
        'name': app,
        'app_base': app_base,
        'dst': '%(name)s-project',
        'settings': '%(name)s_production',
        'url': '/%(name)s',
        'build': 'build/build.sh',
        'wsgi': 'wsgi.py',
        'allowed_hosts': HTTPD_HOST,
        'secret_key': subprocess.check_output(SECRET_KEY_GEN.split()
                                          ).strip(),
        'media_root': os.path.join(HTTPD_MEDIA_BASE, app),
        'static_root': os.path.join(HTTPD_STATIC_BASE, app),
        'scm': '/usr/bin/git',
        'settings_append': """
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'handlers': {
    'file': {
      'level': 'DEBUG',
      'class': 'logging.FileHandler',
      'filename': '/var/tmp/%(name)s-wsgi.log',
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
""",
    }

    # Protect '%' from interpolation
    app_defaults['secret_key'] = re.sub(r'%',r'', 
                                        app_defaults['secret_key'])
    # Choose clone command
    app_defaults['scm_clone'] = SCM_DEFAULT_CHECKOUT[os.path.split(
        app_defaults['scm'])[-1]]

    # Load defaults
    cfg = SafeConfigParser(app_defaults)

    # Force read
    cfg.readfp(open(app+'.cfg', 'r'))

    #logger.debug('Final configuration:')
    #for k,v in cfg.items(CFG_SECTION):
    #    logger.debug('\t%s: %s', k, v)

    # Create directory
    os.mkdir(app_base)

    # Virtualenv
    virtualenv.create_environment(app_base)

    # Checkout
    subprocess.check_call([
        cfg.get(CFG_SECTION, 'scm'),
        cfg.get(CFG_SECTION, 'scm_clone'),
        cfg.get(CFG_SECTION, 'src'),
        path(cfg.get(CFG_SECTION, 'dst')),
    ],
    stdin=sys.stdin,
    stderr=sys.stderr)

    # Build
    activate = path('bin/activate')
    build = os.path.join(
        cfg.get(CFG_SECTION, 'dst'),
        cfg.get(CFG_SECTION, 'build')
    )
    subprocess.check_call([build],
                          cwd=app_base,
                          env={'BASH_ENV': activate})

    # Create settings
    settings_file = path(cfg.get(CFG_SECTION, 'settings'))+'.py'
    slock = LockFile(settings_file)
    slock.acquire()

    if os.path.exists(settings_file):
        slock.release()
        raise IOError([17, 'File exists'])
    try:
        sfp = open(settings_file, 'w')
        print(DJANGO_SETTINGS_TEMPLATE % dict(cfg.items(CFG_SECTION)),
              file=sfp)
        sfp.close()
    finally:
        slock.release()

    # Create wsgi script
    wsgi_file = path(cfg.get(CFG_SECTION, 'wsgi'))
    slock = LockFile(wsgi_file)
    slock.acquire()

    if os.path.exists(wsgi_file):
        slock.release()
        raise IOError([17, 'File exists'])
    try:
        wfp = open(wsgi_file, 'w')
        print(WSGI_TEMPLATE % dict(cfg.items(CFG_SECTION)),
              file=wfp)
        wfp.close()
    finally:
        slock.release()

    # Create apache conf
    conf_file = os.path.join(HTTPD_CONF_DIR,
                             cfg.get(CFG_SECTION, 'name'))+'.conf'
    slock = LockFile(conf_file)
    slock.acquire()

    if os.path.exists(conf_file):
        slock.release()
        raise IOError([17, 'File exists'])
    try:
        sfp = open(conf_file, 'w')
        conf = dict(cfg.items(CFG_SECTION))
        rlib = re.compile(WSGI_PYTHON_PATH % app_base)
        libs = [p for p in sys.path if rlib.match(p)]
        conf['site_libs'] = os.path.join(virtualenv.path_locations(app_base)[1], 'site-packages')
        http_conf = HTTPD_CONF_TEMPLATE % conf
        print(http_conf,
              file=sfp)
        sfp.close()
    finally:
        slock.release()

    # That's it. Remember to reload apache
    print('You should reload apache:\n', '\t', 'systemctl reload httpd')
    return True
