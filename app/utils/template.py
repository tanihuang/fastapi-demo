from jinja2 import Environment, FileSystemLoader
from pathlib import Path

template_dir = Path(__file__).resolve().parent.parent / "templates"
env = Environment(loader=FileSystemLoader(template_dir))

def render_template(template_name: str, context: dict) -> str:
  template = env.get_template(template_name)
  return template.render(context)