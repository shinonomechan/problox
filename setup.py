import setuptools

with open("requirements.txt") as fp:
    requirements = fp.read().splitlines()

setuptools.setup(
    name="problox",
    author="h0nda",
    description="Simple roblox library",
    url="https://github.com/h0nde/problox",
    packages=setuptools.find_packages(),
    classifiers=[],
    install_requires=requirements,
    include_package_data=True,
    version="1.0.0"
)