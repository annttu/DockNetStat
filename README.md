DockNetStat
==========

DockNetStat is OS X dock application to show network connection status.


Usage
=====

Start server.py on remote server. Address can be configured using --address 
and port using --port command line options. Server does not currently fork to
background so start it in screen or tmux window.

    screen -mdS python2.7 ./server.py --address X.X.X.X --port YYYYY

Configure server address and port on app.py

Make application using command

    make

Start application:

    open Applications/DockNetStat.app

Optionally copy Application to /Applications

    cp Applications/DockNetStat.app /Applications/DockNetStat.app


Author
======

* Antti 'Annttu' Jaakkola

License
=======

The MIT License (MIT)

Copyright (c) 2013 Antti Jaakkola

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
