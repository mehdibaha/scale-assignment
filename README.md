# scale-project

This aims to be a take-home project for the company [Scale](https://www.scaleapi.com/), in order to showcase my technical abilities in a "real-life" development project.

## Getting Started

These instructions will get help get your own copy of the project running on your local machine for development and testing purposes.

### Prerequisites

What do you need to get your development env running

```
Python 2.7, pip, mongodb
```

### Installing

To install the necessary dependencies

```
pip install -r requirements.txt
```

You can run ```demo.py``` for a small preview of the app's capabilities, or import the class in REPL, or a freshly-created file:

```
import TaskQueue

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
