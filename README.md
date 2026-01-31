# aep-example-python

An example AEP compliant API, written in Python

## Getting started

1. Install the requirements for this repository from `requirements.txt`.
2. Install this repository as an editable python package (e.g. `pip install -e .`)
3. Run the server (e.g. `aep-server`)

## Using the tools

You can install the command line tool with:

`go install github.com/aep-dev/aepcli/cmd/aepcli@main`

And then use it as an interactive API with:

`aepcli http://localhost:8000`

And you can save it as an configuration with the following:

`aepcli core config add example --openapi-path=http://localhost:8000/openapi.json`