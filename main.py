from getRoutersConfig import setInformations
import json
from dotenv import load_dotenv
load_dotenv()
import os
IP = os.environ.get("IP")
USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")
BASTION = os.environ.get("BASTION")

router = setInformations(host_ip=IP, user=USER, password=PASSWORD, bastion_ip=BASTION)
# table = router.getSystemInformation()
# table = router.getIpv4StaticRoutes()
# table = router.getInterfaces()
# table = router.getDhcp()
table = router.getAcl()

# table = router.getFullConfiguration()
router.disconnect()

print(json.dumps(json.loads(str(table).replace("'", '"')), indent=2))
