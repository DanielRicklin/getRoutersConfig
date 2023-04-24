from getRoutersConfig import setInformations
import json
from dotenv import load_dotenv
load_dotenv()
import os
IP = os.environ.get("IP")
USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")

router = setInformations(host_ip=IP, user=USER, password=PASSWORD)

# table = router.getSystemInformation()
# table = router.getStaticRoutes()
# table = router.getInterfaces()
# table = router.getDhcp()

table = router.getFullConfiguration()

print(json.dumps(json.loads(str(table).replace("'", '"')), indent=2))
