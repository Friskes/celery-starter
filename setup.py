from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()


with open("requirements/base.txt") as fh:
    requirements = [r for r in fh.read().split("\n") if not r.startswith("#")]


setup(
    name="celery_starter",
    version="1.0.0",
    description="Django command to launch celery worker, beat, flower",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Friskes",
    author_email="friskesx@gmail.com",
    url="https://github.com/Friskes/celery-starter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP",
    ],
    license="MIT",
    keywords="Django Celery Beat Flower Autoreload",
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=requirements,
)