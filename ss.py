#!/usr/bin/python

import argparse
import subprocess
from time import localtime, strftime, sleep
import sys, os


parser = argparse.ArgumentParser(description='Simple Scanner', fromfile_prefix_chars='@')

parser.add_argument('-R', help="resolution - default is R_default", default=200, type=int) 
parser.add_argument('-S', help="scanner type", default='net:localhost:fujitsu:fi-5120Cdj:162160')
parser.add_argument('-D', help="choose duplex scan", action="store_true")
parser.add_argument('-G', help="choose grayscale scan", action="store_true")
parser.add_argument('-B', help="Batch of <n> pages", default=1, type=int)
parser.add_argument('-L', help="gdrive label", default='home_filing')
parser.add_argument('-O', help="output file", default='Scan')
parser.add_argument('-T', help="temporary directory", default='/tmp/ss')
parser.add_argument('-d', help="just echo stuff don't do it", action="store_true")

parser.add_argument('-C', help="store in the cloud", action="store_true")
parser.add_argument('-E', help="email to an address", action='append')
parser.add_argument('-P', help="send to printer", action="store_true")

args = parser.parse_args()

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

if (args.D):
    DUPLEX="ADF Duplex"
    sheets = args.B * 2
else:
    DUPLEX="ADF Front"
    sheets = args.B

if (args.G):
    COLOURMODE="Gray"
else:
    COLOURMODE="Color"

thetime=strftime("%y%m%d-%H%M%S", localtime());

args.T = args.T + "/" + thetime + "/"
ensure_dir(args.T)

args.O = args.T + args.O + "-" + thetime + ".pdf"
scan_files = args.T + "scan-%d.tiff"

print "scanning to ", scan_files
print "Finally to ", args.O

scan_command=['sudo', 'scanimage', '-d' , args.S, '--batch=' + scan_files, '--swdespeck', '5', '--format=tiff'];
if (args.d):
    scan_command.insert(0,'echo')


success=False
for attempt in range(10):
    try:
        result = subprocess.check_output(scan_command + 
                                ['--resolution', `args.R`,
                                 '--mode', COLOURMODE,
                                 '--source', DUPLEX,
                                 '--batch-count', `args.B`],
                                stderr=subprocess.STDOUT)
        print result
    except subprocess.CalledProcessError as e:
        if e.returncode != 7: 
            print "Failed errorcode " + str(e.returncode) + "\n" + e.output
            success = False
            break
        sys.stdout.write("..." + `attempt`)
        sys.stdout.flush()
        sleep(1)
    else: 
        success=True
        break

if success == False:
    print "Failed damn it"
    exit(1)

#concatenate and format pages received

input_files = []
for i in range (0,sheets):
    input_files.append(scan_files % (i+1))

print "Converting and agjoining stuff"
print "Input files are ", input_files

convert_command =  ['convert', '-adjoin', '-compress', 'jpeg'] + input_files + [args.O]
if (args.d):
    convert_command.insert(0,'echo')

subprocess.call(convert_command)

if (args.C):
    cloud_command = ['/home/pi/gdu/gdu.py', args.O ];
    if (args.d):
        cloud_command.insert(0,'echo')
    subprocess.call(cloud_command + [args.L])

