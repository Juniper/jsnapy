### Example showing how to pass yaml data in same file ###
from jnpr.jsnapy import SnapAdmin
from pprint import pprint
from jnpr.junos import Device

js = SnapAdmin()

config_data = """
hosts:
  - device: 10.209.16.204
    username : demo
    passwd: demo123
tests:
  - test_exists.yml
  - test_contains.yml
  - test_is_equal.yml
"""

snapchk = js.snapcheck(config_data, "pre")
for val in snapchk:
    print "Tested on", val.device
    print "Final result: ", val.result
    print "Total passed: ", val.no_passed
    print "Total failed:", val.no_failed
    pprint(dict(val.test_details))
