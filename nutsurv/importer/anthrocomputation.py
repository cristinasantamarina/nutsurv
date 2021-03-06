from __future__ import unicode_literals, print_function
""" This module converted from WHO Anthro AnthroComputation.cs -- original C# code is behind #C# comments

General Note: For some reason completely foreign to me [Vernon], WHO performed all of these calculations in Decimal.
  Were they worried about loosing pennies?  Did they imagine that double precision real was not good enough?
  Who can guess?  I will perform all of the calculations in float.
"""

import sys
import math
import os
import json


def roundFloat(number, decimal_places):
    if not decimal_places:
        decimal_places = 2
    elif decimal_places < 0:
        decimal_places = 0
    else:
        decimal_places = int(decimal_places)
    p = math.pow(10, decimal_places)
    return round(number * p) / p


def isFinite(value):
    try:
        float(value)
        if not math.isinf(value) and not math.isnan(value):
            return True
        else:
            return False
    except ValueError:
        return False


NaN = float('NaN')  # the floating point value "Not A Number"
undefined = None

# Boundaries for input values, checked on the UI and data import sides
# The min weight for a child, in kg.
INPUT_MINWEIGHT = 0.9

# The max weight for a child, in kg.
INPUT_MAXWEIGHT = 58.0

# The min length/height for a child, in cm.
INPUT_MINLENGTHORHEIGHT = 38.0

# The max length/height for a child, in cm.
INPUT_MAXLENGTHORHEIGHT = 150.0

# The max possible value for a record's weighting factor.
INPUT_MAXWEIGHTINGFACTOR = sys.float_info.max

# The min HC for a child, in cm.
INPUT_MINHC = 25.0

# The max HC for a child, in cm.
INPUT_MAXHC = 64.0

# The min MUAC for a child, in cm.
INPUT_MINMUAC = 6.0

# The max MUAC for a child, in cm.
INPUT_MAXMUAC = 35.0

# The min TSF for a child, in mm.
INPUT_MINTSF = 1.8

# The max TSF for a child, in mm.
INPUT_MAXTSF = 40.0

# The min SSF for a child, in mm.
INPUT_MINSSF = 1.8

# The max SSF for a child, in mm.
INPUT_MAXSSF = 40.0

# The exact number of days in one months, for converting between days and months.
# Fixed according to WHO instructions.
DAYSINMONTH = 30.4375

# Fixed factor used for computing NCHS z-scores.
NCHSFACTOR = 1.8807936

# The 'cut-off' age when determining whether length or height should be used.
HEIGHT_MINDAYS = 731

# The 'cut-off' value when determining whether length or height should be used
# (WHO standard).
LENGTH_LIMIT = 87

# The 'cut-off' value when determining whether length or height should be used
# (NCHS reference).
NCHSLENGTH_LIMIT = 85

# The min age for a child.
MINDAYS = 0

# The max age for a child to be considered in calculations.
MAXDAYS = 1856

# The min length, in cm (WHO standard).
MINLENGTH = 45

# The max length, in cm (WHO standard).
MAXLENGTH = 110

# The min height, in cm (WHO standard).
MINHEIGHT = 65

# The max height, in cm (WHO standard).
MAXHEIGHT = 120

# The min length/height for males, in cm (NCHS reference).
NCHSMINLENGTHORHEIGHT_MALE = 49

# The min length/height for females, in cm (NCHS reference).
NCHSMINLENGTHORHEIGHT_FEMALE = 49

# The max length/height for males, in cm (NCHS reference).
NCHSMAXLENGTHORHEIGHT_MALE = 145

# The max length/height for females, in cm (NCHS reference).
NCHSMAXLENGTHORHEIGHT_FEMALE = 137

# The amount in cm to add/subtract when correcting from height to length and vice-versa.
HEIGHTCORRECTION = 0.7

# Default number of decimals for measurements.
DEFAULTPRECISION_MEASURE = 2

# Default number of decimals for z-scores.
DEFAULTPRECISION_ZSCORE = 2

# Default number of decimals for percentiles.
DEFAULTPRECISION_PERCENTILE = 1

# Default number of decimals for BMI values.
DEFAULTPRECISION_BMI = 1

# Contains the default min bounds of the indicators.
MINZSCOREBOUNDS = [-5, -6, -6, -5, -5, -5, -5, -5]

