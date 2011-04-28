# simple test against celery

from celery.task.control import inspect
i = inspect()
print i.registered_tasks()


"""
from celery.execute import send_task
r = send_task("videofile.import", ['/home/cribeiro/work/vdeli/cdnmanager/cdnmanager/cdn/uploads/cribeiro/myproject/lixao1'])
print r
import time
for i in xrange(30):
    print i, r.ready(), r.result
    time.sleep(1)
"""

