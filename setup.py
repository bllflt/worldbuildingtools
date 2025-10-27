from setuptools import find_packages, setup

setup(
    name='wbcr-reconcilder',
    version='1.0.0',
    description='',
    include_package_data=True,
    packages=find_packages(where="src", include=["apifast*"]),
    package_dir={"": "src"},
)