# Contains the default max bounds of the indicators.
MAXZSCOREBOUNDS = [5, 5, 6, 5, 5, 5, 5, 5]

_useReferenceTablesCache = False  # [Vernon] WHO did not use cache on mobiles, we will follow that lead, for now.

# Used to not load the same json file several times within a session
INDICATOR_TABLES = {}


def get4AgeIndicatorRefData(ind, sex, ageInDays):
    if ind not in INDICATOR_TABLES:
        indicator_file = os.path.dirname(
            os.path.realpath(__file__)) + '/anthrocomputation_ref_data/AnthroRef_' + ind + '.json'
        json_data = open(indicator_file).read()
        INDICATOR_TABLES[ind] = json.loads(json_data)
    find_first = next(
        (item for item in INDICATOR_TABLES[ind] if item["Sex"] == sex and round(float(item["age"])) == round(ageInDays)), False)
    return find_first


def get4LengthOrHeightRefData(ind, sex, lengthOrHeight):
    if ind not in INDICATOR_TABLES:
        indicator_file = os.path.dirname(
            os.path.realpath(__file__)) + '/anthrocomputation_ref_data/AnthroRef_' + ind + '.json'
        json_data = open(indicator_file).read()
        INDICATOR_TABLES[ind] = json.loads(json_data)
    # In all of the files there is only either height or length, so choose based on which one is available
    if 'length' in INDICATOR_TABLES[ind][0]:
        key_name = 'length'
    else:
        key_name = 'height'
    find_first = next((item for item in INDICATOR_TABLES[ind] if item["Sex"] == sex and round(
        float(item[key_name])) == round(lengthOrHeight)), False)
    return find_first

# Used for storing data points from the indicator reference tables.


class ReferenceData(object):

    def __init__(self, x=NaN, y=NaN, el=NaN, m=NaN, s=NaN):
        # References the X-axis value: age, height or weight
        self.X = x
        self.Y = y
        self.L = el
        self.M = m
        self.S = s

#    def set_extreme(self):
#        this.X = undefined
#        this.Y = undefined
#        this.L = undefined
#        this.M = undefined
#        this.S = undefined


class IndicatorValue(object):

    def __init__(self, p=NaN, z=NaN):
        self.P = p
        self.Z = z


def centile(z_score_value):
    if (z_score_value < -3 or z_score_value > 3):
        return NaN
    abs_val = math.fabs(z_score_value)
    # try to approximate with a 5-degree polynomial function
    P1 = (
        1 - 1 / math.sqrt(2 * math.pi) * math.exp(-math.pow(abs_val, 2) / 2)
        * (
            0.31938 * (1 / (1 + 0.2316419 * abs_val))
            - 0.356563782 * math.pow(1 / (1 + 0.2316419 * abs_val), 2)
            + 1.781477937 * math.pow(1 / (1 + 0.2316419 * abs_val), 3)
            - 1.82125 * math.pow(1 / (1 + 0.2316419 * abs_val), 4)
            + 1.330274429 * math.pow(1 / (1 + 0.2316419 * abs_val), 5)
        )
    )
    P1 *= 100
    if z_score_value < 0:
        P1 = 100 - P1
    if 0 <= P1 and P1 <= 100:
        return P1
    else:
        return NaN


def getAdjustedLengthOrHeight(ageInDays, lengthOrHeight, isRecumbent):

    output = {
        'lengthOrHeight': NaN,
        'isLength': undefined
    }

    if ageInDays < 0:
        output['isLength'] = isRecumbent
        output['lengthOrHeight'] = lengthOrHeight
    else:
        if ageInDays < HEIGHT_MINDAYS:
            output['isLength'] = True

            if isRecumbent:
                output['lengthOrHeight'] = lengthOrHeight
            else:
                output['lengthOrHeight'] = lengthOrHeight + HEIGHTCORRECTION
        else:
            output['isLength'] = False
            if isRecumbent:
                output['lengthOrHeight'] = lengthOrHeight - HEIGHTCORRECTION
            else:
                output['lengthOrHeight'] = lengthOrHeight
    return output

# This function assumes access to function get4AgeIndicatorRefData(ind, sex,
# ageInDays) which provides L, M, S for a given age and sex from whatever
# database they are stored in (see databasereader.py in the old kivy app code).
# This function assumes that the data it gets from the aforementioned function
# is exactly in the same format as the data the Python implementation used to
# get (i.e. a table with the values of interest in row 0 and columns
# addressable by their name (i.e. 'L', 'M' or 'S')).


