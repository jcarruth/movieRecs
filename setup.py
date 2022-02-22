from setuptools import find_packages, setup

setup(
    name="movie_recs",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "pymongo",
        "python-slugify",
        "requests",
    ],
)
