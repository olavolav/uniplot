import setuptools  # type: ignore

from version import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="uniplot",
    version=version,
    author="Olav Stetter",
    author_email="olav.stetter@googlemail.com",
    description="Lightweight plotting to the terminal. 4x resolution via Unicode.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/olavolav/uniplot",
    license="MIT",
    platforms=["any"],
    packages=["uniplot"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
    install_requires=["numpy>=1.15.0"],
)
