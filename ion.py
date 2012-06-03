# coding: utf-8

'''
Ion - A very simple static site generator
Author: Karlisson M. Bezerra
E-mail: contact@hacktoon.com
URL: https://github.com/karlisson/ion
License: WTFPL - http://sam.zoy.org/wtfpl/COPYING
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


def load_config():
    '''Loads a file from a ini file in system folder'''
    from configparser import ConfigParser

    parser = ConfigParser()
    # getcwd allows calling ion.py from wherever it is
    current_dir = os.path.join(os.getcwd(), CFG['system_dir'])
    config_file = os.path.join(current_dir, 'config.ini')
    try:
        parser.read(config_file)
        ion_config = parser['ion']  # .ini section
    except:
        sys.exit('Zap! Could not load configuration file!')

    CFG['base_url'] = ion_config.get('base_url', '/')
    CFG['themes_dir'] = os.path.join(CFG['system_dir'], 'themes')

    theme = ion_config.get('default_theme', 'ion')
    theme_file = theme + '.html'
    # a example theme path: '_ion/themes/ionize/ionize.html'
    CFG['default_theme'] = os.path.join(CFG['themes_dir'], theme, theme_file)

    # folders you don't want Ion to access
    if 'blocked_dirs' in ion_config:
        for folder in ion_config['blocked_dirs'].split(','):
            CFG['blocked_dirs'].append(folder.strip())
    # adds the system dir by default so Ion doesn't
    # read the data model file 'data.ion'
    CFG['blocked_dirs'].append(CFG['system_dir'])


def get_styles(files, url):
    styles = []
    for filename in files:
        if not filename.endswith('.css'):
            continue
        css = os.path.join(url, filename)
        link_tag = '<link rel="stylesheet" type="text/css" href="{0}" />\n'
        styles.append(link_tag.format(css))
    return ''.join(styles)


def get_scripts(files, url):
    scripts = []
    for filename in files:
        if not filename.endswith('.js'):
            continue
        js = os.path.join(url, filename)
        script_tag = '<script src="{0}"></scripts>\n'
        scripts.append(script_tag.format(js))
    return ''.join(scripts)


def build_html(page_data):
    '''Returns the template content populated with page data'''
    # if not using custom theme, use default
    if 'theme' in page_data.keys():
        themes_dir = CFG['themes_dir']
        name = page_data['theme']
        theme_filepath = '{0}/{1}/{1}.html'.format(themes_dir, name)
    else:
        theme_filepath = CFG['default_theme']

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
            key, value = list(map(lambda x: x.strip(), line.split(':')))
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
        # tests for directories that ion shall not read
        if is_blocked(dirname):
            continue
        source_filepath = os.path.join(dirname, CFG['source_file'])

        # directory doesn't have a metafile, skip
        if not os.path.exists(source_filepath):
            continue

        # extracts data from this page
        page_data = get_page_data(source_filepath)

        # set common page data
        base_url = CFG['base_url']
        page_data['base_url'] = base_url
        page_data['themes_url'] = os.path.join(base_url, CFG['themes_dir'])
        page_data['permalink'] = base_url + dirname.replace('./', '')
        page_data['styles'] = get_styles(filenames, page_data['permalink'])
        page_data['scripts'] = get_scripts(filenames, page_data['permalink'])

        # saves a json file
        save_json(dirname, page_data)

        # fills template with page data and saves a html file
        save_html(dirname, build_html(page_data))


def ion_spark(path):
    '''Creates a new page in specified path'''
    import shutil
    if not os.path.exists(path):
        os.makedirs(path)

    # copy data model file to new page
    dst = os.path.join(path, CFG['source_file'])
    if not os.path.exists(dst):
        # copy source file to new path
        src = os.path.join(CFG['system_dir'], CFG['source_file'])
        shutil.copy(src, dst)
        print('Page \'{0}\' successfully created.'.format(path))
        print('Edit the file {0} and call \'ion charge\'!'.format(dst))
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
    if not os.path.exists(CFG['system_dir']):
        sys.exit('Zap! System folder couldn\'t be accessed. It must \
be in the same directory that Ion is called.')

    # first parameter - command
    try:
        command = sys.argv[1]
    except IndexError:
        print(help_message)
        sys.exit()

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
