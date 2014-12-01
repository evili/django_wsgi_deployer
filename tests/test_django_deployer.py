"""
Test suite for django_wsgi_deployer
"""
from __future__ import print_function
from unittest import TestCase
import tempfile
import os
import sys
import shutil

import django_wsgi_deployer


class TestDeploy(TestCase):
    """Base Class For Deploy Tests. It creates a root environment to
    simulate server directories (wsgi, conf, etc.)"""
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='test_dj_deploy-', suffix='.d')
        self.wsgi_base = os.path.join(self.root, 'wsgi')
        self.httpd_conf = os.path.join(self.root, 'httpd')
        os.environ['WSGI_BASE_PATH'] = self.wsgi_base
        os.environ['HTTPD_CONF_DIR'] = self.httpd_conf
        os.chdir(self.root)
        os.mkdir(self.wsgi_base)
        os.mkdir(self.httpd_conf)

    def tearDown(self):
        shutil.rmtree(self.root)


class TestSimpleProject(TestDeploy):
    """Test deploy the simplest Django project"""
    def setUp(self):
        super(TestSimpleProject, self).setUp()
        self.test_proj = 'django_test_deploy'
        self.test_cf = os.path.join(self.root, self.test_proj+'.cfg')
        test_cf_h = open(self.test_cf, 'w')
        print('[deploy]', file=test_cf_h)
        print('name=django_test_deploy', file=test_cf_h)
        print('src=https://github.com/evili/'+self.test_proj+'.git',
              file=test_cf_h)
        print('scm=git', file=test_cf_h)
        test_cf_h.close()

    def test_deploy(self):
        """Deploy the simplest Django project"""
        self.assertTrue(django_wsgi_deployer.deploy_django(self.test_proj),
                        msg='Could not deploy {0} project'.format(
                            self.test_proj))
