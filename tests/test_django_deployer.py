"""
Test suite for django_wsgi_deployer
"""
from __future__ import print_function
from unittest import TestCase
import tempfile
import os
import shutil
import sys
import subprocess
import shutil
import django_wsgi_deployer


class TestDeploy(TestCase):
    """Base Class For Deploy Tests. It creates a root environment to
    simulate server directories (wsgi, conf, etc.)"""
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='test_dj_deploy-', suffix='.d')
        self.wsgi_base = os.path.join(self.root, 'wsgi')
        self.httpd_conf = os.path.join(self.root, 'httpd')
        self.httpd_static = os.path.join(self.root, 'static')
        self.httpd_media = os.path.join(self.root, 'media')
        os.environ['WSGI_BASE_PATH'] = self.wsgi_base
        os.environ['HTTPD_CONF_DIR'] = self.httpd_conf
        os.environ['HTTPD_STATIC_BASE'] = self.httpd_static
        os.environ['HTTPD_MEDIA_BASE'] = self.httpd_media
        os.chdir(self.root)
        os.mkdir(self.wsgi_base)
        os.mkdir(self.httpd_conf)
        os.mkdir(self.httpd_static)
        os.mkdir(self.httpd_media)

    def tearDown(self):
        shutil.rmtree(self.root)


class TestSimpleProject(TestDeploy):
    """Test deploy the simplest Django project"""
    def setUp(self):
        super(TestSimpleProject, self).setUp()
        self.test_proj = 'django_test_deploy'
        self.test_cf = os.path.join(self.root, self.test_proj+'.cfg')
        self.test_cf_h = open(self.test_cf, 'w', buffering=1)
        print('[deploy]', file=self.test_cf_h)
        print('name=django_test_deploy', file=self.test_cf_h)
        print('src=https://github.com/evili/'+self.test_proj+'.git',
              file=self.test_cf_h)
        print('scm=git', file=self.test_cf_h)
        print('requires=django-resto', file=self.test_cf_h)

    def test_deploy(self):
        """Deploy the simplest Django project"""
        self.assertTrue(django_wsgi_deployer.deploy_django(self.test_proj),
                        msg='Could not deploy {0} project'.format(
                            self.test_proj))

    def test_deploy_with_single_requirement(self):
        print('deploy_requires=django-jenkins', file=self.test_cf_h)
        self.assertTrue(django_wsgi_deployer.deploy_django(self.test_proj),
                        msg='Could not deploy {0} project with requirement'.\
                        format(self.test_proj))

    def test_deploy_with_requirements(self):
        print("deploy_requires=django-resto,django-jenkins", 
              file=self.test_cf_h)
        self.assertTrue(django_wsgi_deployer.deploy_django(self.test_proj),
                        msg='Could not deploy {0} project with requirements'.\
                        format(self.test_proj))

    def test_with_django_commands(self):
        print("deploy_commands=migrate,collectstatic --noinput",
              file=self.test_cf_h)
        self.assertTrue(django_wsgi_deployer.deploy_django(self.test_proj),
                        msg='Could not deploy {0} project with commands'.\
                        format(self.test_proj))


    def tearDown(self):
        _KEEP_TEMP = 'KEEP_TEMP_FILES'
        self.test_cf_h.close()
        if os.environ.has_key(_KEEP_TEMP):
            print('Keeping root directory: %s' % self.root, file=sys.stderr)
        else:
            print('Deleting root tree: %s' % self.root, file=sys.stderr)
            shutil.rmtree(self.root)
