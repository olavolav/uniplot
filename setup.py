from setuptools import setup  # type: ignore

from version import version

long_description = """Lightweight plotting to the terminal. 4x resolution via Unicode.

![uniplot screenshot](https://github.com/olavolav/uniplot/raw/master/resource/uniplot-screenshot.png)

When working with production data science code it can be handy to have plotting
tool that does not rely on graphics dependencies or works only in a Jupyter notebook.

The **use case** that this was built for is to have plots as part of your data science /
machine learning CI pipeline - that way whenever something goes wrong, you get not only
the error and backtrace but also plots that show what the problem was."""


setup(
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
    package_data={"uniplot": ["py.typed"]},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
    install_requires=["numpy>=1.15.0"],
    extras_require={
        "dev": [
            "black",
            "mypy",
            "pytest>=6.0.1",
        ]
    },
)
