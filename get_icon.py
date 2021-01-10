#!/usr/bin/env python3
import base64
import sys
from zealdown import get_docset_list, get_valid_docset_names

def save_icon_from_base64(b64_str, filename):
    icon = base64.b64decode(b64_str.encode('utf8'))
    with open(filename, 'wb') as f:
        f.write(icon)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: {} docset_name [icon name]'.format(sys.argv[0]))
        sys.exit(-1)
    docset = sys.argv[1]
    if len(sys.argv) > 2:
        output_name = sys.argv[2]
    else:
        output_name = docset + '.png'

    docsets = get_docset_list()
    docset_names = get_valid_docset_names(docsets)

    if docset not in docset_names:
        print('Error: no icon for {}'.format(docset))
        print('Supported icon: {}'.format(docset_names))
        sys.exit(-1)

    for doc in docsets:
        if docset == doc['name']:
            if 'icon2x' in doc:
                save_icon_from_base64(doc['icon2x'], output_name)
            elif 'icon' in doc:
                save_icon_from_base64(doc['icon'], output_name)
            else:
                print('no icon for {}'.format(docset))
                sys.exit(-1)


