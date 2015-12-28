from pprint import pprint

__author__ = 'jpriyal'

from jnpr.jsnapy.jsnapy import SnapAdmin

js = SnapAdmin()

snap_name= "pre"
config_data = "/etc/jsnapy/config_single_snapcheck.yml"
config_data1 = "/etc/jsnapy/config_single_check.yml"


snapvalue = js.snap("pre", config_data1, dev= None)
print(snapvalue)

snapvalue1 = js.snap("post", config_data1, dev= None)
print snapvalue1

snapcheck = js.snapcheck(snap_name, config_data, dev= None)
print "Tested on", snapcheck.device
print "Final result: ", snapcheck.result
print "Total passed: ", snapcheck.no_passed
print "Total failed:", snapcheck.no_failed
pprint (snapcheck.test_details)


check = js.check("pre", "post", config_data1, dev= None)
print "Tested on", check.device
print "Final result: ", check.result
print "Total passed: ", check.no_passed
print "Total failed:", check.no_failed
pprint (dict(check.test_details))