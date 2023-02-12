# Changelog
## Version 1.0.1
- Formatted some of the variable names for readability
## Version 1.0.2
- Fixed a bug in `--resolve` where on printing a field in a `CONSTANT` which was `CONSTANT_Utf8`, it wasn't reduced to just the `bytes` field on it
- Fixed having the index in `--edit` increase by 1
- Added `--hex` allowing you to view indices in hex instead of base-10