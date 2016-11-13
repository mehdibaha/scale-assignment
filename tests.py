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

@raises(ScalerNotFound)
def test_receiveTasks3():
    """Checks receive_tasks returns error if scaler is not found in db"""
    tq.receive_tasks(scaler_id=ObjectId(), batch_size=1)

@raises(ValueError)
def test_receiveTasks4():
    """Checks receive_tasks returns error if batch_size is not > 0"""
    tq.receive_tasks(scaler_id=ObjectId(), batch_size=0)

@raises(TypeError)
def test_receiveTasks5():
    """Checks receive_tasks returns error if scaler_id is not an ObjectId"""
    tq.receive_tasks(scaler_id=123456, batch_size=3)