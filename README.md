# PayU Hub E2EE example
This repository is based on the implementation of a simple python implementation of PayU Hub [End To End Encryption](https://developers.paymentsos.com/docs/security/e2ee.html).

## Installation

- Create a [virtual environment](https://docs.python.org/es/3/tutorial/venv.html) with the command

    ### windows
    `py -3 -m venv .venv`
    ### MacOS/Linux
    `python -m venv .venv` or `python3 -m venv .venv`

- Activate the virtual environment:

    ### In Linux or Mac:
    `source .venv/bin/activate`

    ### Windows:
    `.venv\scripts\activate` or `.venv\scripts\activate.bat`

    It should appear (venv) in the console. Whenever a new console is executed, the virtual machine has a libraries and dependencies other than those found in the normal Windows environment, this to maintain the integrity of the applications in the operating system.

    linux or mac `pip install --upgrade pip` or `python3 -m pip install --upgrade pip`
    windows `python -m pip install --upgrade pip` 

- Install dependencies

    #### Windows (may require elevation)
    `py -3 -m pip install -r requirements.txt`

     ### macOS/Linux
    `python -m pip install -r requirements.txt` or `python3 -m pip install -r requirements.txt`

    ### Linux (Debian)
    `apt-get install python3-tk`
    `python3 -m pip install m-r requirements.txt`

    use `python3 -m pip install --upgrade pip` if necessary.

## Execution

- With the virtual environment activated, run the following console command:

    `uvicorn app:app --reload --port 5000`

    in case you need to delete cache use

    `find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf`

    for root open `http://127.0.0.1:5000/`

    for swagger open `http://127.0.0.1:5000/docs`