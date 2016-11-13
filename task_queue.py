# Pymongo
import pymongo
from pymongo import MongoClient
from pymongo.collection import ReturnDocument

# Other imports
from datetime import datetime
from bson.objectid import ObjectId

MONGO_URL = 'localhost'
MONGO_PORT = '27017'
DB_NAME = 'scale-db'
TASKS_COLLECTION = 'tasks'
SCALERS_COLLECTION = 'scalers'

class TaskQueue(object):
    """
    Assigns tasks so that it prioritizes tasks based on when they need to be completed by.

    It should also assign tasks so that no task is assigned to multiple Scalers
    at the same time, where each Scaler will be identified by a unique scaler_id.
    """

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[DB_NAME]
        self.tasks = self.db[TASKS_COLLECTION]
        self.scalers = self.db[SCALERS_COLLECTION]

    def create_task(self, urgency):
        """
        Creates task based on urgency

        :param str urgency: Urgency of the task
        :return: the object Task created
        :rtype: Task
        :raises TypeError: if urgency is not a string
        :raises ValueError: if urgency is not "immediate" or "day" or "week"
        """
        if type(urgency) is not str:
            raise TypeError("Urgency parameter should be a string")
        if urgency not in ["immediate", "day", "week"]:
            raise ValueError("Urgency parameter not \"immediate\" or \"day\" or \"week\"")
        # Creating document in mongodb, then retrieving to convert it as a object
        urgency = self.to_int(urgency)
        new_id = self.tasks.insert_one({"urgency": urgency, "created_at": datetime.utcnow(), "status": "pending", "completed_at": None, "scaler_id": None}).inserted_id
        task = self.tasks.find_one({"_id": new_id})
        return self.to_obj(task)

    def complete_task(self, task_id):
        """
        Marks the given pending task as completed

        :param ObjectId task_id: Id of the task
        :return: the updated Task object
        :rtype: Task
        :raises TypeError: if task_id is not an ObjectId
        :raises TaskNotFound: if the task with given id does not exist
        """
        self.modify_task(task_id, status="completed")

    def cancel_task(self, task_id):
        """
        Marks the given pending task as canceled

        :param ObjectId task_id: Id of the task
        :return: the updated Task object
        :rtype: Task
        :raises TypeError: if task_id is not an ObjectId
        :raises TaskNotFound: if the task with given id does not exist
        """
        self.modify_task(task_id, status="canceled")
    
    def receive_tasks(self, scaler_id, batch_size):
        """
        Assigns a batch of the highest priority batch_size tasks to Scaler with
        given scaler_id

        :param ObjectId scaler_id: Id of the scaler
        :param int batch_size: size of the tasks batch
        :return: the batch of assigned tasks in a list
        :rtype: List<Task>
        :raises TypeError: if scaler_id is not an ObjectId or batch_size is not an int
        :raises ValueError: if the batch_size is inferior or equal to 0
        :raises ScalerNotFound: if the scaler with given id does not exist
        """
        if type(scaler_id) is not ObjectId:
            raise TypeError("Scaler_id parameter should be an ObjectId")
        if type(batch_size) is not int:
            raise TypeError("Bach_size parameter should be an int")
        if batch_size <= 0:
            raise ValueError("Batch_size parameter should be strictly superior to 0")
        scaler = self.scalers.find_one({'_id': scaler_id})
        if scaler:
            # Looking for unassigned tasks ids by priority and batch_size
            tasks = self.tasks.find({"status": "pending", "scaler_id": None}).sort([("urgency", -1)]).limit(batch_size)
            ids = [task['_id'] for task in tasks]
            # Assigning tasks to scaler_id
            self.tasks.update_many({'_id': {'$in': ids}}, {'$set': {'scaler_id': scaler_id, 'status': 'pending'}}, upsert=False)
            # Retrieving updated tasks
            new_tasks = self.tasks.find({'_id': {'$in': ids}})
            new_tasks = [self.to_obj(task) for task in new_tasks]
            return new_tasks
        else:
            raise ScalerNotFound("Scaler not found in db")
    
    def unassign_tasks(self, scaler_id):
        """
        Unassigns all tasks assigned to the Scaler with given scaler_id

        :param ObjectId scaler_id: Id of the scaler
        :return: the unassigned tasks in a list
        :rtype: List<Task>
        :raises TypeError: if scaler_id is not an ObjectId
        :raises ScalerNotFound: if the scaler with given id does not exist
        """
        if type(scaler_id) is not ObjectId:
            raise TypeError("Scaler_id parameter should be an ObjectId")
        scaler = self.scalers.find_one({"_id": scaler_id})
        if scaler:
            # Retrieving tasks (and ids) assigned to scaler_id
            tasks = self.tasks.find({"scaler_id": scaler_id})
            ids = [t['_id'] for t in tasks]
            # Updating tasks retrieved
            self.tasks.update_many({"scaler_id": scaler_id}, {'$set': {"status": "pending", "scaler_id": None}}, upsert=False)
            new_tasks = self.tasks.find({'_id': {'$in': ids}})
            new_tasks = [self.to_obj(task) for task in new_tasks]
            return new_tasks
        else:
            raise ScalerNotFound("Scaler not found in db")

    def modify_task(self, task_id, status):
        """
        Internal method to modify the status of tasks

        :param ObjectId task_id: Id of the task
        :param str status: Status to modify the tasks status to
        :return: the updated Task object
        :rtype: Task
        :raises TypeError: if task_id is not an ObjectId
        :raises TaskNotFound: if the task with given id does not exist
        """
        if type(task_id) is not ObjectId:
            raise TypeError("Task_id parameter should be an ObjectId")
        to_modify = {'status': status, 'scaler_id': None}
        if status is "completed":
            to_modify["completed_at"] = datetime.utcnow()
        task = self.tasks.find_one_and_update({'_id': task_id}, {'$set': to_modify}, upsert=False, return_document=ReturnDocument.AFTER)
        if task:
            return self.to_obj(task) 
        else:
            raise TaskNotFound("Task not found in db")

    def to_obj(self, task):
        return Task(task_id=task["_id"], status=task["status"], created_at=task["created_at"], urgency=task["urgency"], scaler_id=task["scaler_id"], completed_at=task["completed_at"])

    def to_int(self, urgency):
        if urgency is "immediate":
            return 3
        elif urgency is "day":
            return 2
        else: #urgency is "week"
            return 1

class Task(object):
    """
    Implements a Task with a given id, and urgency
    """
    def __init__(self, task_id, created_at, status, urgency, scaler_id, completed_at):
        self.task_id = task_id
        self.created_at = created_at
        self.status = status
        self.urgency = urgency
        self.completed_at = completed_at
        self.scaler_id = scaler_id

class TaskNotFound(ValueError):
    """Exception raised for error in giving unvalid task id"""

class ScalerNotFound(ValueError):
    """Exception raised for error in giving unvalid scaler id"""