# Entre Guillemets: compare natural language processing APIs

Run a corpus of text files through multiple natural language processing (NLP) API vendors. View API results side by side so that you can get a general feel for how well each vendor works for your use case. Supported vendors: TextRazor, Google Cloud, IBM Watson and Rosette.

Entre Guillemets is greatly inspired by [Cloudy Vision](https://github.com/goberoi/cloudy_vision) which meets the same types of objectives, but for computer vision APIs.

See [example results here](https://projet-tamis.github.io/entre-guillemets/report/).

## Installation

Entre Guillemets works with Python 3.6. If using Anaconda, you can first:

```bash
source activate py36
```

Install dependencies by running

```bash
pip install -r requirements.txt
```

Copy `settings.dist.json` to `settings.json` and add you API credentials.


## Running

Running and getting results is simply

```bash
python pg.py
```

This will process all text files (`.txt` extension) in `input_files` and store the results in `output`.

## Annotating input files for some context

You can also provide context information or metadata about each input file (eg. title, reference number, tags, etc.) to display in the output report. Simply include those in JSON by creating a file with the same name as the input file, by adding `.json` to its name (so the metadata for `some_file.txt` would be in `some_file.txt.json`).

## Vendor specific notes

### Rosette

Text in truncated to 50 000 characters in order to respect Rosette's limit.

Categories and Topics extractions are not benchmarked because they are available in English only.

The Rosette entity output includes a confidence score _for some_ entities, and not for others. The report separates entities with confidence (sorted by reverse confidence value) and without confidence information (sorted by number of occurrences).

### Google

Classification is not benchmarked because it is available in English only.

### TextRazor

Text in truncated to 200kb in order to respect TextRazor's limit.
