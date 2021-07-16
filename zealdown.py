import argparse
import requests
import json
import os
import urllib.request
import urllib
from urllib.parse import urljoin
import sys

zealapi_url = 'http://api.zealdocs.org/v1/docsets'
usercontribution_url = 'https://zealusercontributions.vercel.app/api/docsets'
zealapi_cache_filename = 'docsets.json'
viable_source = None

source_candidates = [
    'singapore',
    'tokyo',
    'london',
    'newyork',
    'sanfrancisco',
    'frankfurt',
    'sydney',
    'mumbai',
    ''  # fallback
]

######## 网络访问相关

def is_accessible(url, timeout=5):
    try:
        r = requests.get(url, timeout=timeout)
    except Exception:
        return False
    return True

def get_source(city):
    if len(city) == 0: return 'https://kapeli.com'
    return 'https://' + city + '.kapeli.com'

def get_viable_source(timeout=5):
    if viable_source is not None:
        return get_source(viable_source)

    for city in source_candidates:
        if is_accessible(get_source(city)):
            viable_source = city
            return get_source(city)
        else:
            print('{} not accessible'.format(get_source(city)))
    print('Failed to find accessible source', file=sys.stderr)
    sys.exit(-1)

def prefixed_url(path):
    source = get_viable_source()
    return urljoin(source, path)

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
