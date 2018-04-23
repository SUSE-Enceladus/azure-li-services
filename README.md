# azure-li-services - Azure Large Instance Services

[![Build Status](https://travis-ci.org/SUSE/azure-li-services.svg?branch=master)](https://travis-ci.org/SUSE/azure-li-services)

Systemd services reading and processing the sections of a
configuration file provided to the system during the startup
phase of an Azure Large or Very Large Instance.

## Contents

  * [Contributing](#contributing)

## Contributing

The Python project uses `tox` to setup a development environment
for the desired Python version.

The following procedure describes how to create such an environment:

1.  Let tox create the virtual environment(s):

    ```
    $ tox
    ```

2.  Activate the virtual environment

    ```
    $ source .tox/3/bin/activate
    ```

3.  Install requirements inside the virtual environment:

    ```
    $ pip install -U pip setuptools
    $ pip install -r .virtualenv.dev-requirements.txt
    ```

4.  Let setuptools create/update your entrypoints

    ```
    $ ./setup.py develop
    ```

Once the development environment is activated and initialized with
the project required Python modules, you are ready to work.

In order to leave the development mode just call:

```
$ deactivate
```

To resume your work, change into your local Git repository and
run `source .tox/3/bin/activate` again. Skip step 3 and 4 as
the requirements are already installed.
