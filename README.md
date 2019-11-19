# Extensions for Phenome AI

This repository is for all code and metadata extensions for the Phenome AI Platform. It contains the base system metadata needed in order to initialize the system in a default manner, as well as some basic OBJECT extensions needed by multiple projects.

Currently, it is organized into three main sections: META, CODE, and TOOLS. In the future this repo will may be broken up in to multiple, smaller repos, so it is important to keep things organized. 

It is pulled in during builds in order to build packages and run tests. If your Phenome project has some sharable (and testable) code, meta or tools that could be used by other projects, this is the place to put it.

Once you create a new project, you can clone this repo directly into a subdirectory named "phenome".

```
$ git clone https://github.com/holitics/phenome-extensions phenome
```

