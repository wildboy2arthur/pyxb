#!/usr/bin/env pythong

from distutils.core import setup, Command
import os
import stat
import re

class test (Command):

    # Brief (40-50 characters) description of the command
    description = "Run all unit tests found "

    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [ ( 'testdirs', None, 'colon separated list of directories to search for tests' ) ]

    def initialize_options (self):
        self.testdirs = 'tests'


    __TestFile_re = re.compile('^test.*\.py$')
    def finalize_options (self):
        pass

    def run (self):
        # Walk the tests hierarchy looking for tests
        dirs = self.testdirs.split(':')
        tests = [ ]
        while dirs:
            dir = dirs.pop(0)
            print 'Searching for tests in %s' % (dir,)
            for f in os.listdir(dir):
                fn = os.path.join(dir, f)
                statb = os.stat(fn)
                if stat.S_ISDIR(statb[0]):
                    dirs.append(fn)
                elif self.__TestFile_re.match(f):
                    tests.append(fn)

        number = 0
        import sys
        import traceback
        import new
        import unittest
        import types

        # Import each test into its own module, then add the test
        # cases in it to a complete suite.
        loader = unittest.defaultTestLoader
        suite = unittest.TestSuite()
        for fn in tests:
            stage = 'compile'
            try:
                # Assign a unique name for this test
                test_name = 'test%d' % (number,)
                number += 1

                # Read the test source in and compile it
                rv = compile(file(fn).read(), test_name, 'exec')
                state = 'evaluate'

                # Make a copy of the globals array so we don't
                # contaminate this environment.
                g = globals().copy()

                # The test cases use __file__ to determine the path to
                # the schemas
                g['__file__'] = fn

                # Create a module into which the test will be evaluated.
                module = new.module(test_name)

                # The generated code uses __name__ to look up the
                # containing module in sys.modules.
                g['__name__'] = test_name
                sys.modules[test_name] = module

                # Import the test into the module
                eval(rv, g)

                # Find all subclasses of unittest.TestCase that were
                # in the test source and add them to the suite.
                for (nm, obj) in g.items():
                    if (type == type(obj)) and issubclass(obj, unittest.TestCase):
                        suite.addTest(loader.loadTestsFromTestCase(obj))
                print '%s imported' % (fn,)
            except Exception, e:
                print '%s failed in %s: %s' % (fn, state, e)
                traceback.print_exception(*sys.exc_info())

        # Run everything
        runner = unittest.TextTestRunner()
        runner.run(suite)

# Require Python 2.4

setup(name='PyXB',
      description = 'Python W3C XML Schema Bindings',
      author='Peter A. Bigot',
      author_email='pyxb@comcast.net',
      url='http://pyxb.sourceforge.net',
      version='0.1.3',
      packages=[ 'pyxb', 'pyxb.binding', 'pyxb.utils', 'pyxb.xmlschema', 'pyxb.standard.bindings' ],
      data_files= [ ('pyxb/standard/schemas', [ '*.xsd' ] ) ],
      scripts=[ 'scripts/pyxbgen', 'scripts/pyxbwsdl' ],
      cmdclass = { 'test' : test } )
      
