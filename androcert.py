import sys
import os
import subprocess
import argparse
import hashlib
import warnings
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Creates the parser object
parser = argparse.ArgumentParser(
    prog='AndroCert', 
    description='Converts a security certificate in .der format to the format used by android\'s system store and installs to the device', 
    usage='%s -c cacert.der' % (sys.argv[0]))
parser.add_argument('-c', '--cert', help='The certificate to install', required=True)
parser.add_argument('-o', '--output', help='The path of the directory to output to', default='./')
parser.add_argument('-n', '--no_install', help='Do not install the certificate and just convert', action='store_true', default=False)
args = parser.parse_args()


### Certificate Modification ###

# Reads the certificate data
cert_file = open(args.cert, 'rb')
data = cert_file.read()
# Attempts to determine the type of the certificate
cert_type = 'pem' if data[0:27] == b'-----BEGIN CERTIFICATE-----' else 'der'
cert_file.close()

# Loads the certificate and calculates the MD5 hash of the subject
def certLoad():
    if cert_type == 'der':
        return x509.load_der_x509_certificate(data, default_backend())
    else:
        return x509.load_pem_x509_certificate(data, default_backend())
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    cert = certLoad()
    cert_hash = hashlib.md5(cert.subject.public_bytes()).digest()

# Ignores warning about country name being an incorrect amount of characters

# Calculates hash depending on CPU endianess (Probably a better way to achieve this)
if sys.byteorder == 'little':
    filename = bytearray(reversed(cert_hash[:4])).hex() + '.0'
else:
    filename = cert_hash[:4] + '.0'

# Serializes the certificate to PEM format
cert_bytes = cert.public_bytes(serialization.Encoding.PEM)

# Outputs the certificate to PEM with the filename being the prior calculated hash
filepath = args.output + '/' + filename
output_cert = open(filepath, 'wb')
output_cert.write(cert_bytes)
output_cert.close()

# Terminate if the no-install flag is present
if args.no_install:
    print('Certificate succesfully converted!')
    subprocess.run(['adb', 'kill-server'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sys.exit()


### ADB Commands ###

# Starts adb server and gets device list
subprocess.run(['adb', 'start-server'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
devices = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, text=True)


# Splits the output of the 'adb devices' command into a list and removes the extra lines
devices = devices.stdout.split('\n')[1:-2]

# If the number of devices is greater than 1 prompt the user to select one
if len(devices) > 1:
    print('Connected Devices')
    for index, device in enumerate(devices):
        print('({})* {}'.format(index + 1, device.split()[0]))
    # Casts the user's input as an integer and uses it as the index
    choose = int(input('Please choose a device (1-{}): '.format(len(devices)))) - 1
    target = devices[choose].split('\t')[0]
elif len(devices) < 1:
    print('No devices found')
    sys.exit()
else:
     target = devices[0].split('\t')[0]

# List of adb commands to run
adb_commands = [
    ['adb', '-s', target, 'root'],
    ['adb', '-s', target, 'remount'],
    ['adb', '-s', target, 'push', filepath, '/system/etc/security/cacerts/'],
    ['adb', '-s', target, 'shell', 'chmod 644 /system/etc/security/cacerts/{}'.format(filename)]
]

def cleanup():
    os.remove(filepath)
    subprocess.run(['adb', 'kill-server'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# Loops through the list of commands and runs them sequentially
for command in adb_commands:
    cmd = subprocess.run(command, text=True, stderr=subprocess.DEVNULL)
    if cmd.returncode != 0:
        cleanup()
        sys.exit()

# Prompts for a reboot
if input('Installed certificate successfully! A reboot is necessary to take effect. Reboot now?(y/n): ').lower() == 'y':
    subprocess.run(['adb', '-s', target, 'reboot'], stdout=subprocess.DEVNULL)

cleanup()
