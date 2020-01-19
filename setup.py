import setuptools

setuptools.setup(
    name="pandas_inspect",
    version="0.0.3",
    author="Yunus Emre Inci",
    author_email="yemreinci@pragmacraft.com",
    description="Dynamically inspect pandas code",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['pandas_inspect=pandas_inspect.commandline:main']
    }
)