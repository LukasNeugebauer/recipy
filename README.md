# recipy
Cut the crap and get recipes from annoying blogs.

Annoyed of verbose blogs that need two pages to tell you how this dinner is a weeknight staple after yoga and how their children love it?

Fear no more! For I got you covered. This script extracts the relevant information, puts it into a HTML-file and opens it in your browser.
It certainly doesn't work on all blogs, but most I have tried were fine.

Requirements are BeautifulSoup and requests.
Either make it executable, rename recipy.py to recipy and put it somewhere on your PATH, or import the main function in a Python script.

CLI: recipy url [--folder --file]
Python: from recipy import main; main(url [,folder, file])

If you're on Windows or Mac you'll probably have to give a folder argument, since '/tmp' doesn't exist. At least on Windows. 
Or you could just stop using Windows.
