from pathlib import Path
import shutil

import click
from jinja2 import FileSystemLoader, Environment
import toml


def _load_config(file_path):
    """Load the config from a toml file"""
    with open(file_path, "r") as config:
        configuration = toml.load(config)
    return configuration


@click.command()
@click.argument('config_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument('templates', type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path))
@click.argument('static', type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path))
@click.argument('output_path', type=click.Path(dir_okay=True, file_okay=False, path_type=Path))
def create_web(config_file, templates, static, output_path):
    """Build html slide deck with the course specific configuration

    \b
    CONFIG_FILE Toml file with the course configuration parameters.
    TEMPLATES Folder Path to the Jinja2 compatible templates folder.
    STATIC Folder Path to static entities, copied to the output folder.
    OUTPUT_PATH Folder Path to write the output.

    \f
    Notes
    -----
    Course configuration should contain following elements:

        * 'title', e.g.
        * 'dates', e.g. June 8, 9 and 10, 2022
        * 'repository', e.g. ICES-python-data
        * 'hackmd', e.g. https://hackmd.io/zuHWx-doS9ORQGV_1JcXDw?both
        * 'googleform', e.g. https://forms.gle/UfDRr3hkFtt2JcwGA

    """
    # check existence of required configuration settings for the web elements
    config = _load_config(config_file)
    required_config = ["title", "dates", "organisation", "repository",
                       "hackmd", "googleform", "conda_environment"]
    assert set(required_config).issubset(config.keys())

    # prepare output folder
    if not output_path.exists():
        output_path.mkdir(parents=True)

    env = Environment(
        loader = FileSystemLoader(str(templates.absolute())),
        trim_blocks = True
    )

    # render the template pages
    for tmpl in env.list_templates(extensions="tmpl"):
        template = env.get_template(tmpl)
        rendered = template.render(config)
        with open(output_path / ".".join(tmpl.split(".")[:-1]), "w") as page:
            page.write(str(rendered))

    # copy the static files
    shutil.copytree(static, output_path / static.stem, dirs_exist_ok=True)

if __name__ == "__main__":
    create_web()