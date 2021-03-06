# This file performs the installation step once the build is complete.
# Installation primarily involves copying the build results to the
# IronPython site-packages directory.

import os
import zipfile
from os.path import join


numpy_version = '2.0.0b2'


config_txt = """# this file is generated by iron_egg.py
__all__ = ["show"]
_config = {}
def show():
    print 'Numpy for IronPython'
"""

version_txt = """# this file is generated by ironsetup.py
short_version = '%s'
version = '%s'
full_version= '%s.dev-unknown'
git_revision = 'unknown'
release = False

if not release:
    version = full_version
""" % tuple(3 * [numpy_version])

spec_txt = """\
metadata_version = '1.1'
name = 'numpy'
version = '%s'
build = 1

arch = 'x86'
platform = 'cli'
osdist = None
python = None
packages = []
""" % numpy_version

def build_egg():
    egg_name = 'numpy-%s-1.egg' % numpy_version
    print "BUILDING %r ..." % egg_name
    z = zipfile.ZipFile(egg_name, 'w', zipfile.ZIP_DEFLATED)

    ignore_libs = ["Microsoft.Scripting.dll",
                   "Microsoft.Scripting.Metadata.dll",
                   "Microsoft.Dynamic.dll",
                   "IronPython.dll",
                   "IronPython.Modules.dll",
                   # ignore multipe copies and add one below
                   "NumpyDotNet.dll",
                   ]

    # Recursively walk the numpy tree and add all files to the egg
    for root, dirs, files in os.walk("numpy"):
        for fn in files:
            path = join(root, fn)
            if path.startswith('numpy\\linalg\\lapack_lite\\'):
                continue
            if fn.endswith('.py'):
                arcname = path.replace('\\', '/')
                if fn.endswith('_clr.py'):
                    arcname = arcname[:-7] + '.py'
                z.write(path, arcname)

            elif (fn.endswith('.dll') and fn not in ignore_libs):
                z.write(path, 'EGG-INFO/prefix/DLLs/' + fn)

    z.write(r'numpy\NumpyDotNet\bin\NumpyDotNet.dll',
            'EGG-INFO/prefix/DLLs/NumpyDotNet.dll')

    for fn in ('msvcr100.dll', 'msvcp100.dll'):
        z.write(join(os.environ['VSINSTALLDIR'],
                     r'VC\redist\x86\Microsoft.VC100.CRT', fn),
                'EGG-INFO/prefix/DLLs/' + fn)

    z.writestr('numpy/__config__.py', config_txt)
    z.writestr('numpy/version.py', version_txt)
    z.writestr('EGG-INFO/spec/depend', spec_txt)
    z.close()


if __name__ == '__main__':
    build_egg()
