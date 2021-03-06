# TRiver
A Torrent viewer

#### Description

A Torrent viewer for Linux(GTK) and Windows(Tkinter)

When phosh for pinephone fixes the GTK dialogs then you will be able to use it on pinephone

#### License
GPLv3 - [read here](https://github.com/Frankmau5/TRiver/blob/main/LICENSE)

#### Install

Install for Linux Desktop

`flatpak --user install triver-x86-64-v1.0.0.flatpak`

For Windows

clone project and got tot the windows folder in the src folder.
run the requirements.txt file with pip

`pip install -r requirements.txt`

then just double click on the TRiver_windows.py
#### Build

For Linux 

`flatpak-builder --repo=myrepo _flatpac  mlv.knrf.TRiver.json`

`flatpak build-bundle  myrepo pastebinReader.flatpak mlv.knrf.TRiver`

#### Usage

There should be a desktop entry in your luncher. You might want to try to logout.

you can run in the terminal.

`flatpak run mlv.krnf.triver` 


For Windows 
just double click on the TRiver_windows.py  
