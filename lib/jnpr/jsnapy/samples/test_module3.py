from jnpr.jsnapy import SnapAdmin
from pprint import pprint
from jnpr.junos import Device

dev = Device(host='10.209.61.156', user='regress', password='MaRtInI')
dev.open()

js = SnapAdmin()
config_data = """
hosts:
  - device: 10.209.16.206
    username : regress
    passwd: MaRtInI
tests:
  - test_is_equal.yml
"""

chk = js.check(
    "/etc/jsnapy/config_single_check.yml",
    "/etc/jsnapy/10.209.16.204_pre_show_interfaces_terse_lo*.xml",
    "/etc/jsnapy/10.209.16.204_post_show_interfaces_terse_lo*.xml")
for check in chk:
    print "Tested on", check.device
    print "Final result: ", check.result
    print "Total passed: ", check.no_passed
    print "Total failed:", check.no_failed
    print check.test_details
    pprint(dict(check.test_details))
