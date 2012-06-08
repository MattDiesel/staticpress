
__NAME__ = 'ssm'
__AUTHOR__ = 'Matt Diesel'
__VERSION__ = '0.01'

import sys, os.path

basepath = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])))

os.system(os.path.join(basepath, "bin\\{}.py {}".format(sys.argv[1], ' '.join(sys.argv[2:]))))
