@TODO store this in a separate repo as per https://stackoverflow.com/a/43729803

# How Plugins Work

Plugins are configured in settings.json, like so:

```
{
  ...,
  "plugins": {
    "file_refs": "pluging_source_file_name",
    "vendor_reports": "other_pluging_source_file_name"
  }
}
```
The plugin source file names must match `.py` files in the `plugins` folder. Each file must contain a `Plugin` class that implements a `apply(data)` method.

The report building will call the `apply()` with the raw report data (in the form of a dict). The method must return the transformed (or not) data.

The `file_refs` plugin will be applied to file references.

The `vendor_reports` plugin will be applied to all reports from vendors (from a single input).
