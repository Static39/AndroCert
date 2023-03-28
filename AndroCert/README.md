# AndroCert
A system CA certificate installer for android
## Description
A simple python script designed to convert .der CA certificates and install them to the system store on a rooted android device over ADB.

## Usage
```
python3 ./androcert -c cacert.der
```
## Requirements
* Python 3.6+
* `cryptography` python3 package
* ADB installed and in PATH

## Setup
```
pip install cryptography
```
