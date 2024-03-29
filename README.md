# Blackrock Microsystem Data Loader for Python
## Version: 0.0.1

The BlackRock Microsofts NSX and NEV loader for Python

### Requirements
- tested at Python 3.7.6 only

### Installation
```angular2html
pip install bmloader
```

### Command line tool
- Help function
```angular2html
brkraw -h
```

- Print out summary of the scan
```angular2html
brkraw summary <session path>
```

- Convert a whole session
```angular2html
brkraw tonii <session path>
```

- Convert only one scan in the session
```angular2html
brkraw tonii <session path> -s <scan id> -r <reco id>
```

- If <reco id> is not provided, then default is 1

- To convert all raw data under the folder. This command will scan all folder under the parent folder and the derived file will be structured as BIDS
```angular2html
brkraw tonii_all <parent folder>
```