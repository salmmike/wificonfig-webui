from setuptools import setup, find_packages

setup(
    name="wificonfigui",
    version="0.0.2",
    packages=find_packages(include=["wificonfigui"]),
    package_data={"templates": ["templates/login.html", "templates/login.html"]},
    include_package_data=True,
    zip_safe=False,
    install_requires=["Flask", "requests"],
    entry_points={"console_scripts": ["wificonfigui=wificonfigui.webui:main"]},
)
