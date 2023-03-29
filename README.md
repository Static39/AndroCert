# AndroCert
A system CA certificate installer for android(API>=24)
## Description
*A simple python script designed to convert .der CA certificates and install them to the system store on a rooted android device over ADB.*

Android 7.0(API>=24) introduced changes to the way apps handle CA certificates. Prior to this version apps would trust CA certificates added by the user.

   However, after this version apps will only trust certificates that are in the system store which isn't accessible without root. This added an additional
hurdle to proxying traffic on android due to the fact that you not only need root to add certificates to the system store, but the added certificates
have to be named in a very precise manner to be considered valid.

I designed this script to streamline the process of adding a new CA certificate to
a device without having to memorize all the openssl commands and directories where certificates are stored.

## Usage
```
python3 ./androcert -c cacert.der
```
## Requirements
* Python 3.6+
* [cryptography](https://pypi.org/project/cryptography/) package
* ADB installed and in PATH

## Setup
```
pip install cryptography
```
