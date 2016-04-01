### Example showing how to use existing device connection ###
from jnpr.jsnapy import SnapAdmin
from pprint import pprint
from jnpr.junos import Device

dev_obj = Device(host='10.209.61.156', user='demo', password='demo123')
dev_obj.open()

js = SnapAdmin()
config_file = "/etc/jsnapy/testfiles/config_check.yml"

# can pass device object
# it will not create new connection with device
snapchk = js.snapcheck(config_file, "snap", dev=dev_obj)

for val in snapchk:
    print "Tested on", val.device
    print "Final result: ", val.result
    print "Total passed: ", val.no_passed
    print "Total failed:", val.no_failed
    print val.test_details
    pprint(dict(val.test_details))
