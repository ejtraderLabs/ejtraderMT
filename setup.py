from setuptools import setup
from setuptools_rust import RustExtension

setup(
    name="ejtradermtlib",
    version="0.1",
    rust_extensions=[RustExtension("ejtradermtlib", "Cargo.toml", binding=pyo3)],
    packages=["ejtradermtlib"],
    setup_requires=["setuptools-rust>=1.4.0"],
    zip_safe=False,
)
