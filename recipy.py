#!/usr/bin/python3

import json
from bs4 import BeautifulSoup
import requests
import os
import webbrowser
import argparse
import re


def main(url, *args, **kwargs):
    parser = _get_html_parser(url)
    recipe = _get_recipe_dict(parser)
    html = _write_html(
        recipe,
        *args, **kwargs
    )
    _open_html(html)


def _get_html_parser(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def _write_html(recipe, file='', folder=None):
    if file:
        file = '_'.join(recipe['title'].split())
    if not file.endswith('.html'):
        file += '.html'
    if folder is None:
        folder = '/tmp'
    filename = os.path.join(folder, file)
    scaffolding = """<html>
    <head>
    <title>{}</title>
    </head>
    <body>
    <h1>{}</h1>
    {}
    </body>
    </html> 
    """.format(recipe['title'], recipe['title'], '{}')
    ingredients = (
        "<h2>Ingredients</h2>" + 
        "\n".join(["<p>{}</p>".format(x) for x in recipe['ingredients']])
    ) if 'ingredients' in recipe.keys() else ""
    instructions = (
        "<h2>Instructions</h2>" + 
    "\n".join(["<h4>{}</h4>\n<p>{}</p>".format(1+i,x) for i,x in enumerate(recipe['instructions'])])
    ) if 'instructions' in recipe.keys() else ""
    _image = ""
    if 'images' in recipe.keys():
        if isinstance(recipe['images'], dict):
            _image = recipe['images']['url']
        elif isinstance(recipe['images'], list):
            _image = recipe['images'][0]
        elif isinstance(recipe['images'], str):
            _image = recipe['images']
    image = "<img src=\"{}\">".format(_image) if _image else ""
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


def _get_recipe_dict(parser):
    scripts = parser.find_all('script')
    scripts = list(filter(lambda x: x is not None, scripts))
    for sc in scripts:
        if sc.string is not None and \
           re.findall('"@type":\w?"Recipe"', sc.string):
            return _get_recipe_dict_json(sc)
    # if this didn't work maybe the recipe isn't in json but html
    scripts = parser.find_all('article')
    if len(scripts) == 1:
        return _get_recipe_dict_html(scripts[0])
    raise RuntimeError('Couldn\'t find recipe tag in html.')


def _get_recipe_dict_json(tag):
    _json = json.loads(tag.string)
    if isinstance(_json, dict) and _json['@type'] == 'Recipe':
        _recipe = _json
    else:
        if isinstance(_json, dict) and '@graph' in _json.keys():
            _json = _json['@graph']
        _recipe = list(filter(lambda x: x['@type'] == 'Recipe', _json))[0]
    if not _recipe:
        raise RuntimeError('Couldn\'t find recipe dictionary in json.')
    recipe = {
        new: _recipe[old] for old, new in zip(
            ['name', 'image', 'recipeIngredient', 'recipeInstructions'],
            ['title', 'images', 'ingredients', 'instructions']
        ) if old in _recipe.keys()
    }
    recipe['instructions'] = [x['text'] for x in recipe['instructions']]
    return recipe


def _get_recipe_dict_html(tag):
    _tag = tag.select('div.recipe')[0]
    title = _tag.select('h2')[0].contents[0]
    _instructions = _tag.select('div.instructions')[0].select('li')
    instructions = [ins.contents[0] for ins in _instructions]
    _ingredients = _tag.select('div.ingredients')[0].select('li')
    ingredients = [ing.contents[0] for ing in _ingredients]
    image = _tag.select('img')[0].get('src')
    return {
        'title': title,
        'ingredients': ingredients,
        'instructions': instructions,
        'images': image
    }


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        dest='url',
        action='store',
        type=str
    )
    parser.add_argument(
        '--folder',
        dest='folder',
        action='store',
        default='/tmp'
    )
    parser.add_argument(
        '--file',
        dest='file',
        action='store',
        default=None
    )
    args = parser.parse_args()
    main(args.url, args.folder, args.file)
