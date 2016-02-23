from jnpr.jsnapy import SnapAdmin
from pprint import pprint
from jnpr.junos import Device


js = SnapAdmin()

config_file = "/etc/jsnapy/config_single_snapcheck.yml"
try:
    print "inside try"
    js.snap(config_file, "pre")
except Exception as ex:
    print "inside exception"
    print "Ex is", ex
else:
    print "Hello"
