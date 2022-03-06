#!/usr/bin/env python3
"""
recipy
Script to extract the actual recipe from annoying blogs
"""


import json
from bs4 import BeautifulSoup
import requests
import webbrowser
import sys
import re
import tempfile
import platform

if platform.system() == "Windows":
    import ntpath as path
else:
    from os import path


def main(url, filename):
    parser = _get_html_parser(url)
    recipe = _get_recipe_dict(parser)
    html = _get_html(recipe)
    if filename is not None:
        filename = _save_html(filename, html)
    else:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
            f.write(html)
            filename = f.name
    webbrowser.open(filename)


def _get_html_parser(url):
    html = requests.get(url)
    if html.status_code == 403:
        raise RuntimeError(
            "Requests returned error code 403: Forbidden. "
            + "Have a look at the website and this stackoverflow question:\n\n"
            + "https://stackoverflow.com/questions/38489386/"
            + "python-requests-403-forbidden"
        )
    soup = BeautifulSoup(html.text, "html.parser")
    return soup


def _get_html(recipe):
    scaffolding = """
        <html>
        <head>
        <title>{}</title>
        </head>
        <body>
        <h1>{}</h1>
        {}
        </body>
        </html>
    """.format(
        recipe["title"], recipe["title"], "{}"
    )
    ingredients = (
        (
            "<h2>Ingredients</h2>"
            + "\n".join(["<p>{}</p>".format(x) for x in recipe["ingredients"]])
        )
        if "ingredients" in recipe.keys()
        else ""
    )
    instructions = (
        (
            "<h2>Instructions</h2>"
            + "\n".join(
                [
                    "<h4>{}</h4>\n<p>{}</p>".format(1 + i, x)
                    for i, x in enumerate(recipe["instructions"])
                ]
            )
        )
        if "instructions" in recipe.keys()
        else ""
    )
    _image = ""
    if "images" in recipe.keys():
        if isinstance(recipe["images"], dict):
            _image = recipe["images"]["url"]
        elif isinstance(recipe["images"], list):
            _image = recipe["images"][0]
        elif isinstance(recipe["images"], str):
            _image = recipe["images"]
    image = '<img src="{}" style="height:40%">'.format(_image) if _image else ""
    return scaffolding.format(image + ingredients + instructions)


def _save_html(filename, html):
    if not filename.endswith(".html"):
        filename += ".html"
    with open(filename, "w") as f:
        f.write(html)
    print("HTML file created at {:s}".format(filename))
    return filename


def _get_recipe_dict(parser):
    scripts = parser.find_all("script")
    scripts = list(filter(lambda x: x is not None, scripts))
    for sc in scripts:
        if sc.string is not None and re.findall(r'"@type":\w?"Recipe"', sc.string):
            return _get_recipe_dict_json(sc)
    # if this didn't work maybe the recipe isn't in json but html
    scripts = parser.find_all("article")
    if len(scripts) == 1:
        return _get_recipe_dict_html(scripts[0])
    raise RuntimeError("Couldn't find recipe tag in html.")


def _get_recipe_dict_json(tag):
    _json = json.loads(tag.string)
    if isinstance(_json, dict) and "@type" in _json.keys():
        _recipe = _json
    else:
        if isinstance(_json, dict) and "@graph" in _json.keys():
            _json = _json["@graph"]
        _recipe = list(filter(lambda x: x["@type"] == "Recipe", _json))[0]
    if not _recipe:
        raise RuntimeError("Couldn't find recipe dictionary in json.")
    recipe = {
        new: _recipe[old]
        for old, new in zip(
            ["name", "image", "recipeIngredient", "recipeInstructions"],
            ["title", "images", "ingredients", "instructions"],
        )
        if old in _recipe.keys()
    }
    recipe["instructions"] = [x["text"] for x in recipe["instructions"] if "text" in x]
    return recipe


def _get_recipe_dict_html(tag):
    _tag = tag.select("div.recipe")[0]
    title = _tag.select("h2")[0].contents[0]
    if str(title).startswith("<") and str(title).endswith(">"):
        title = title.string
    _instructions = _tag.select("div.instructions")[0].select("li")
    instructions = [ins.contents[0] for ins in _instructions]
    _ingredients = _tag.select("div.ingredients")[0].select("li")
    ingredients = [ing.contents[0] for ing in _ingredients]
    image = _tag.select("img")[0].get("src")
    return {
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions,
        "images": image,
    }


if __name__ == "__main__":

    argc = len(sys.argv)
    if argc == 1:
        raise RuntimeError(
            "Can't run without URL. Use me like this:\nrecipy url [,filename]"
        )
    elif argc == 2:
        url = sys.argv[1]
        filename = None
    elif argc == 3:
        url = sys.argv[1]
        filename = sys.argv[2]
    main(url, filename)
