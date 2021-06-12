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
K_x = '\u3131-\u318e' # Compatibility Jamo
K_RE = re.compile('(?:[' + K_a + '][' + K_b + '][' + K_c + ']?|[' + K_x + ']+)')

F_A = '\u115f' # choseong filler
F_B = '\u1160' # jungseong filler

def main(args):
	collection = {}
	collection_variants = {}

	def collect_variants(matchobj):
		#if matchobj.group(2) is not None:
		# does not work
		try:
			z_variant = matchobj.group(1)
			z_orthodox = matchobj.group(2)
		except:
			z_variant = '…'
			z_orthodox = matchobj.group(1)

		if not z_orthodox in collection_variants:
			collection_variants[z_orthodox] = []
		if not z_variant in collection_variants[z_orthodox]:
			collection_variants[z_orthodox].append(z_variant)

		return z_orthodox

	def format_pages(data):
		ret = []
		for ka, kb in data:
			ret_local = (ka or '-') + '/' + (kb or '-')
			for volume_and_page_number in data[(ka, kb)]:
				volume, page_number = volume_and_page_number.split('-')
				url = f'https://ko.wikisource.org/wiki/Page:重刊老乞大諺解_00{volume}.pdf/{page_number}'
				ret_local += f', <a href="{url}">{volume_and_page_number}</a>'
			ret.append(ret_local)
		return '<hr>'.join(ret)

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

				if args.collection:
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

						z = re.sub(r'(.+)\((.+)\)', collect_variants, z) # XXX
						z = re.sub(r'{{' + unicodedata.normalize('NFD', '이체자') + '\|(.*?)\|(.*?)}}', collect_variants, z) # XXX
						z = re.sub(r'{{' + unicodedata.normalize('NFD', '이체자') + '\|(.*?)}}', collect_variants, z) # XXX

						if not z in collection:
							collection[z] = {}

						if not k_corrected in collection[z]:
							collection[z][k_corrected] = {}

						if not k_uncorrected in collection[z][k_corrected]:
							collection[z][k_corrected][k_uncorrected] = []

						#collection[z][k_corrected][k_uncorrected].append(path)
						collection[z][k_corrected][k_uncorrected].append(re.sub(r'.+(\d)\/(\d+)$', r'\1-\2', path)) # XXX

	if args.collection == 'text':
		for z in sorted(collection):
			if (len(collection[z]) > 1 if args.paeumja else True):
				print(z)
				for k_corrected in sorted(collection[z]):
					k_variant_count = len(collection[z][k_corrected]) if len(collection[z][k_corrected]) > 1 else ''
					print('\t' + str(k_corrected) + '\t' + str(k_variant_count) + str(collection[z][k_corrected]))
	elif args.collection == 'html':
		from yattag import Doc
		doc, tag, text, line = Doc().ttl()
		doc.asis('<!DOCTYPE html>')
		with tag('html'):
			with tag('head'):
				with tag('meta', ('charset', 'utf-8')):
					pass
			with tag('body'):
				with tag('script', ('src', 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.slim.min.js')):
					pass
				with tag('script', ('src', 'https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/js/jquery.tablesorter.min.js')):
					pass
				with tag('script', ('src', 'https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/js/widgets/widget-filter.min.js')):
					pass
				with tag('script', ('src', 'https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/js/widgets/widget-cssStickyHeaders.min.js')):
					pass
				doc.stag('link', ('href', 'https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/css/theme.blue.min.css'), ('rel', 'stylesheet'))

				with tag('script'):
					text("""
						document.addEventListener('DOMContentLoaded', function() {
							$('#MYTABLE').tablesorter({
								theme: 'blue',
								 widgets: ['filter', 'cssStickyHeaders'],
							});

							/*
							$('.tablesorter-filter-row td[data-column=1]').attr('colspan', 5);
							$('.tablesorter-filter-row td[data-column=2]').remove();
							$('.tablesorter-filter-row td[data-column=3]').remove();
							$('.tablesorter-filter-row td[data-column=4]').remove();
							$('.tablesorter-filter-row td[data-column=5]').remove();
							// ----
							$('.tablesorter-filter-row td[data-column=6]').attr('colspan', 5);
							$('.tablesorter-filter-row td[data-column=7]').remove();
							$('.tablesorter-filter-row td[data-column=8]').remove();
							$('.tablesorter-filter-row td[data-column=9]').remove();
							$('.tablesorter-filter-row td[data-column=10]').remove();
							*/
						});
					""")
				with tag('style'):
					text("""
						body {
							font-family: 'nanumbarungothic yethangul', sans-serif;
							font-size: 150%;
						}
						.tablesorter-blue th, .tablesorter-blue thead td {
							font: inherit;
						}
						td.no-jungseong {
							background-color: rgba(0, 0, 0, 0.1);
							color: white;
						}
						td.pages {
							font-size: 50%;
						}
					""")

				with tag('table', ('id', 'MYTABLE'), ('class', 'tablesorter tablesorter-blue')):
					with tag('thead'):
						with tag('tr'):
							with tag('th', ('colspan', 2)):
								text('字')
							with tag('th', ('colspan', 5)):
								text('俗音(校正畢)')
							with tag('th', ('colspan', 5)):
								text('正音(校正畢)')
							with tag('th', ('rowspan', 2)):
								text('俗(原文)/正(原文), 上下補-No')
						with tag('tr'):
							with tag('th'):
								text('正')
							with tag('th'):
								text('別')
							with tag('th'):
								text('俗')
							with tag('th',):
								text('初')
							with tag('th',):
								text('中')
							with tag('th',):
								text('終')
							with tag('th',):
								text('韻')
							with tag('th'):
								text('正')
							with tag('th',):
								text('初')
							with tag('th',):
								text('中')
							with tag('th',):
								text('終')
							with tag('th',):
								text('韻')
					with tag('tbody'):
						for z in sorted(collection):
							if (len(collection[z]) > 1 if args.paeumja else True):
								i = 0
								while i < len(collection[z]):
									for k_corrected in sorted(collection[z]):
										with tag('tr'):
											#if i == 0:
												#with tag('th', ('rowspan', len(collection[z]))):
													#text(z)
											# rowspan not supported by tablesorter

											line('th', z)
											line('th', '<hr>'.join(collection_variants[z]) if z in collection_variants else '')
											# ----
											line('td', k_corrected[0])
											line('td', k_corrected[0][0] + F_B)
											line('td', F_A + k_corrected[0][1])
											jungseong = (F_A + F_B + k_corrected[0][2]) if len(k_corrected[0]) == 3 else '-'
											with tag('td', ('class', 'no-jungseong' if jungseong == '-' else '')):
												text(jungseong)
											line('td', F_A + k_corrected[0][1:])
											# ----
											line('td', k_corrected[1])
											line('td', k_corrected[1][0] + F_B)
											line('td', F_A + k_corrected[1][1])
											jungseong = (F_A + F_B + k_corrected[1][2]) if len(k_corrected[1]) == 3 else '-'
											with tag('td', ('class', 'no-jungseong' if jungseong == '-' else '')):
												text(jungseong)
											line('td', F_A + k_corrected[1][1:])
											# ----
											with tag('td', ('class', 'pages')):
												text(format_pages(collection[z][k_corrected]))
											# ----
											i += 1

		print(doc.getvalue().replace('&lt;', '<').replace('&gt;', '>'))

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
		choices = ['text', 'html'],
		help = 'collect data, and export as text/html',
	)
	parser.add_argument(
		'-p',
		dest = 'paeumja',
		action = 'store_true',
		help = 'only print 破音字',
	)
	args = parser.parse_args()

	main(args)
