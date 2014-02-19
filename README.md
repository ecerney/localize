localize.py
========

Localization Tool for iOS


###Installation:
Simply download the file either to the project you want to localize, or anywhere you can run the script from.

If you want to use it system wide place it in ```/usr/local/bin``` and make sure it's executable: ```chmod+x localize.py```
###Usage:
```
usage: ./localize.py [-h] [-v] {generate,replace} ...
```

###Arguments:

```
optional arguments:
  -h, --help          show this help message and exit
  -v, --verbose       increase output verbosity

subcommands:
  valid subcommands

  {generate,replace}
    generate          Used to generate localization files optionally combining
                      them with previous translations
    replace           Replaces existing Localization files with their new
                      matching file
```

###Subcommands:

####generate:
```
usage: ./localize.py generate [-h] [-n] [-e EXISTING] [-i INPUT] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -n, --new             Creates brand new Localization file from source code
  -e EXISTING, --existing EXISTING
                        Creates new Localization file(s) for each existing
                        file in the app
  -i INPUT, --input INPUT
                        Project folder path or individual file
  -o OUTPUT, --output OUTPUT
                        Output file/folder path
```

####replace:
```
usage: ./localize.py replace [-h] output input

positional arguments:
  output      Output file/folder path
  input       Project folder path or individual file

optional arguments:
  -h, --help  show this help message and exit
```  
  
  
##License

The MIT License (MIT)

Copyright (c) 2014 ecerney

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
