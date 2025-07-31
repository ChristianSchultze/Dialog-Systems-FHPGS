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

### Satirical News Agent
Main news agent with conversation possible over the command line. Requires already matched data. Depending on the 
context length, the number of articles has to be limited.
````
python -m satnews.summarizer -p onion_matched_data_sports.lzma -l 15
````

### Preprocessing
Attention! The provided file name is always the name of the original scraped file and then automatically modified down the line.
All preprocessing scripts have the option to limit the number of processed articles with "-l".
Running Matcher with specific topic. Requires synthesized output. This is an example line for the file "onion_satire_output.lzma".
````
python -m satnews.matcher --topic "Sports, Baseball, Football" -p onion.lzma
````

Running Synthesizer.
````
python -m satnews.satire_synthesizer -p onion.lzma
````

Running Retriever.
````
python -m satnews.satire_retriever -p onion_data_2.lzma
````

Running scarper.
````
python -m satnews.scraper -d https:/example.com
````

### Real News Searcher

### Image and Audio

Running media analysis script from console:

The `analyze_image_audio.py` script currently runs with hardcoded example image and YouTube URLs. To execute it from the console:

python -m satnews.analyze_image_audio


(Note: For dynamic input of image, YouTube, or audio URLs, the `analyze_image_audio.py` script would need modifications to accept command-line arguments, similar to how `scraper.py` uses `-d` for domain.)
```
