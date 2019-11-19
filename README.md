# Extensions for Phenome AI

This repository is for all shared extensions for the Phenome AI Platform. It contains the base system metadata and code needed in order to initialize the system in a default manner (including a basic `__init__.py` file), OBJECT extensions and libraries needed by multiple projects, some standard web assets for the embedded agent UI, all the shared UNIT TEST framework files, and a growing set of tools.

This entire repo is pulled in during builds in order to make packages and run tests. If your Phenome project has some sharable (and testable) code, libraries, meta or tools that could be used by other projects, this is the place to put it.

## Repo Structure

Currently, it is organized into several different areas:

| Area          | Location                  |Description |  
|:---           |:--------------------------|:-------------------           |  
| META          | `/config/meta`              | Metadata in JSON format       |
| CODE          | `/extensions`               | Objects, Actions, SensorChecks, 3rd party libs and wrappers   |
| STATIC        | `/static`                   | Web assets including templates, css, javascript, images|
| TESTS         | `/test`                     | Shared test framework including specific tests for extensions|
| TOOLS         | `/tools`                    | Various tools used for apps, unit tests, etc.|


## Getting started

Once you create a new project, you can clone this repo directly into a subdirectory named "phenome".

```
$ git clone https://github.com/holitics/phenome-extensions phenome
```

