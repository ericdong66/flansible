import os
import sys


def site():
    install_path = os.path.dirname(__file__)
    print >> sys.stdout, str(os.path.join(install_path, 'site.yml'))
