from task_queue import TaskQueue, TaskNotFound
from nose.tools import raises
from bson.objectid import ObjectId

tq = TaskQueue()

def test_createTask():
    i_task = tq.create_task("immediate")
    assert i_task.status == "pending" and i_task.urgency == "immediate"

@raises(TypeError)
def test_createTask2():
    task = tq.create_task(12)

@raises(ValueError)
def test_createTask3():
    task = tq.create_task("year")

def test_completeTask():
    t = tq.create_task("immediate")
    tq.complete_task(task_id=t.task_id)
    task = tq.tasks.find_one({"_id": t.task_id})
    assert task["status"] == "completed"

@raises(TypeError)
def test_completeTask2():
    tq.complete_task(task_id=123456)

@raises(TaskNotFound)
def test_completeTask3():
    tq.complete_task(task_id=ObjectId())

def test_cancelTask():
    t = tq.create_task("immediate")
    tq.cancel_task(task_id=t.task_id)
    task = tq.tasks.find_one({"_id": t.task_id})
    assert task["status"] == "canceled"
