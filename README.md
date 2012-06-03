
# Íon - Shocking simple static (site) generator

## Quickstart

### Installing Íon
Íon comes with a **_ion** folder and a Python **ion.py** script. First you have to put these files in a new directory in your web root. If you want to create more than one site, move **ion.py** out of the directory created and put it in PATH. Anyway, **ion.py** must be run in the root folder of your site (i.e. the same where the folder **_ion** is).

You need Python 3 to run Ion.

### Configure
Open the *config.ini* in **_ion** folder and define your settings.
* **base_url** - Will be used in the templates for absolute linking.
* **default_theme** - If a custom theme is not provided for a page, this theme will be used
* **blocked_dirs** - The directories you don't want Ion to read.

### Create your first page
Just run the *spark* command in the site root folder to create a new page:

    python3 **ion.py** spark
    
If you're not in the site root, you have to pass a path as second parameter:

    python3 ion.py spark path/to/folder

This will create a *data.ion* model file. You're ready to start adding your own content:

    title: My first post
    date: 2012/05/20
    content:
    My page content

Now run the charge command to generate the HTML:
    
    python3 **ion.py** charge

This will create a HTML and a JSON file in the folder you specified. Done!

### Theming and page variables.
You can add new themes to **_ion/themes**, create and use optional variables without having to edit all your previous *.ion* files. If you want a page to use a specific theme, just add the definition in data.ion:

    title: My first post
    **theme: mytheme**
    date: 2012/05/20
    content:
    My page content

Defining new variables is as simple as that. Just add any new definition to your *data.ion* and make the theme render it:

    author: Bob

In theme file:

    {{author}}

New themes must obey the same file structure of the default theme.

### Javascript/CSS automatic detection
Just put the files in the page folder and Íon will create the tags in your theme.

### And another thing...
* All page content stay in its own folder - so each page is independent.
* Uses the file system hierarchy to simulate pages and sub-pages.
* Easy to track changes and maintain websites with version controls systems like git.

## Roadmap
* Generate RSS feeds
* Page listings

## Help

* ion.py **spark** *[path/to/folder]* - Creates an empty page on path specified.
* ion.py **charge** *[path/to/folder]* - Generates HTML/JSON files of each folder under the path specified and its subfolders, recursively.
