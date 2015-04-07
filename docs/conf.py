import sys
import os

sys.path.append(os.getcwd())

# Import the Jam pygments lexer
try:
    from .highlighting import JamLexer
except KeyError:
    from highlighting import JamLexer

extensions = [
    'sphinx.ext.todo',
]

highlight_language = "Jam"

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Jam'

# The short X.Y version.
version = '0.0'
# The full version, including alpha/beta/rc tags.
release = '0.0.1'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Keep warnings as "system message" paragraphs in the built documents.
keep_warnings = True

# The theme to use for HTML and HTML Help pages.
html_theme = 'basic'

def setup(sphinx):
    sphinx.add_lexer("Jam", JamLexer())
