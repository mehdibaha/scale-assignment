

class TaskQueue(object):
    """
    Assigns tasks so that it prioritizes tasks based on when they need to be completed by.

    It should also assign tasks so that no task is assigned to multiple Scalers
    at the same time, where each Scaler will be identified by a unique scaler_id.
    """

    def __init__(self):
        super(TaskQueue, self).__init__()

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
        #mondogb create task, returns task_id
        task_id, created_at, completed_at, status = 1, 1, 1, 1
        new_task = Task(task_id, created_at, completed_at, status urgency)
        return new_task

    def complete_task(self, task_id):
        """
        Marks the given pending task as completed

        :param int task_id: Id of the task
        :return: the updated Task object
        :rtype: Task
        :raises TypeError: if task_id is not an int
        :raises TaskNotFound: if the task with given id does not exist
        """
        modify_task(task_id, status="completed")


    def cancel_task(self, task_id):
        """
        Marks the given pending task as canceled

        :param int task_id: Id of the task
        :return: the updated Task object
        :rtype: Task
        :raises TypeError: if task_id is not an int
        :raises TaskNotFound: if the task with given id does not exist
        """
        modify_task(task_id, status="canceled")

    def modify_task(self, task_id, status):
        """
        Internal method to modify the status of tasks

        :param int task_id: Id of the task
        :param str status: Status to modify the tasks status to
        :return: the updated Task object
        :rtype: Task
        :raises TypeError: if task_id is not an int
        :raises TaskNotFound: if the task with given id does not exist
        """
        if type(task_id) is not int:
            raise TypeError("Task_id parameter should be an int")
        #mongo.get(task_id)
        #catch exception mongodb, then
        #modify task object then update with paremeters
        if False:
            raise TaskNotFound("Task not found in db")
        return Task(1, "")
    
    def receive_tasks(self, scaler_id, batch_size):
        """
        Assigns a batch of the highest priority batch_size tasks to Scaler with
        given scaler_id

        :param int scaler_id: Id of the scaler
        :param int batch_size: size of the tasks batch
        :return: the batch of assigned tasks in a list
        :rtype: List<Task>
        :raises TypeError: if scaler_id (or batch_size) is not an int
        :raises ValueError: if the batch_size is inferior or equal to 0
        :raises ScalerNotFound: if the scaler with given id does not exist
        """
        if type(task_id) is not int:
            raise TypeError("Task_id parameter should be an int")
        if batch_size <= 0:
            raise TypeError("Batch_size parameter should be strictly superior to 0")
        #mongo.get(scaler_id)
        #catch exception mongodb, then
        raise ScalerNotFound("Scaler not found in db")
        #do magic
        tasks_list = []
        return tasks_list
    
    def unassign_tasks(self, scaler_id):
        """
        Unassigns all tasks assigned to the Scaler with given scaler_id

        :param int scaler_id: Id of the scaler
        :return: the unassinged tasks in a list
        :rtype: List<Task>
        :raises TypeError: if scaler_id is not an int
        :raises ScalerNotFound: if the scaler with given id does not exist
        """
        if type(task_id) is not int:
            raise TypeError("Task_id parameter should be an int")
        if batch_size <= 0:
            raise TypeError("Batch_size parameter should be strictly superior to 0")
        #mongo.get(scaler_id)
        #catch exception mongodb, then
        if False:
            raise ScalerNotFound("Scaler not found in db")
        #do magic
        tasks_list = []
        return tasks_list

class Task(object):
    """
    Implements a Task with a given id, and urgency
    """
    def __init__(self, task_id, created_at, completed_at, status, urgency):
        super(Task, self).__init__()
        self.task_id = task_id
        self.created_at = created_at
        self.completed_at = completed_at
        self.status = status
        self.urgency = urgency
    
class Scaler(object):
    """
    Implements a Scaler with a given id
    """
    def __init__(self, scaler_id):
        super(Scaler, self).__init__()
        self.scaler_id = scaler_id

class TaskNotFound(ValueError):
    """Exception raised for error in giving unvalid task id"""

class ScalerNotFound(ValueError):
    """Exception raised for error in giving unvalid scaler id"""