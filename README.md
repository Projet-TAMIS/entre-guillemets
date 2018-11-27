# Entre Guillemets: compare natural language processing APIs

Run a corpus of text files through multiple natural language processing (NLP) API vendors. View API results side by side so that you can get a general feel for how well each vendor works for your use case. Supported vendors: ...

Entre Guillemets is greatly inspired by [Cloudy Vision](https://github.com/goberoi/cloudy_vision) which meets the same types of objectives, but for computer vision APIs.

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

## Vendor specific notes

### Rosette

Text in truncated to 50 000 characters in order to respect Rosette's limit.

Categories and Topics extractions are not benchmarked because they are available in English only.

The Rosette entity output includes a confidence score _for some_ entities, and not for others. The report separates entities with confidence (sorted by reverse confidence value) and without confidence information (sorted by number of occurrences).

### Google

Classification is not benchmarked because it is available in English only.

# TODO

[x] Create settings.json.dist and instructions
[ ] Add more vendors
[ ] Add TOC to vendor report
[ ] Add metrics to vendor report
[ ] Create an aggregated report for all vendors and a way to compare features accross vendors
