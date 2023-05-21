from setuptools import setup
from setuptools_rust import RustExtension

setup(
    name="ejtradermtlib",
    version="0.1",
    rust_extensions=[RustExtension("ejtradermtlib", "Cargo.toml", binding=pyo3)],
    packages=["ejtradermtlib"],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries",
    ],
    setup_requires=["setuptools-rust>=1.4.0"],
    zip_safe=False,
)
