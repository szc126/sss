#!/usr/bin/env python3
import argparse
import re # XXX
import regex
import sys
import unicodedata

# TODO: check for SIC content being identical

Z_RE = r'(?:(?:\p{Hani}|[⿰-⿻][^()]+)(?:\(\p{Hani}\))?)'

K_a = '\u1100-\u115f' + '\ua960-\ua97c' # Jamo + Jamo Ext-A (Unicode 13.0)
K_b = '\u1160-\u11a7' + '\ud7b0-\ud7c6' # Jamo + Jamo Ext-B
K_c = '\u11a8-\u11ff' + '\ud7cb-\ud7fb' # Jamo + Jamo Ext-B
K_RE = re.compile('(?:[' + K_a + '][' + K_b + '][' + K_c + ']?)')

def main(args):
	collection = {}

	for path in args.paths:
		with open(path, mode = 'r', encoding = 'utf-8') as file:
			text = file.read()
			text = unicodedata.normalize('NFD', text)
			text = re.sub(r'<!--(.*?)-->', r'', text)
			text = re.sub(r'{{SIC\|([^|{}]+)}}', r'\1', text) # book 2, page 85, 非 /ㅸ/

			for chunk in re.finditer(r';(.+)\n:(.+)\n:(.+)', text):
				line_z, line_ka, line_kb = chunk[1], chunk[2], chunk[3]
				line_z              = re.sub(r'{{SIC\|([^|{}]+)\|([^|{}]+)}}', r'\2', line_z)
				line_ka_uncorrected = re.sub(r'{{SIC\|([^|{}]+)\|([^|{}]+)}}', r'\1', line_ka)
				line_ka_corrected   = re.sub(r'{{SIC\|([^|{}]+)\|([^|{}]+)}}', r'\2', line_ka)
				line_kb_uncorrected = re.sub(r'{{SIC\|([^|{}]+)\|([^|{}]+)}}', r'\1', line_kb)
				line_kb_corrected   = re.sub(r'{{SIC\|([^|{}]+)\|([^|{}]+)}}', r'\2', line_kb)

				found_z = regex.findall(Z_RE, line_z)
				found_ka_uncorrected, found_ka_corrected = re.findall(K_RE, line_ka_uncorrected), re.findall(K_RE, line_ka_corrected)
				found_kb_uncorrected, found_kb_corrected = re.findall(K_RE, line_kb_uncorrected), re.findall(K_RE, line_kb_corrected)

				if args.consistency_check:
					if len(found_z) != len(found_ka_uncorrected):
						print('A', path, line_z, line_ka_uncorrected)
						print('\t'.join(found_z))
						print('\t'.join(found_ka_uncorrected))
					if len(found_z) != len(found_kb_uncorrected):
						print('B', path, line_z, line_kb_uncorrected)
						print('\t'.join(found_z))
						print('\t'.join(found_kb_uncorrected))
				else:
					for i in range(len(found_z)):
						z = found_z[i]
						k_corrected = (
							found_ka_corrected[i],
							found_kb_corrected[i],
						)
						k_uncorrected = (
							found_ka_uncorrected[i] if found_ka_uncorrected[i] != found_ka_corrected[i] else '',
							found_kb_uncorrected[i] if found_kb_uncorrected[i] != found_kb_corrected[i] else '',
						)

						z = re.sub(r'(.+)\((.+)\)', r'\2', z) # XXX

						if not z in collection:
							collection[z] = {}

						if not k_corrected in collection[z]:
							collection[z][k_corrected] = {}

						if not k_uncorrected in collection[z][k_corrected]:
							collection[z][k_corrected][k_uncorrected] = []

						#collection[z][k_corrected][k_uncorrected].append(path)
						collection[z][k_corrected][k_uncorrected].append(re.sub(r'.+(\d)\/(\d+)$', r'\1-\2', path)) # XXX

	if args.collection:
		if args.paeumja:
			for z in sorted(collection):
				if len(collection[z]) > 1:
					print(z)
					for k_corrected in sorted(collection[z]):
						k_variant_count = len(collection[z][k_corrected]) if len(collection[z][k_corrected]) > 1 else ''
						print('\t' + str(k_corrected) + '\t' + str(k_variant_count) + str(collection[z][k_corrected]))
		else:
			for z in sorted(collection):
				print(z)
				for k_corrected in sorted(collection[z]):
					k_variant_count = len(collection[z][k_corrected]) if len(collection[z][k_corrected]) > 1 else ''
					print('\t' + str(k_corrected) + '\t' + str(k_variant_count) + str(collection[z][k_corrected]))

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'paths',
		nargs = '+',
	)
	parser.add_argument(
		'-C',
		dest = 'consistency_check',
		action = 'store_true',
		help = 'perform consistency checks on the data',
	)
	parser.add_argument(
		'-c',
		dest = 'collection',
		action = 'store_true',
		help = 'print collection',
	)
	parser.add_argument(
		'-p',
		dest = 'paeumja',
		action = 'store_true',
		help = 'only print 破音字',
	)
	args = parser.parse_args()

	main(args)
