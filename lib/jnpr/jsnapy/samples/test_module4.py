from jnpr.jsnapy import SnapAdmin
from pprint import pprint
from jnpr.junos import Device

dev = Device(host='10.209.16.204', user='regress', password='MaRtInI')
dev.open()


js = SnapAdmin()

config_file1 = "/etc/jsnapy/testfiles/config_single_snapcheck.yml"

config_data = """
hosts:
  - include: device.yml
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

snap = js.snap(config_file, "pre")
snap2 = js.snap(config_file, "post")

chk = js.snapcheck(config_file1, "pre")


for check in chk:
    print "Tested on", check.device
    print "Final result: ", check.result
    print "Total passed: ", check.no_passed
    print "Total failed:", check.no_failed
    print check.test_details
    pprint(dict(check.test_details))
