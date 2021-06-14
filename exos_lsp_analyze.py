#!/usr/bin/env python3

import subprocess
import sys
import re
import time
from pprint import pprint


def vpn(node, vpn_name):
	directory = f'~/Downloads/{node}.cfg'
	'''regular expressions'''
	regex_ip = re.compile('.*peer ((\w+.){3}(\w+))')
	regex_lsp = re.compile('.* lsp "(\S+)" .*')
	'''looking for all peers of vpn'''
	peers = subprocess.run([f'grep "l2vpn.*{vpn_name}.*peer" {directory}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
	peers = peers.stdout.split('\n')
	lsps_of_vpn = []
	for i in peers:
		match = re.match(regex_ip, i)
		if match:
			out = subprocess.run([f'grep "rsvp-te.*destin" {directory} | grep {match.group(1)}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')	
			out = out.stdout.split('\n')
			for i in out:
				match_lsp = re.match(regex_lsp, i)
				if match_lsp:
					lsps_of_vpn.append(match_lsp.group(1))
	result_vpn = dict()
	for lsps in lsps_of_vpn:
		result_vpn.update(lsp(node, lsps))
	return result_vpn


def lsp(node, lsp_name):
	directory = f'~/Downloads/{node}.cfg'
	regex_path = re.compile('.*add path "*(\S+?)"* .*')
	out = subprocess.run([f'grep "rsvp-te.*add path" {directory} | grep {lsp_name}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')	
	out = out.stdout.split('\n')
	paths = []
	for path1 in out:
		match = re.match(regex_path, path1)
		if match:
			paths.append(match.group(1))
	result = {}
	for path1 in paths:
		hops = path(node, path1)
		result[path1] = hops
	lsp = {}
	lsp[lsp_name] = result	
	return lsp

	
def path(node, path_name):
	directory = f'~/Downloads/{node}.cfg'
	regex_hops = re.compile('.*ero include ((\w+.){3}(\w+))\/(\w+) .*(order \w+)')
	hops2 = subprocess.run([f'grep "rsvp-te.*add ero" {directory} | grep {path_name}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
	hops2 = hops2.stdout.split('\n')
	ips = []
	for ip in hops2:	
		match = re.match(regex_hops, ip)
		if match:
			ips.append(match.group(1))
	return resolve_ip(node, ips)
	
		
def resolve_ip(node, ips_to_resolve):
	directory = f'~/Downloads/{node}.cfg'
	regex_name = re.compile('.*pointer (\S+?-\S+?-\S+?..)')
	regex_lo0 = re.compile('.*lo0 ipaddress ((\w+.){3}(\w+)).*')
	hops3 = []			
	for ip in ips_to_resolve:
		domain_name = subprocess.run([f'host {ip}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
		time.sleep(0.1)
		lo0 = subprocess.run([f'grep "lo0 ipaddress" {directory}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
		match_dn = re.match(regex_name, domain_name.stdout)
		match_lo0 = re.match(regex_lo0, lo0.stdout)
		if match_dn:
			hops3.append(f'{match_dn.group(1)}, ip {ip}, lo0 no')
		else:
			hops3.append(f'no name, ip {ip}, lo0 no')
	return hops3
	

if __name__ == "__main__":
	'''objects to check:
		-vpn (vpls and vpws)
		-lsp (rsvp-te and ldp)
		-paths
		and hops resolving
	'''
	#make keys option to choose vpn/lsp/path/hop obj
	#add hop ip and lo0 ip info when resolving
	#check vpn section (too slow)
	#add extended mode (to check ldp)
	
	node = sys.argv[1]
	obj_for_analisys = sys.argv[2]
	obj_name = sys.argv[3]

	
	if obj_for_analisys == 'v':
		pprint(vpn(node, obj_name), width=120)
	if obj_for_analisys == 'l':
		pprint(lsp(node, obj_name), width=120)
	if obj_for_analisys == 'p':
		pprint(path(node, obj_name), width=120)
	if obj_for_analisys == 'h':
		pprint(resolve_ip(node, obj_name), width=120)