def get4AgeIndicatorReference(ind, sex, ageInDays):
    if not _useReferenceTablesCache:
        data = get4AgeIndicatorRefData(ind, sex, ageInDays)
        if data:
            return ReferenceData(ageInDays, undefined, float(data['L']), float(data['M']), float(data['S']))
        else:
            # if no data have been found from the DB, we return extreme values
            return ReferenceData()
    else:
        raise NotImplementedError()


# Crops a value to a defined precision.
# If the value is too large for truncation to the specified number of decimal
# places, the method simply truncates the value to an integer.
# Precision set to 2 by default in case invalid value or no value passed.
# Warning: this function does its job for small values of 'value' and precision
# as intended but leads to the loss of precision in case of large numbers so
# please do not use it as a general-purpose symetric crop function for
# different data sets.
def symetricCrop(value, precision):
    if not value:
        return value
    if not precision:
        precision = 2
    elif precision < 0:
        precision = 0
    else:
        precision = int(precision)

    output = int(value)
    ten_to_precision = math.pow(10, precision)
    if not isFinite(ten_to_precision):
        return output
    step = value * ten_to_precision
    if not isFinite(step) or not step:
        return output
    step = int(step) / ten_to_precision
    if not isFinite(step) or not step:
        return output
    else:
        return step


# This function assumes access to function get4LengthOrHeightRefData(ind, sex,
#   lengthOrHeight, interpolate) which provides L, M, S for a given sex,
#   'lengthOrHeight' and 'interpolate' from whatever database they are stored in.
#   This function and the function it assumes access to are analogous to
#   functions used to provide similar functionality for age-related indicators so
#   please see comment preceding function get4AgeIndicatorReference() above to
#   understand how to write get4LengthOrHeightRefData()).

def get4LengthOrHeightIndicatorReference(ind, sex, lengthOrHeight):

    if not _useReferenceTablesCache:
        data = get4LengthOrHeightRefData(ind, sex, lengthOrHeight)
        if data:
            return ReferenceData(lengthOrHeight, undefined, float(data['L']), float(data['M']), float(data['S']))
        else:
            # if no data have been found from the DB, we return extreme values
            return ReferenceData()
    else:
        raise NotImplementedError()

# Given a ReferenceData structure, this method returns a result with the correct P and Z.


def calculateZandP(refDat, computeFinalZScore):
    if refDat.Y is NaN:
        return IndicatorValue(True)  # returns an "invalid" value (NaN, NaN)

    output = IndicatorValue()
    if refDat.Y == undefined or refDat.M == undefined or refDat.L == undefined:
        return output
    # The following block of code (till the except/catch below) was enclosed
    # in a try in the original python and c#. The conditionals above and below have been
    # modified to avoid using them to control the flow (which is standard in
    # python but a bad practice in C# and most other languages).
    if refDat.L != 0:
        output.Z = (math.pow((refDat.Y / refDat.M), refDat.L) - 1.0) / (refDat.L * refDat.S)
    else:
        output.Z = math.pow((refDat.Y / refDat.M), refDat.L)
    if computeFinalZScore:
        if output.Z < -3.0:
            SD3neg = refDat.M * math.pow((1.0 + refDat.L * refDat.S * -3.0), (1.0 / refDat.L))
            SD2neg = refDat.M * math.pow((1.0 + refDat.L * refDat.S * -2.0), (1.0 / refDat.L))
            output.Z = -3.0 - (SD3neg - refDat.Y) / (SD2neg - SD3neg)
        elif output.Z > 3.0:
            SD2pos = refDat.M * math.pow((1.0 + refDat.L * refDat.S * 2.0), (1.0 / refDat.L))
            SD3pos = refDat.M * math.pow((1.0 + refDat.L * refDat.S * 3.0), (1.0 / refDat.L))
            output.Z = 3.0 + (refDat.Y - SD3pos) / (SD3pos - SD2pos)
    output.P = centile(output.Z)
    return output


# Computes the weight-for-age indicator result.
def computeWeight4Age(ageInDays, weight, sex, hasOedema):
    if hasOedema or ageInDays < 0 or ageInDays > MAXDAYS or weight < INPUT_MINWEIGHT:
        return IndicatorValue(True)
    rd = get4AgeIndicatorReference('Weight4Age', sex, round(ageInDays))
    rd.Y = weight
    return calculateZandP(rd, True)

