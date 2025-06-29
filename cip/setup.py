from setuptools import setup, find_packages


if __name__ == "__main__":
    setup(
        name='cip',
        version='0.0.1',
        package_dir={"": "src"},
        packages=find_packages(where="src"),
    )