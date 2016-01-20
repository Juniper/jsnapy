from jnpr.jsnapy import SnapAdmin
from pprint import pprint
from jnpr.junos import Device

dev = Device(host='10.209.16.204', user='regress', password='MaRtInI' )
dev.open()


js = SnapAdmin()
print "Version is:", versi
on

#config_file = "/etc/jsnapy/config_multiple_snapcheck.yml"
config_file = "/etc/jsnapy/config_multiple_check.yml"

config_data= """
hosts:
  - include: devices.yml
    group: MX
tests:
  - test_is_equal.yml
#  - test_no_diff.yml
#  - test_not_less.yml
#  - test_not_more.yml
#  - test_delta.yml
sqlite:
  - store_in_sqlite: yes
    check_from_sqlite: yes
    database_name: jbb.db
    compare: 0,1
mail: send_mail.yml

"""

snapvalue = js.check(config_data, None, None, dev)
print "snap value is:", snapvalue


for snapcheck in snapvalue:
    print "\n -----------snapcheck----------", snapcheck
    print "Tested on", snapcheck.device
    print "Final result: ", snapcheck.result
    print "Total passed: ", snapcheck.no_passed
    print "Total failed:", snapcheck.no_failed
    pprint (dict(snapcheck.test_details))
