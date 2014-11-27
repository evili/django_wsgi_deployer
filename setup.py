from setuptools import setup

setup(name='django_deployer',
      version='0.1',
      description='Django Project Deployer',
      url='https://devel.iri.upc.edu/iritic/scripts/trunk/django_deployer',
      author='Evili del Rio',
      author_email='erio@iri.upc.edu',
      license='LGPL',
      packages=['django_deployer'],
      scripts=['djdeploy.py'],
      zip_safe=False)


