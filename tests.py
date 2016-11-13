from task_queue import TaskQueue, TaskNotFound, ScalerNotFound
from nose.tools import raises, with_setup
from bson.objectid import ObjectId

tq = TaskQueue()

def cleanup_db():
    tq.tasks.delete_many({})
    tq.scalers.delete_many({})

@with_setup(teardown=cleanup_db)
def test_createTask1():
    """Checks for newly created task its status and urgency"""
    i_task = tq.create_task("immediate")
    assert i_task.status == "pending" and i_task.urgency == 3

@raises(TypeError)
def test_createTask2():
    """Checks create_task returns error if task_id is not an ObjectId"""
    task = tq.create_task(12)

@raises(ValueError)
def test_createTask3():
    """Checks create_task returns error if urgency is not valid"""
    task = tq.create_task("year")

@with_setup(teardown=cleanup_db)
def test_completeTask1():
    """Checks status for newly completed task"""
    t = tq.create_task("immediate")
    tq.complete_task(task_id=t.task_id)
    task = tq.tasks.find_one({"_id": t.task_id})
    assert task["status"] == "completed"

@raises(TypeError)
def test_completeTask2():
    """Checks complete_task returns error if task_id is not an ObjectId"""
    tq.complete_task(task_id=123456)

@raises(TaskNotFound)
def test_completeTask3():
    """Checks complete_task returns error if task is not found in db"""
    tq.complete_task(task_id=ObjectId())

@with_setup(teardown=cleanup_db)
def test_cancelTask():
    """Checks status for newly cancelled task"""
    t = tq.create_task("immediate")
    tq.cancel_task(task_id=t.task_id)
    task = tq.tasks.find_one({"_id": t.task_id})
    assert task["status"] == "canceled"

@with_setup(teardown=cleanup_db)
def test_receiveTasks1():
    """
    The situation:
        -In: 3 scalers, 3 tasks (1 "immediate", 1 "day", 1 "week")
        -The scalers ask for tasks one by one
        -Out:
            Scaler 1 (1 "immediate")
            Scaler 2 (1 week")
            Scaler 3 (1 "week")
    """
    # Creating scalers and tasks
    scalers = [tq.scalers.insert_one({}) for _ in range(3)]
    tasks_i = [tq.create_task("immediate") for _ in range(1)]
    tasks_d = [tq.create_task("day") for _ in range(1)]
    tasks_w = [tq.create_task("week") for _ in range(1)]

    scalers = list(tq.scalers.find({}).limit(3))
    tasks = [tq.receive_tasks(scaler["_id"], batch_size=1)
                                                for scaler in scalers]

    print(tasks[2][0].urgency)

    len1 = len([t for t in tasks[0] if t.urgency == 3])
    len2 = len([t for t in tasks[1] if t.urgency == 2])
    len3 = len([t for t in tasks[2] if t.urgency == 1])
    
    # Each scaler gets 1/1/1 "immediate"/"day"/"week" task
    print(len1, len2, len3)
    assert len1 == len2 == len3 == 1

@with_setup(teardown=cleanup_db)
def test_receiveTasks2():
    """
    The situation:
        -In: 3 scalers, 12 tasks (3 "immediate", 4 "day", 5 "week")
        -The scalers ask for tasks one by one
        -Out:
            Scaler 1 (3 "immediate", 1 "day")
            Scaler 2 (3 "immediate", 1 "week")
            Scaler 3 (4 "week")
    """
    # Creating scalers and tasks
    scalers = [tq.scalers.insert_one({}) for _ in range(3)]
    tasks_i = [tq.create_task("immediate") for _ in range(3)]
    tasks_d = [tq.create_task("day") for _ in range(4)]
    tasks_w = [tq.create_task("week") for _ in range(5)]

    scalers = list(tq.scalers.find({}).limit(3))
    tasks = [tq.receive_tasks(scaler["_id"], batch_size=4)
                                                for scaler in scalers]

    len1 = len([t for t in tasks[0] if t.urgency == 3])
    len2 = len([t for t in tasks[0] if t.urgency == 2])
    len3 = len([t for t in tasks[1] if t.urgency == 2])
    len4 = len([t for t in tasks[1] if t.urgency == 1])
    len5 = len([t for t in tasks[2] if t.urgency == 1])
    
    # First scaler gets 3 "immediate" tasks and 1 "day" task
    assert len1 == 3 and len2 == 1
    # Second scaler gets 3 "day" tasks and 1 "week" task
    assert len3 == 3 and len4 == 1
    # Third scaler gets 4 "week" tasks
    assert len5 == 4

