from pprint import pprint
from jnpr.junos import Device
from jnpr.jsnapy import SnapAdmin

js = SnapAdmin()
config_file = "/etc/jsnapy/config_single_snapcheck.yml"


dev = Device(host='10.209.61.156', user='regress', password='MaRtInI')
dev.open()

config_data = "/etc/jsnapy/config_single_snapcheck.yml"
config_data1 = "/etc/jsnapy/config_single_check.yml"
"""
hosts:
  - device: 10.209.16.204
    username : regress
    passwd: MaRtInI

"""

config_data = """
tests:
  #- test_delta.yml
 # - test_not_more.yml
  #- test_not_less.yml
  #- test_contains.yml
  #- test_no_diff.yml
  #- test_all_same.yml
 # - test_exists.yml
  - test_is_equal.yml
 # - test_not_range.yml
  #- test_get_config.yml
"""


print "config_data", config_data

snapvalue = js.snap(config_file, "pre")
print "snap value is:", snapvalue
snapvalue2 = js.snap(config_data, "post", dev)
# print "dev is:", dev
snapchk = js.snapcheck(config_data, "pre", dev)

for snapcheck in snapchk:
    print "\n -----------snapcheck----------", snapcheck
    print "Tested on", snapcheck.device
    print "Final result: ", snapcheck.result
    print "Total passed: ", snapcheck.no_passed
    print "Total failed:", snapcheck.no_failed
    pprint(dict(snapcheck.test_details))
"""
chk = js.check(config_data, "pre", "post", dev)
for check in chk:
    print "Tested on", check.device
    print "Final result: ", check.result
    print "Total passed: ", check.no_passed
    print "Total failed:", check.no_failed
    print check.test_details
    pprint (dict(check.test_details))
"""
