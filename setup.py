#!/usr/bin/env python
#
#    This software is derived from Django-things originally written and
#    copyrighted by John-Michael Oswalt <https://github.com/jmoswalt/django-things>
#
#    This is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This software is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with Django-things.  If not, see <http://gnu.org/licenses/>.
from setuptools import setup, find_packages

setup(
    name='django-things',
    version=__import__('things').__version__,
    license='GNU Lesser General Public License (LGPL), Version 3',
    url='https://github.com/jmoswalt/django-things',
    include_package_data=True,
    packages=find_packages(),
    description='Two Table model for Django for storing other model data.',
    long_description=open('README.md').read(),
    requires=['python (>= 2.6)'],
    install_requires=[
        'Django==1.5',
        'python-dateutil==2.1'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
