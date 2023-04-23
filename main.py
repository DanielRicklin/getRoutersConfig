from getRoutersConfig import setInformations
import json
router = setInformations(host_ip='192.168.1.101', user='admin', password='!adm;rmi')

# table = router.getStaticRoutes()

table = router.getFullConfiguration()

# table = router.getSystemInformation()
# table = router.getInterfaces()
# print(table)
print(json.dumps(json.loads(str(table).replace("'", '"')), indent=2))
