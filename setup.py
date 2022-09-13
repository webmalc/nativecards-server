"""The setup module for the booking-sites-parser"""
import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

README = (HERE / 'README.md').read_text()
DESC = 'The backend server for the Nativecards app'

setup(
    name='nativecards-server',
    version='0.0.1',
    description=DESC,
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/webmalc/nativecards-server',
    author='webmalc',
    author_email='m@webmalc.pw',
    license="GPL-3.0",
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.7.0',
    packages=find_packages(
        exclude=['tests', '*.tests', '*.tests.*', 'tests.*']),
    include_package_data=True,
    install_requires=[
        'amqp==2.3.2',
        'apipkg==1.5',
        'arrow==0.12.1',
        'atomicwrites==1.1.5',
        'attrs==18.1.0',
        'Babel==2.6.0',
        'backcall==0.1.0',
        'bcrypt==3.1.4',
        'billiard==3.5.0.4',
        'boto3==1.7.79',
        'botocore==1.10.79',
        'cairocffi==0.9.0',
        'CairoSVG==2.1.3',
        'celery==4.2.1',
        'certifi==2018.8.13',
        'cffi==1.13.2',
        'cryptography==2.3.1',
        'cssselect2==0.2.1',
        'defusedxml==0.5.0',
        'Django>=2.2.9,<3.0.0',
        'django-annoying==0.10.4',
        'django-appconf==1.0.2',
        'django-autoslug==1.9.3',
        'django-ckeditor==5.6.1',
        'django-colorful==1.2',
        'django-cors-headers==2.4.0',
        'django-crispy-forms==1.7.2',
        'django-debug-toolbar==1.9.1',
        'django-extensions==2.2.5',
        'django-filter==2.1.0',
        'django-formtools==2.1',
        'django-imagekit==4.0.2',
        'django-js-asset==1.1.0',
        'django-markdownx==2.0.24',
        'django-model-utils==3.1.2',
        'django-modeltranslation==0.12.2',
        'django-ordered-model==2.1.0',
        'django-otp==0.5.0',
        'django-phonenumber-field==1.3.0',
        'django-reversion==3.0.0',
        'django-templatetag-handlebars==1.3.1',
        'django-two-factor-auth==1.8.0',
        'djangorestframework==3.9.1',
        'django-environ==0.4.5',
        'djangorestframework-simplejwt==4.3.0',
        'PyJWT==1.7.1',
        'docutils==0.14',
        'drf-extensions==0.3.1',
        'execnet==1.5.0',
        'Fabric3==1.14.post1',
        'flower==1.2.0',
        'html5lib==1.0.1',
        'idna==2.7',
        'jmespath==0.9.3',
        'jsonpickle==0.9.6',
        'kombu==4.2.1',
        'Markdown==3.0.1',
        'mccabe==0.6.1',
        'microsofttranslator==0.8',
        'more-itertools==4.3.0',
        'num2words==0.5.7',
        'paramiko==2.4.2',
        'pdfrw==0.4',
        'pew==1.1.5',
        'phonenumberslite==8.9.10',
        'pilkit==2.0',
        'pipenv==2018.7.1',
        'pluggy==0.13.1',
        'polib==1.1.0',
        'progressbar2==3.38.0',
        'psycopg2==2.8.4',
        'ptyprocess==0.6.0',
        'py==1.5.4',
        'py-moneyed==0.7.0',
        'pyasn1==0.4.4',
        'pycparser==2.18',
        'Pyphen==0.9.4',
        'python-dateutil==2.7.3',
        'python-memcached==1.59',
        'python-utils==2.3.0',
        'qrcode==6.0',
        'raven==6.9.0',
        'redis==2.10.6',
        'requests==2.22.0',
        'rsa==3.4.2',
        's3transfer==0.1.13',
        'sqlparse==0.2.4',
        'standardjson==0.3.1',
        'tinycss2==0.6.1',
        'tornado==5.1',
        'tqdm==4.24.0',
        'unicodecsv==0.14.1',
        'Unidecode==1.0.22',
        'urllib3==1.25.7',
        'vine==1.1.4',
        'watchtower==0.5.3',
        'WeasyPrint==0.42.3',
        'webencodings==0.5.1',
        'Werkzeug==0.16.0',
        'wrapt==1.11.1',
        'xlrd==1.1.0',
        'xlwt==1.3.0',
        'typing==3.6.4',
        'PyYAML==5.1.2',
        'gTTS==2.0.4',
        'googletrans==2.4.0',
    ],
)
