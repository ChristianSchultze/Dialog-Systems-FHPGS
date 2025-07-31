# Dialog-Systems-FHPGS

## Setup
Install ollama on your system and make sure it is running in the background and you have the llama3 model downloaded.
https://ollama.com/download

Requirements for this python project can be installed via in the main directory:
````
pip install .
````

From now on the project can be used like any other python library.
Import project in python:
````
import satnews
````

## Usage

Running scarper script from console:

````
python -m satnews.scraper -d https:/example.com
````