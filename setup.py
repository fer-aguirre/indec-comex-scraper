from setuptools import setup, find_packages

setup(
    name='indec_comex',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'requests',
        'tabulate'
    ],
    entry_points={
        'console_scripts': [
            # La sintaxis es 'nombre-del-comando = carpeta.archivo:funcion'
            'indec-descargar = indec_comex.cli:main',
        ],
    },
)
