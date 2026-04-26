from setuptools import setup, find_packages


with open("requirements.txt", "r", encoding="utf-8") as requirements_file:
    install_requires = [
        line.strip()
        for line in requirements_file
        if line.strip() and not line.lstrip().startswith("#")
    ]


setup(
    name="shwap",
    version="0.0.1",
    description="Inventory-first sharing app for Frappe",
    author="shwap.trade",
    author_email="hello@shwap.trade",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
)
