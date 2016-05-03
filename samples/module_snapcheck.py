### performing function similar to --snapcheck option in command line ######
from jnpr.jsnapy import SnapAdmin
from pprint import pprint
from jnpr.junos import Device

js = SnapAdmin()

config_file = "/etc/jsnapy/testfiles/config_single_snapcheck.yml"
snapvalue = js.snapcheck(config_file, "snap")

for snapcheck in snapvalue:
    print "\n -----------snapcheck----------"
    print "Tested on", snapcheck.device
    print "Final result: ", snapcheck.result
    print "Total passed: ", snapcheck.no_passed
    print "Total failed:", snapcheck.no_failed
    pprint(dict(snapcheck.test_details))
