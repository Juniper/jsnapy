from pprint import pprint

from jnpr.jsnapy import SnapAdmin

js = SnapAdmin()

config_data = "/etc/jsnapy/config_single_snapcheck.yml"
config_data1 = "/etc/jsnapy/config_single_check.yml"

"""
snapvalue = js.snap("pre", config_data1, dev= None)
print(snapvalue)
snapvalue1 = js.snap("pre1", config_data1, dev= None)
print snapvalue1
"""
"""
snapchk = js.snapcheck("pre", config_data, dev= None)

for snapcheck in snapchk:
    print "\n -----------snapcheck----------", snapcheck
    print "Tested on", snapcheck.device
    print "Final result: ", snapcheck.result
    print "Total passed: ", snapcheck.no_passed
    print "Total failed:", snapcheck.no_failed
    pprint (dict(snapcheck.test_details))

"""
chk = js.check("pre", "pre1", config_data1, dev= None)
for check in chk:
    print "Tested on", check.device
    print "Final result: ", check.result
    print "Total passed: ", check.no_passed
    print "Total failed:", check.no_failed
    pprint (dict(check.test_details))
