
from units.engine.orm import *
from units.engine.tasker.work_planner import WorkPlanner

orm = ORM()

#task = orm.set('task', {'protocol':'http', 'hostname':'localhost', 'port':80, 'path':'/'})

task = orm.session.query(Task).filter_by(id=1).first()

print(task)

wp = WorkPlanner(orm, task, 200)

pw = wp.get_pending_work()

print(pw)