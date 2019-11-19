# Extensions for Phenome AI

This repository is for all shared extensions for the Phenome AI Platform. It contains the base system metadata needed in order to initialize the system in a default manner, basic OBJECT extensions needed by multiple projects, some standard web assets for the embedded agent UI, and a growing set of tools.

Currently, it is organized into three main sections: CONFIG (metadata is here), EXTENSIONS (code is here), STATIC (web assets) and TOOLS. In the future this repo may be broken up in to multiple, smaller repos, so it is important to keep things organized. 

This entire repo is pulled in during builds in order to make packages and run tests. If your Phenome project has some sharable (and testable) code, libraries, meta or tools that could be used by other projects, this could be the place to put it.

## Getting started

Once you create a new project, you can clone this repo directly into a subdirectory named "phenome".

```
$ git clone https://github.com/holitics/phenome-extensions phenome
```

