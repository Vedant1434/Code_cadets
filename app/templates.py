from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
import os


# Get the templates directory (app/templates)
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# Create Jinja2 environment with file system loader
env = Environment(loader=FileSystemLoader(template_dir))

def render_template(name: str, context: dict):
    if not name.endswith('.html'):
        name += '.html'
    template = env.get_template(name)
    return HTMLResponse(template.render(**context))