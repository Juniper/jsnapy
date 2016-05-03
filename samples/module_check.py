### Performing function similar to --check in command line ###
from jnpr.jsnapy import SnapAdmin
from pprint import pprint
from jnpr.junos import Device

js = SnapAdmin()

config_file = "/etc/jsnapy/testfiles/config_check.yml"
js.snap(config_file, "pre")
js.snap(config_file, "post")
chk = js.check(config_file, "pre", "post")

for check in chk:
    print "Tested on", check.device
    print "Final result: ", check.result
    print "Total passed: ", check.no_passed
    print "Total failed:", check.no_failed
    print check.test_details
    pprint(dict(check.test_details))
