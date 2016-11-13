# scale-project

This aims to be a take-home project for the company [Scale](https://www.scaleapi.com/), in order to showcase my technical abilities in a "real-life" development project.

## Getting Started

These instructions will get help get your own copy of the project running on your local machine for development and testing purposes.

### Prerequisites

To get your development environment running, you need

```
Python 2.7, pip, mongodb
```

### Installing

To install the necessary python dependencies

```
pip install -r requirements.txt
```

To start running tests, or using the class, you should run ```add_scalers.py```. This helps create a few scalers in the db.
You can then use the TaskQueue class by import

```
from task_queue import TaskQueue

tq = TaskQueue(...)
tq.create_task(..., ...)
```

## Running the tests

To run the complete test suite, you'll have to run the following command:

```
nosetests
```

## Stack

* [Python](https://www.python.org/) - Primary language for development
* [Mongodb](https://www.mongodb.com/) - Database platform

## Authors

* **Mehdi BAHA** - [mehdibaha](https://github.com/mehdibaha)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Big thanks to Scale for the opportunity
* Python community for such an awesome language
