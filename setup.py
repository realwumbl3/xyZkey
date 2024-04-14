from setuptools import setup, find_packages

packages = find_packages()

print("packages: ", packages)

setup(
    name="zyXKey",
    version="1.0",
    packages=packages,
    install_requires=[
        # List your package's dependencies here
    ],
)
