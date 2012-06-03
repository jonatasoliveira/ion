# Íon - A very simple static site generator

## Íon features

* Data definition
 * Uses a data model files (*.ion) to store and define data
 * Outputs pure HTML, so it is very fast
 * Generates a JSON file for each page
* Smart templating
 * Supports multiple templates
 * Uses template variables to show data.
 * You can create additional template variables in your data files and make your templates use them.
 * Javascript/CSS automatic detection - just put the files in the page folder and Íon will create the tags for you
* Organization
 * All page content stay in its own folder - so each page is independent
 * Allows page hierarchy


## Instalation

You just have to put the folder **_ion** in your site root directory. Edit the configuration file **config.ini** inside this folder and call **ion.py** in the same folder you put the **_ion** directory.


## Usage

* ion.py **spark** *[path/to/folder]* - Creates a empty page os path specified.
* ion.py **charge** *[path/to/folder]* - Generates HTML/JSON files of each folder under the path specified and its subfolders, recursively.

*You need Python 3 to use Ion*
