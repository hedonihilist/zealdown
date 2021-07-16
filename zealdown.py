#!/usr/bin/env python3
import argparse
import tarfile
import requests
import json
import os
import re
import urllib.request
import urllib
from urllib.parse import urljoin
import sys

zealapi_url = 'https://api.zealdocs.org/v1/docsets'
zealapi_cache_filename = 'docsets.json'
usercontribution_url = 'https://zealusercontributions.vercel.app/api/docsets'
usercontribution_cache_filename = 'user-docsets.json'
zealdocsets = None
userdocsets = None
viable_source = None

source_candidates = [
    '',
    'singapore',
    'tokyo',
    'london',
    'newyork',
    'sanfrancisco',
    'frankfurt',
    'sydney',
    'mumbai',
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
    global viable_source
    if viable_source is not None:
        return get_source(viable_source)

    for city in source_candidates:
        if is_accessible(get_source(city)):
            viable_source = city
            print('Found viable source: {}'.format(get_source(city)))
            return get_source(city)
        else:
            print('{} not accessible'.format(get_source(city)))
    print('Failed to find accessible source', file=sys.stderr)
    sys.exit(-1)

def prefixed_url(path):
    path = re.sub('^https?://.*kapeli.com', '', path)
    print(path)
    source = get_viable_source()
    return urljoin(source, path)

def get_download_url_of_docset(docset):
    if 'urls' in docset and len(docset['urls']) != 0:
        return prefixed_url(docset['urls'][0])
    if 'author' in docset:
        # assume it's a user docset
        return prefixed_url('/feeds/zzz/user_contributed/build/{}/{}.tgz'.format(docset['name'], docset['name']))
    else:
        return prefixed_url('/feeds/{}.tgz'.format(docset['name']))

def get_docset_list(enable_cache):
    docsets = None
    if enable_cache and os.path.exists(zealapi_cache_filename):
        with open(zealapi_cache_filename, 'r') as f:
            return json.load(f)
    try:
        data = urllib.request.urlopen(zealapi_url)
        docsets = json.loads(data.read())
    except BaseException as e:
        print(e, file=sys.stderr)
        print('failed to fetch docset list from zealdocs.org', file=sys.stderr)
        sys.exit(-1)
    if enable_cache:
        with open(zealapi_cache_filename, 'w') as f:
            json.dump(docsets, f)
    return docsets

def get_user_docset_list(enable_cache):
    docsets = None
    if enable_cache and os.path.exists(usercontribution_cache_filename):
        with open(usercontribution_cache_filename, 'r') as f:
            return json.load(f)
    try:
        data = urllib.request.urlopen(usercontribution_url)
        docsets = json.loads(data.read())
    except Exception as e:
        print(e, file=sys.stderr)
        print('failed to fetch user contributions', file=sys.stderr)
        sys.exit(-1)
    if enable_cache:
        with open(usercontribution_cache_filename, 'w') as f:
            json.dump(docsets, f)
    return docsets

def download_and_save(url, filename, show_progress=True):
    print('downloading {}'.format(url))
    def progress(chunk_i, chunk_num, total_size):
        sys.stdout.write('\r{} [{}/{}]'.format(filename, chunk_i, chunk_num))
        #print('%d/%d %d' % (chunk_i, chunk_num, total_size))
    urllib.request.urlretrieve(url, filename, progress)

def print_docset(docset):
    print(f'Name: {docset["name"]}')

def get_docset_dict(docset_list):
    return {docset['name']:docset for docset in docset_list}

def do_search(args):
    pattern = re.compile(args.doc_pattern)
    print('Search result in Official docsets:')
    for docset in zealdocsets:
        if pattern.findall(docset['name'].lower()) or ('title' in docset and pattern.findall(docset['title'].lower())):
            print_docset(docset)
    if userdocsets:
        print('Search result in user docsets:')
        for docset in userdocsets:
            if pattern.findall(docset['name'].lower()) or ('title' in docset and pattern.findall(docset['title'].lower())):
                print_docset(docset)

def extract_docset(docset_tar_path, dest_path):
    with tarfile.open(docset_tar_path, 'r:gz') as tarobj:
        for tarinfo in tarobj:
            tarobj.extract(tarinfo.name, dest_path)

def do_install(args):
    dict1 = get_docset_dict(zealdocsets)
    if args.user:
        dict1.update(get_docset_dict(userdocsets))
    for docset_name in args.doc_names:
        if docset_name in dict1:
            docset = dict1[docset_name]
            dest_dir = os.path.expanduser(args.dest)
            print(dest_dir)
            try:
                print('Downloading "{}"'.format(docset_name))
                tar_path = download_to_dir(docset, dest_dir)
                print('Extracting "{}"'.format(docset_name))
                extract_docset(tar_path, dest_dir)
                # remove the downloaded tar 
                os.remove(tar_path)
                print('"{}" installed'.format(docset_name))
            except Exception as e:
                print('Error: {}'.format(e), file=sys.stderr)
                continue
        else:
            print('{} not in docset list. Skip.'.format(docset_name))

def download_to_dir(docset, path):
    """
    download docset to dir and return path
    file will not be created if interrupted
    """
    temp_path = os.path.join(path,docset['name']+'.tgz-temp')
    download_and_save(get_download_url_of_docset(docset), temp_path)
    target_path = temp_path.replace('tgz-temp', 'tgz')
    os.rename(temp_path, target_path)
    return target_path

def do_download(args):
    print('docsets to download: {}'.format(args.doc_names))
    dict1 = get_docset_dict(zealdocsets)
    if args.user:
        dict1.update(get_docset_dict(userdocsets))
    for docset_name in args.doc_names:
        if docset_name in dict1:
            docset = dict1[docset_name]
            try:
                target_path = download_to_dir(docset, args.dest)
            except Exception as e:
                print('Error: {}'.format(e), file=sys.stderr)
                continue
            print('{} downloaded and saved to {}'.format(docset['name'], target_path))
        else:
            print('{} not in docset list. Skip.'.format(docset_name))

def do_list(args):
    print('Official Docsets:')
    for docset in zealdocsets:
        print_docset(docset)
    if userdocsets is not None:
        print('User Contribution Docsets:')
        for docset in userdocsets:
            print_docset(docset)

def parse_args():
    parser = argparse.ArgumentParser()
    """
    四个sub-command:
        install 安装docset
        search 查找docset
        download 下载docset
        list 列出所有的docset
    """
    parser.add_argument('--no-cache', help='cache the docset list for later use', action='store_true', default=False)
    parser.add_argument('--user', help='also use the docset in the user contribution list', action='store_true', default=False)
    subparsers = parser.add_subparsers(title='sub-commands', description='sub commands', dest='subcommand', required=True)

    install_parser = subparsers.add_parser('install', help='install docsets')
    install_parser.add_argument('doc_names', help='name of docset to install', nargs='+')
    install_parser.add_argument('--dest', help='docset dir of Zeal', default='~/.local/share/Zeal/Zeal/docsets')

    search_parser = subparsers.add_parser('search', help='look for docsets')
    search_parser.add_argument('doc_pattern', help='regex pattern of docset(ignore case)')

    download_parser = subparsers.add_parser('download', help='download docsets from Internet')
    download_parser.add_argument('doc_names', help='name of docset to download', nargs='+')
    download_parser.add_argument('--dest', help='dest dir to store the downloaded docset', default='.')

    list_parser = subparsers.add_parser('list', help='show all docsets')
    return parser.parse_args()



def main():
    args = parse_args()
    cache = not args.no_cache
    global zealdocsets
    global userdocsets
    zealdocsets = get_docset_list(cache)
    if args.user:
        userdocsets = get_user_docset_list(cache)
    handler = {
        'install':do_install,
        'search':do_search,
        'download':do_download,
        'list':do_list,
    }
    handler[args.subcommand](args)

if __name__ == '__main__':
    main()



