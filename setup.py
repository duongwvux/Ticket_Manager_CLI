from setuptools import setup, find_packages

setup(
    name="ticket-manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["click"],
    entry_points={
        "console_scripts": [
            "tickets=adapters.primary.cli.main:cli",
        ],
    },
    package_dir={"": "."},
)