@with_setup(teardown=cleanup_db)
def test_receiveTasks3():
    """
    The situation:
        -In: 2 scalers, 3 tasks (3 "immediate")
        -Scaler1 asks for 3 tasks
        -Scaler2 asks for 1 task
        -Out:
            Scaler 1 (3 "immediate")
            Scaler 2 (0 tasks)
    """
    # Creating scalers and tasks
    scalers = [tq.scalers.insert_one({}) for _ in range(2)]
    tasks_i = [tq.create_task("immediate") for _ in range(3)]

    scaler1, scaler2 = tq.scalers.find({}).limit(2)
    tasks1 = tq.receive_tasks(scaler1["_id"], batch_size=3)
    tasks2 = tq.receive_tasks(scaler2["_id"], batch_size=1)

    len1 = len([t for t in tasks1 if t.urgency == 3])
    len2 = len(tasks2)
    
    # First scaler gets 3 "immediate" tasks, Second scaler gets 0 tasks
    assert len1 == 3 and len2 == 0

@raises(ScalerNotFound)
def test_receiveTasks4():
    """Checks receive_tasks returns error if scaler is not found in db"""
    tq.receive_tasks(scaler_id=ObjectId(), batch_size=1)

@raises(ValueError)
def test_receiveTasks5():
    """Checks receive_tasks returns error if batch_size is not > 0"""
    tq.receive_tasks(scaler_id=ObjectId(), batch_size=0)

@raises(TypeError)
def test_receiveTasks6():
    """Checks receive_tasks returns error if scaler_id is not an ObjectId"""
    tq.receive_tasks(scaler_id=123456, batch_size=3)

@with_setup(teardown=cleanup_db)
def test_unassignTasks1():
    """
    The situation:
        -In: 2 scalers, 2 tasks (1 "day", 1 "week")
        -The 2 scalers ask for tasks one by one
        -We unassign tasks for Scaler1
        -scalers ask for tasks
        -Out:
            Scaler 1 (0 tasks)
            Scaler 2 (1 "immediate", 1 "day")
    """
    # Creating scalers and tasks
    scalers = [tq.scalers.insert_one({}) for _ in range(2)]
    tasks_i = [tq.create_task("day") for _ in range(1)]
    tasks_d = [tq.create_task("week") for _ in range(1)]
    # Assigning tasks one by one
    scaler1, scaler2 = tq.scalers.find({}).limit(2)
    tasks1 = tq.receive_tasks(scaler1["_id"], batch_size=1)
    tasks2 = tq.receive_tasks(scaler2["_id"], batch_size=1)
    # Unassigning for Scaler1
    tq.unassign_tasks(scaler_id=scaler1["_id"])
    # Assigning remaining tasks to scalers one by one (2nd then 1st scaler)
    tq.receive_tasks(scaler2["_id"], batch_size=1)
    tq.receive_tasks(scaler1["_id"], batch_size=1)
    # Retrieving tasks for scaler1, scaler2
    tasks1 = tq.tasks.find({"scaler_id": scaler1["_id"]})
    tasks2 = tq.tasks.find({"scaler_id": scaler2["_id"]})
    tasks1 = list(tasks1); tasks2 = list(tasks2)
    # Retrieving amounts of task by urgency
    len1 = len(tasks1)
    len2 = len([t for t in tasks2 if t["urgency"] == 1])
    len3 = len([t for t in tasks2 if t["urgency"] == 2])
    print(len1, len2, len3)

    # Scaler1 has 0 tasks, Scaler2 has 1/1 "immediate"/"day"
    assert len1 == 0 and len2 == len3 == 1