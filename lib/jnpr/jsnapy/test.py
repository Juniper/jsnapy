__author__ = 'jpriyal'

from jnpr.jsnapy.jsnapy import SnapAdmin

js = SnapAdmin()

snap_name= "pre"
config_data = "/etc/jsnapy/config_single_snapcheck.yml"
config_data1 = "/etc/jsnapy/config_single_check.yml"

snapvalue = js.snap(snap_name, config_data1, dev= None)
print(snapvalue)

snapvalue1 = js.snap("post", config_data1, dev= None)
print(snapvalue1)

'''
snapcheck = js.snapcheck(snap_name, config_data, dev= None)
print snapvalue
'''

chk_value = js.check("pre", "post", config_data1, dev= None)