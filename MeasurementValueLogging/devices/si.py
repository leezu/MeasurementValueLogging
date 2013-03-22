# -*- coding: utf-8 -*-

# Python Measurement Value Logging Software.
# SI Module
# 
# Copyright (C) 2013  Leonard Lausen <leonard@lausen.nl>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math

def splitNumber(x):
    """Split x into a float and an exponent.

    >>> splitNumber(2.5e7)
    (2.5, 7)

    """

    try:
        return round(x * pow(10, -1 * math.floor(math.log(abs(x),10))), 15), math.floor(math.log(abs(x), 10))
    except ValueError: # If x == 0
        return 0.0, 0.0

def getNumberPrefix(x):
    """Return a tuple containing x splitted to a number and SI-Prefix.

    >>> getNumberPrefix(2.5e6)
    (2.5, "M")

    """

    split = list(splitNumber(x))

    factor = split[1] % 3
    split[1] = getPrefix(pow(10, split[1] - factor))

    split[0] = split[0] * pow(10, factor)

    return tuple(split)

def getFactor(x):
    """Get factor of SI-Prefix or SI-Name

    :param x: SI-Prefix or SI-Name
    :type x: String
    :returns: SI-Factor
    :rtype: Float

    """

    if len(x) == 1:
        return _siPrefixValue[x]
    else:
        return _siPrefixValue[_siNamePrefix[x.lower()]]

def getPrefix(x):
    """Get prefix of SI-Factor or SI-Name

    :param x: SI-Factor or SI-Name
    :type x: Float or String
    :returns: SI-Prefix
    :rtype: String

    """
    
    if isinstance(x, float):
        return _siValuePrefix[x]
    else:
        return _siNamePrefix[x.lower()]


def getName(x):
    """Get name of SI-Prefix or SI-Factor

    :param x: SI-Prefix or SI-Factor
    :type x: String or Float
    :returns: SI-Name
    :rtype: String

    """
    
    if isinstance(x, float):
        return _siPrefixName[_siValuePrefix[x]]
    else:
        return _siPrefixName[x]


def getSiNames(type="normal"):
    """Return list of SI-Names

    :returns: List of SI-Names
    :rtype: List of Strings

    """
    if type=="normal":
        return normalNamesList[:]

    elif type=="all":
        return allNamesList[:]

normalNamesList = ['nano',
                'micro',
                'mili',
                '',
                'kilo',
                'mega']

allNamesList = ['yocto',
                'zepto',
                'atto',
                'femto',
                'pico',
                'nano',
                'micro',
                'mili',
                '',
                'kilo',
                'mega',
                'giga',
                'tera',
                'peta',
                'exa',
                'zetta',
                'yotta']

_siPrefixValue = { 'y': 1e-24,  # yocto
                'z': 1e-21,  # zepto
                'a': 1e-18,  # atto
                'f': 1e-15,  # femto
                'p': 1e-12,  # pico
                'n': 1e-9,   # nano
                u'µ': 1e-6,   # micro
                'm': 1e-3,   # mili
                '' : 1e0,    #
                'k': 1e3,    # kilo
                'M': 1e6,    # mega
                'G': 1e9,    # giga
                'T': 1e12,   # tera
                'P': 1e15,   # peta
                'E': 1e18,   # exa
                'Z': 1e21,   # zetta
                'Y': 1e24 }  # yotta

_siPrefixName = { 'y': 'yocto',
                'z': 'zepto',
                'a': 'atto',
                'f': 'femto',
                'p': 'pico',
                'n': 'nano',
                u'µ': 'micro',
                'm': 'mili',
                '' : '',
                'k': 'kilo',
                'M': 'mega',
                'G': 'giga',
                'T': 'tera',
                'P': 'peta',
                'E': 'exa',
                'Z': 'zetta',
                'Y': 'yotta' }

_siNamePrefix = {'yocto': 'y',
                'zepto': 'z',
                'atto': 'a',
                'femto': 'f',
                'pico': 'p',
                'nano': 'n',
                'micro': u'µ',
                'mili': 'm',
                '': '',
                'kilo': 'k',
                'mega': 'M',
                'giga': 'G',
                'tera': 'T',
                'peta': 'P',
                'exa': 'E',
                'zetta': 'Z',
                'yotta': 'Y' }

_siValuePrefix = { 1e-24: 'y',
                1e-21: 'z',
                1e-18: 'a',
                1e-15: 'f',
                1e-12: 'p',
                1e-9: 'n',
                1e-6: u'µ',
                1e-3: 'm',
                1e0: '',
                1e3: 'k',
                1e6: 'M',
                1e9: 'G',
                1e12: 'T',
                1e15: 'P',
                1e18: 'E',
                1e21: 'Z',
                1e24: 'Y' }