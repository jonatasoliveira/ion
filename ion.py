# coding: utf-8

'''
===============================================================================
Ion - A shocking simple static (site) generator

Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/karlisson/ion
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING

===============================================================================
'''

import os
import json
import re
import sys


if sys.version_info.major < 3:
    sys.exit('Zap! Ion requires Python 3!')

# pre-configuration values
CFG = {
    'system_dir': '_ion',
    'source_file': 'data.ion',
    'blocked_dirs': []
}

# this is the model of files used to store content
# it will be saved to a new file data.ion every
# time 'ion spark' is called
DATA_MODEL = '''title: Write your title here
date: yyyy-mm-dd
content:
Write your content here
'''


def parse_config_file(file_path):
    '''Parse a configuration file and returns data in a dictionary'''
    config_file = open(file_path)
    # remove trailing whitespaces and linebreaks
    lines = [line.strip() for line in config_file.readlines()]
    config = {}
    for line in lines:
        # avoid comments, empty and incorrect lines
        if line.startswith('#') or not len(line) or '=' not in line:
            continue
        key, value = line.split('=')
        config[key.strip()] = value.strip()
    config_file.close()
    return config


def load_config():
    '''Loads a config file from a ini file in system folder'''
    # getcwd allows calling ion.py from wherever it is located
    system_dir = os.path.join(os.getcwd(), CFG['system_dir'])

    if not os.path.exists(system_dir):
        sys.exit('Zap! System folder "{0}" doesn\'t exists or couldn\'t be \
read. It must be in the same directory that ion.py is \
called.'.format(CFG['system_dir']))

    try:
        config = parse_config_file(os.path.join(system_dir, 'config.ini'))
    except:
        sys.exit('Zap! Could not load configuration file!')
    # try to set a default value if it wasn't defined in config
    base_url = config.get('base_url', 'http://localhost/')
    # will add a trailing slash if not informed
    CFG['base_url'] = os.path.join(base_url, '')

    CFG['themes_dir'] = os.path.join(CFG['system_dir'], 'themes')

    # a example theme path: '_ion/themes/ionize/index.html'
    CFG['default_theme'] = config.get('default_theme', 'ionize')

    # folders you don't want Ion to access
    if 'blocked_dirs' in config:
        for folder in config.get('blocked_dirs'):
            CFG['blocked_dirs'].append(folder)
    # adds the system dir by default
    CFG['blocked_dirs'].append(CFG['system_dir'])


def build_external_tags(files, permalink):
    '''Detects if there are CSS and Javascript files in current folder
    and returns concatenated link/script tags for each one'''
    styles = []
    scripts = []
    link_tag = '<link rel="stylesheet" type="text/css" href="{0}" />\n'
    script_tag = '<script src="{0}"></scripts>\n'
    for filename in files:
        url = os.path.join(permalink, filename)
        if filename.endswith('.css'):
            styles.append(link_tag.format(url))
        elif filename.endswith('.js'):
            scripts.append(script_tag.format(url))
    return {'styles': ''.join(styles), 'scripts':''.join(scripts)}


def build_html(page_data):
    '''Returns the template content populated with page data'''
    # if not using custom theme, use default
    themes_dir = CFG['themes_dir']
    if 'theme' in page_data.keys():
            name = page_data['theme']
    else:
        name = CFG['default_theme']
    theme_filepath = '{0}/{1}/index.html'.format(themes_dir, name)

    if not os.path.exists(theme_filepath):
        sys.exit('Zap! Template file {0} couldn\'t be \
found!'.format(theme_filepath))

    #abrindo arquivo de template e extraindo o html
    theme_file = open(theme_filepath, 'r')
    html = theme_file.read()
    theme_file.close()

    # fill template with page data
    for key, value in page_data.items():
        regex = re.compile(r'\{\{\s*' + key + '\s*\}\}')
        html = re.sub(regex, value.strip(), html)
    return html


def get_page_data(source_path):
    '''Parses *.ion data files and returns the values'''
    source_file = open(source_path, 'r')
    page_data = {}

    while True:
        line = source_file.readline()
        # if reached end of file, exit loop
        if len(line) == 0:
            break
        # will avoid splitting blank lines
        try:
            key, value = list(map(str.strip, line.split(':')))
        except:
            continue
        # read the rest of the file
        if(key == 'content'):
            value = value + source_file.read()
        #setting values
        page_data[key] = value
    source_file.close()
    return page_data


def save_json(dirname, page_data):
    json_filepath = os.path.join(dirname, 'index.json')
    json_file = open(json_filepath, 'w')
    json_file.write(json.dumps(page_data))
    json_file.close()


def save_html(dirname, html):
    html_filepath = os.path.join(dirname, 'index.html')
    html_file = open(html_filepath, 'w')
    html_file.write(html)
    html_file.close()
    print('\'{0}\' generated.'.format(html_filepath.replace('./', '')))


def is_blocked(dirname):
    '''Checks if the actual directory is blocked to generation'''
    return dirname.replace('./', '') in CFG['blocked_dirs']


def ion_charge(path):
    '''Reads recursively every directory under path and
    outputs HTML/JSON for each data.ion file'''
    for dirname, subdirs, filenames in os.walk(path):
        source_filepath = os.path.join(dirname, CFG['source_file'])
        # tests for directories that ion shall not read
        # or directory doesn't have a metafile
        if is_blocked(dirname) or not os.path.exists(source_filepath):
            continue
        # extracts data from this page
        page_data = get_page_data(source_filepath)

        # set common page data
        base_url = CFG['base_url']
        page_data['base_url'] = base_url
        page_data['themes_url'] = base_url + CFG['themes_dir']
        #removing ./ in the case of root directory of site
        page_data['permalink'] = base_url + dirname.replace('./', '')
        # get css and javascript found in the folder
        external_tags = build_external_tags(filenames, page_data['permalink'])
        page_data['styles'] = external_tags['styles']
        page_data['scripts'] = external_tags['scripts']

        # saves a json file
        save_json(dirname, page_data)

        # fills template with page data and saves a html file
        save_html(dirname, build_html(page_data))


def ion_spark(path):
    '''Creates a new page in specified path'''
    if not os.path.exists(path):
        os.makedirs(path)

    filepath = os.path.join(path, CFG['source_file'])
    if not os.path.exists(filepath):
        # copy source file to new path
        data_file = open(filepath, 'w')
        data_file.write(DATA_MODEL)
        data_file.close()

        print('Page \'{0}\' successfully created.'.format(path))
        print('Edit the file {0} and call \'ion charge\'!'.format(filepath))
    else:
        print('Zap! Page \'{0}\' already exists \
with a data.ion file.'.format(path))


def main():
    load_config()

    help_message = '''Usage:
    ion.py spark [path/to/folder] - Creates a empty page os path specified.
    ion.py charge [path/to/folder] - Generates HTML/JSON files of each \
folder under the path specified and its subfolders, recursively.
    ion.py help - Shows this help message.
    '''

    # first parameter - command
    try:
        command = sys.argv[1]
    except IndexError:
        sys.exit(help_message)

    # second parameter - path
    # if not provided, defaults to current
    try:
        path = sys.argv[2]
    except IndexError:
        path = '.'

    if command == 'spark':
        ion_spark(path)
    elif command == 'charge':
        ion_charge(path)
    elif command == 'help':
        sys.exit(help_message)
    else:
        print('Zap! {0} is a very strange command!'.format(command))
        sys.exit(help_message)


if __name__ == '__main__':
    main()
