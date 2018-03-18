"""
Author: Tony Cox

Dream Team is a pulp-based integer programming formulation for the generalised dream team problem.
It is based on the premise that for a given 'expected score' per player and price per player, acting within the
selection rules of the game, an optimal team exists and can be selected
"""

import setuptools


DESCRIPTION = """
Dream Team is a pulp-based integer programming formulation for the generalised dream team problem.
It is based on the premise that for a given 'expected score' per player and price per player, acting within the
selection rules of the game, an optimal team exists and can be selected
"""


setuptools.setup(
    name='dreamteam',
    version='0.0.1',
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    author='Tony Cox',
    author_email='',
    url='',
    license='MIT',
    keywords='dreamteam dream team fantasy football sport',
    packages=setuptools.find_packages(exclude=('tests', 'docs')),
    install_requires=['pulp'],
)
