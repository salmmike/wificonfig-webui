from setuptools import setup, find_packages

setup(
    name="wificonfigui",
    version="0.0.1",
    packages=find_packages(include=["wificonfigui"]),
    package_data={"templates": ["templates/login.html"]},
    include_package_data=True,
    zip_safe=False,
    install_requires=["Flask", "requests", "wifi==0.3.8"],
    entry_points={"console_scripts": ["wificonfigui=wificonfigui.webui:main"]},
)
