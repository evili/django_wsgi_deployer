#!/usr/bin/env python
"""
Utility script for django_deployer
"""
from __future__ import print_function
from django_deployer import deploy_django_app

import sys
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "appname1 [appname2...]")
        sys.exit(1)

    for a in sys.argv[1:]:
        print("Tryng to deploy", a)
        deploy_django_app(a)

