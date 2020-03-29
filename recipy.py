#!/usr/bin/python3

import json
from bs4 import BeautifulSoup
import requests
import os
import webbrowser
import argparse
    
def main(url, *args, **kwargs):
    parser = _get_html_parser(url)
    tag = _get_recipe_tag(parser)
    recipe = _get_recipe_dict(tag)
    html = _write_html(
        _parse_recipe(recipe),
        *args, **kwargs
    )
    _open_html(html)

def _get_html_parser(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def _write_html(recipe, file = '', folder = None):
    if file:
        file = '_'.join(recipe['title'].split( ))
    if not file.endswith('.html'):
        file += '.html'
    if folder is None:
        folder = '/tmp'
    filename = os.path.join(folder,file)
    scaffolding = """<html>
    <head>
    <title>{}</title>
    </head>
    <body>
    <h1>{}</h1>
    {}
    </body>
    </html> 
    """.format(recipe['title'], recipe['title'],'{}')
    ingredients = (
        "<h2>Ingredients</h2>" + 
        "\n".join(["<p>{}</p>".format(x) for x in recipe['ingredients']])
    ) if 'ingredients' in recipe.keys() else ""
    instructions =(
        "<h2>Instructions</h2>" + 
    "\n".join(["<h4>{}</h4>\n<p>{}</p>".format(1+i,x) for i,x in enumerate(recipe['instructions'])])
    ) if 'instructions' in recipe.keys() else ""
    image = "<img src=\"{}\">".format(recipe['images'][0]) if 'images' in recipe.keys() else ""
    with open(filename, 'w') as f:
        f.write(
            scaffolding.format(
                ingredients +
                instructions +
                image
            )
        )
    print('HTML file created at {:s}'.format(filename))
    return filename

def _open_html(html):
    webbrowser.open(html)
    
def _get_recipe_tag(parser):
    scripts = parser.find_all('script')
    for sc in scripts:
        if 'yoast-schema-graph' in sc.get_attribute_list('class'):
            return sc
    raise RuntimeError('Couldn\'t find recipe tag in html.')
    
def _get_recipe_dict(tag):
    _json = json.loads(tag.string)['@graph']
    _recipe = list(filter(lambda x: x['@type'] == 'Recipe', _json))[0]
    if not _recipe:
        raise RuntimeError('Couldn\'t find recipe dictionary in json.')
    return _recipe

def _parse_recipe(_recipe):
    recipe = {
        new: _recipe[old] for old, new in zip(
            ['name', 'image', 'recipeIngredient', 'recipeInstructions'],
            ['title', 'images', 'ingredients', 'instructions']
        ) if old in _recipe.keys()
    }
    recipe['instructions'] = [x['text'] for x in recipe['instructions']]
    return recipe

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    #url
    parser.add_argument(
        dest = 'url',
        action = 'store',
        type = str
    )
    parser.add_argument(
        '--folder',
        dest = 'folder',
        action = 'store',
        default = '/tmp'
    )
    parser.add_argument(
        '--file',
        dest = 'file',
        action = 'store',
        default = None
    )
    
    args = parser.parse_args()
    main(args.url, args.folder, args.file)
