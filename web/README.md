## Course slideshow generation

Usage of a template to generate the course website and slideshow. Uses jinja2 and a toml-configuration file to generate the slideshow of a specific course.

1. Adjust/create a config file `config.toml`
1. Run the build command, with the configurations a ref to the template folder, the static folder and a chosen output file, e.g.

   ```
   python build.py ./config_example.toml ./templates ./static ../docs
   ```