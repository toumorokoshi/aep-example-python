# aep-example-python

An example AEP compliant API, written in Python

## Prequisites

- [uv](https://github.com/astral-sh/uv).
- [spectral](https://github.com/stoplightio/spectral).

## Starting the server

The example server can be started with the following command:

`uv run aep-server`

## Command line tools with aepcli

You can install the command line tool with:

`go install github.com/aep-dev/aepcli/cmd/aepcli@main`

And then use it as an interactive API with:

`aepcli http://localhost:8000`

And you can save it as an configuration with the following:

`aepcli core config add example --openapi-path=http://localhost:8000/openapi.json`

## using ui.aep.dev

You can use [ui.aep.dev](https://ui.aep.dev) to navigate the API through a web interface.


