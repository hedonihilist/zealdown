import argparse
import json
import os
import urllib.request
import urllib
import sys

zealapi_url = 'http://api.zealdocs.org/v1/docsets'
zealapi_cache_filename = 'docsets.json'

valid_source = [
        'singapore',
        'tokyo',
        'london',
        'newyork',
        'sanfrancisco',
        'frankfurt',
        'sydney',
        'mumbai'
    ]


def get_download_url(source, docset_name):
    return 'http://{}.kapeli.com/feeds/{}.tgz'.format(source, docset_name)


def get_docset_list():
    docsets = None
    if os.path.exists(zealapi_cache_filename):
        with open(zealapi_cache_filename, 'r') as f:
            return json.load(f)
    else:
        try:
            data = urllib.request.urlopen(zealapi_url)
            docsets = json.loads(data.read())
        except BaseException as e:
            print(e, file=sys.stderr)
            print('failed to fetch docset list from zealdocs.org', file=sys.stderr)
            sys.exit(-1)
    with open(zealapi_cache_filename, 'w') as f:
        json.dump(docsets, f);
    return docsets


def get_valid_docset_names(docset_list):
    return [docset['name'] for docset in docset_list]


def download_and_save(url, filename, show_progress=True):
    def progress(chunk_i, chunk_num, total_size):
        sys.stdout.write('\r{} [{}/{}]'.format(filename, chunk_i, chunk_num))
        #print('%d/%d %d' % (chunk_i, chunk_num, total_size))

    urllib.request.urlretrieve(url, filename, progress)

def parse_args():
    parser = argparse.ArgumentParser()
    # flags
    parser.add_argument('--print-download-url',
            action='store_true', help='print the download urls of the given docsets')
    parser.add_argument('--print-zeal-docsets',
            action='store_true', help='print names of the docset in zealdoc.org')
    parser.add_argument('--no-extract',
            action='store_true', help='just download. dont extract the docsets')

    # args
    parser.add_argument('--name', help='name of the docset to be downloaded')
    parser.add_argument('--docset-dir', help='the dir where Zeal stores docsets')
    parser.add_argument('--get-icon', help='get icons of the docsets')
    parser.add_argument('--source', help='download from which source', default='singapore')

    return parser.parse_args()


def main():
    args = parse_args()
    if args.print_download_url:
        docsets = get_docset_list()
        for docset in docsets:
            print(get_download_url(args.source, docset['name']))


if __name__ == '__main__':
    main()
