import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ozapfdis",
    version="0.0.1-ultra-experimental",
    author="Markus Harrer",
    author_email="ozapfdis@markusharrer.de",
    description="Open Zippy Analysis Project For Data In Software: A helper library that let's you import all kinds of software related data into the data analysis framework pandas.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/feststelltaste/ozapfdis",
    packages=setuptools.find_packages(),
    install_requires=[
          'pandas',
          'gitpython'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD 3-Clause License",
        "Operating System :: OS Independent",
    ]
)