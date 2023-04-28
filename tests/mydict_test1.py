from pysyncobj import SyncObj
from mydict import ReplDict
import time

dict1 = ReplDict()
syncObj = SyncObj("node-1:9000", ["node-1:9001", "node-1:9002"], consumers=[dict1])

time.sleep(5)

while True:
    dict1.set_nested_item("testKey1", "key", "testValue1", sync=True)
    print(
        dict1.get_nested_item("testKey1", "key"),
        dict1.get_nested_item("testKey2", "key"),
        dict1.get_nested_item("testKey3", "key"),
    )
    time.sleep(0.5)
