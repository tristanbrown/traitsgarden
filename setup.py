from setuptools import setup, find_packages

import __about__

REQUIREMENTS = [
    'python-dotenv',
    'pandas>=1.1.0',
    'psycopg2',
    'sqlalchemy>=1.4.0',
    'alembic',
    'arrow',
    'flask>=2.1.2',
    'werkzeug>=2.1.2',
    'dash>=2.5.0',
    'dash-bootstrap-components',
]

setup(
    name=__about__.__name__,
    version=__about__.__version__,
    author=__about__.__author__,
    author_email=__about__.__email__,
    description=__about__.__desc__,
    license=__about__.__license__,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=REQUIREMENTS,
    python_requires='>=3.6, !=3.7.2',
    entry_points={
        'console_scripts': [
            'traitsgarden_app = traitsgarden.__main__:run',
        ]
    },
)