# Computes the length/height-for-age indicator result.


def computeLengthOrHeight4Age(ageInDays, lengthOrHeight, sex):
    if ageInDays < 0 or ageInDays > MAXDAYS or lengthOrHeight < 1:
        return IndicatorValue(True)
    rd = get4AgeIndicatorReference('LengthOrHeight4Age', sex, round(ageInDays))
    rd.Y = lengthOrHeight
    return calculateZandP(rd, False)


def computeWeight4LengthOrHeight(weight, lengthOrHeight, sex, useLength, hasOedema):
    if hasOedema or not weight >= INPUT_MINWEIGHT:
        return IndicatorValue()

    if useLength:
        indicator = 'Weight4Length'
    else:
        indicator = 'Weight4Height'

    if lengthOrHeight >= MINLENGTH and lengthOrHeight <= MAXLENGTH:
        rd = get4LengthOrHeightIndicatorReference(indicator, sex, lengthOrHeight)
    else:
        return IndicatorValue()

    rd.Y = weight
    return calculateZandP(rd, True)


# Computes the anthro result for the given raw data values.
def getAnthroResult(ageInDays, sex, weight, height, isRecumbent, hasOedema, hc, muac, tsf, ssf):

    ar = {}
    ar['sex'] = sex

    ar['ageUnknown'] = ageInDays is None
    ar['heightUnknown'] = height is None

    ar['weight'] = weight if weight is not None else NaN
    ar['lengthOrHeightAdjusted'] = NaN
    ar['isLength'] = isRecumbent

    if ageInDays is not None:
        ar['ageInDays'] = ageInDays

        # first: check & adjust length/height
        if height is not None:
            adjusted = getAdjustedLengthOrHeight(int(ar['ageInDays']), height, isRecumbent)

            ar['lengthOrHeightAdjusted'] = adjusted['lengthOrHeight']
            ar['isLength'] = adjusted['isLength']

        # WAZ
        ivw = computeWeight4Age(ar['ageInDays'], ar['weight'], ar['sex'], hasOedema)
        ar['PW4A'] = ivw.P
        ar['ZW4A'] = ivw.Z

        # HAZ
        ivh = computeLengthOrHeight4Age(ar['ageInDays'], ar['lengthOrHeightAdjusted'], ar['sex'])
        ar['ZLH4A'] = ivh.Z
        ar['PLH4A'] = ivh.P

    ageAbove60CompletedMonths = False
    if not ageInDays:
        ageAbove60CompletedMonths = ageInDays > MAXDAYS
    # check if WHZ can be calculated, if not set as undefined
    if not (height and ageAbove60CompletedMonths):
        ar['lengthOrHeight'] = height
        if not ar['lengthOrHeightAdjusted']:
            if ar['isLength']:
                adjusted_height_mindays = HEIGHT_MINDAYS - 1
            else:
                adjusted_height_mindays = HEIGHT_MINDAYS
            # TODO: Figure out if we really want this. This returns an object
            ar['lengthOrHeight'] = getAdjustedLengthOrHeight(adjusted_height_mindays, height, isRecumbent)
            ar['lengthOrHeightAdjusted'] = ar['lengthOrHeight']

        # weight-for-length/height aka WHZ
        ivwhz = computeWeight4LengthOrHeight(
            ar['weight'], ar['lengthOrHeightAdjusted'], ar['sex'], ar['isLength'], hasOedema)

        ar['ZW4LH'] = roundFloat(ivwhz.Z, DEFAULTPRECISION_ZSCORE)
        ar['PW4LH'] = roundFloat(ivwhz.P, DEFAULTPRECISION_PERCENTILE)
    else:
        ar['lengthOrHeight'] = NaN
        ar['lengthOrHeightAdjusted'] = NaN
        ar['ZW4LH'] = NaN
        ar['PW4LH'] = NaN
    return ar


def keys_who_to_unicef(zscore_dict):
    mapping = (
        ('ZLH4A', 'HAZ'),
        ('ZW4A', 'WAZ'),
        ('ZW4LH', 'WHZ'),
    )

    for who_key, unicef_key in mapping:
        if who_key in zscore_dict:
            zscore_dict[unicef_key] = zscore_dict.pop(who_key)

    return zscore_dict
