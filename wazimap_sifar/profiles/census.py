from __future__ import division
from collections import OrderedDict
import logging

from wazimap.data.tables import get_datatable, get_table_id
from wazimap.data.utils import get_session, add_metadata
from wazimap.geo import geo_data

from wazimap.data.utils import (
    collapse_categories, calculate_median, calculate_median_stat, merge_dicts,
    group_remainder, get_stat_data, percent, current_context, dataset_context)

log = logging.getLogger(__name__)

PROFILE_SECTIONS = (
    'demographics',  # population group, age group in 5 years, age in completed years
    'economics',  # individual monthly income, type of sector, official employment status
    #'service_delivery',  # source of water, refuse disposal
    #'households',  # household heads, etc.
    #'children',  # child-related stats
    #'child_households',  # households headed by children
    'health')

# Education categories

COLLAPSED_ATTENDANCE_CATEGORIES = {
    'Unspecified': 'Other',
    'Not applicable': 'Other',
    'Do not know': 'Other',
}

# Age categories

COLLAPSED_AGE_CATEGORIES = {
    '60 - 64': '60-69',
    '65 - 69': '60-69',
    '70 - 74': '70-79',
    '75 - 79': '70-79',
    '80 - 84': '80-84',
    '85 - 120': '85+',
}

# Income categories
#
# Note from StatsSA on different income categories between '2011 census'
# and '2011 census along 2016 boundaries':
# The community profile dataset (Census 2011) was based on the first version of
# Census 2011 data released in 2013. The first version did not have information
# such as migration, fertility and complete employment. In 2015 the census
# dataset was revised to include all the missing information. The process of
# revision also ensured that the entire dataset is consistent with the
# questionnaire and metadata. Income variable was one of the variables affected
# and the individual income categories were corrected to match metadata,
# however, that did not change the totals. All the products from 2015 dataset,
# i.e., Census 2011 10% sample and Census 2011(Boundaries 2016) are based on the
# revised version. The above mentioned products are final and they are in line
# with metadata. In addition we have kept all the income categories as annual
# and the corresponding monthly income can be obtained in a questionnaire and
# metadata.

COLLAPSED_MONTHLY_INCOME_CATEGORIES = OrderedDict()
COLLAPSED_MONTHLY_INCOME_CATEGORIES["No income"] = "R0"
COLLAPSED_MONTHLY_INCOME_CATEGORIES["R 1 - R 400"] = "Under R400"
COLLAPSED_MONTHLY_INCOME_CATEGORIES["R 401 - R 800"] = "R400 - R800"
COLLAPSED_MONTHLY_INCOME_CATEGORIES["R 801 - R 1 600"] = "R800 - R2k"
COLLAPSED_MONTHLY_INCOME_CATEGORIES["R 1 601 - R 3 200"] = "R2k - R3k"
COLLAPSED_MONTHLY_INCOME_CATEGORIES["R 3 201 - R 6 400"] = "R3k - R6k"
COLLAPSED_MONTHLY_INCOME_CATEGORIES["R 6 401 - R 12 800"] = "R6k - R13k"
COLLAPSED_MONTHLY_INCOME_CATEGORIES["R 12 801 - R 25 600"] = "R13k - R26k"
COLLAPSED_MONTHLY_INCOME_CATEGORIES["R 25 601 - R 51 200"] = "R26k - R51k"
COLLAPSED_MONTHLY_INCOME_CATEGORIES["R 51 201 - R 102 400"] = "R51k - R102k"
COLLAPSED_MONTHLY_INCOME_CATEGORIES["R 102 401 - R 204 800"] = "Over R102k"
COLLAPSED_MONTHLY_INCOME_CATEGORIES["R 204 801 or more"] = "Over R102k"
COLLAPSED_MONTHLY_INCOME_CATEGORIES["Unspecified"] = "Unspecified"

ESTIMATED_MONTHLY_INCOME_CATEGORIES = {}
ESTIMATED_MONTHLY_INCOME_CATEGORIES["R0"] = 0
ESTIMATED_MONTHLY_INCOME_CATEGORIES["Under R400"] = 200
ESTIMATED_MONTHLY_INCOME_CATEGORIES["R400 - R800"] = 600
ESTIMATED_MONTHLY_INCOME_CATEGORIES["R800 - R2k"] = 1200
ESTIMATED_MONTHLY_INCOME_CATEGORIES["R2k - R3k"] = 2400
ESTIMATED_MONTHLY_INCOME_CATEGORIES["R3k - R6k"] = 4800
ESTIMATED_MONTHLY_INCOME_CATEGORIES["R6k - R13k"] = 9600
ESTIMATED_MONTHLY_INCOME_CATEGORIES["R13k - R26k"] = 19200
ESTIMATED_MONTHLY_INCOME_CATEGORIES["R26k - R51k"] = 38400
ESTIMATED_MONTHLY_INCOME_CATEGORIES["R51k - R102k"] = 76800
ESTIMATED_MONTHLY_INCOME_CATEGORIES["Over R102k"] = 204800
ESTIMATED_MONTHLY_INCOME_CATEGORIES["Unspecified"] = None

ESTIMATED_ANNUAL_INCOME_CATEGORIES = {}
ESTIMATED_ANNUAL_INCOME_CATEGORIES["R0"] = 0
ESTIMATED_ANNUAL_INCOME_CATEGORIES["Under R4800"] = 2400
ESTIMATED_ANNUAL_INCOME_CATEGORIES["R5k - R10k"] = 7500
ESTIMATED_ANNUAL_INCOME_CATEGORIES["R10k - R20k"] = 15000
ESTIMATED_ANNUAL_INCOME_CATEGORIES["R20k - R40k"] = 30000
ESTIMATED_ANNUAL_INCOME_CATEGORIES["R40k - R75k"] = 57500
ESTIMATED_ANNUAL_INCOME_CATEGORIES["R75k - R150k"] = 117000
ESTIMATED_ANNUAL_INCOME_CATEGORIES["R150k - R300k"] = 225000
ESTIMATED_ANNUAL_INCOME_CATEGORIES["R300k - R600k"] = 450000
ESTIMATED_ANNUAL_INCOME_CATEGORIES["R600k - R1.2M"] = 900000
ESTIMATED_ANNUAL_INCOME_CATEGORIES["R1.2M - R2.5M"] = 1350000
ESTIMATED_ANNUAL_INCOME_CATEGORIES["Over R2.5M"] = 2457600
ESTIMATED_ANNUAL_INCOME_CATEGORIES["Unspecified"] = None

# Household income
HOUSEHOLD_INCOME_RECODE_2011 = OrderedDict()
HOUSEHOLD_INCOME_RECODE_2011['No income'] = 'R0'
HOUSEHOLD_INCOME_RECODE_2011['R 1 - R 4800'] = 'Under R4800'
HOUSEHOLD_INCOME_RECODE_2011['R 4801 - R 9600'] = 'R5k - R10k'
HOUSEHOLD_INCOME_RECODE_2011['R 9601 - R 19 600'] = 'R10k - R20k'
HOUSEHOLD_INCOME_RECODE_2011['R 19 601 - R 38 200'] = 'R20k - R40k'
HOUSEHOLD_INCOME_RECODE_2011['R 38 201 - R 76 400'] = 'R40k - R75k'
HOUSEHOLD_INCOME_RECODE_2011['R 76 401 - R 153 800'] = 'R75k - R150k'
HOUSEHOLD_INCOME_RECODE_2011['R 153 801 - R 307 600'] = 'R150k - R300k'
HOUSEHOLD_INCOME_RECODE_2011['R 307 601 - R 614 400'] = 'R300k - R600k'
HOUSEHOLD_INCOME_RECODE_2011['R 614 001 - R 1 228 800'] = 'R600k - R1.2M'
HOUSEHOLD_INCOME_RECODE_2011['R 1 228 801 - R 2 457 600'] = 'R1.2M - R2.5M'
HOUSEHOLD_INCOME_RECODE_2011['R 2 457 601 or more'] = 'Over R2.5M'

COLLAPSED_ANNUAL_INCOME_CATEGORIES = OrderedDict()
COLLAPSED_ANNUAL_INCOME_CATEGORIES['No income'] = 'R0'
COLLAPSED_ANNUAL_INCOME_CATEGORIES['R 1 - R 4800'] = 'Under R4800'
COLLAPSED_ANNUAL_INCOME_CATEGORIES["R 4801 - R 9600"] = "R5k - R10k"
COLLAPSED_ANNUAL_INCOME_CATEGORIES["R 9601 - R 19200"] = "R10k - R20k"
COLLAPSED_ANNUAL_INCOME_CATEGORIES["R 19201 - R 38400"] = "R20k - R40k"
# Note double space is intentional to match SuperWeb export.
COLLAPSED_ANNUAL_INCOME_CATEGORIES["R 38401 -  R 76800"] = "R40k - R75k"
COLLAPSED_ANNUAL_INCOME_CATEGORIES["R 38401 - R 76800"] = "R40k - R75k"
COLLAPSED_ANNUAL_INCOME_CATEGORIES["R 76801 - R 153600"] = "R75k - R150k"
COLLAPSED_ANNUAL_INCOME_CATEGORIES["R 153601 - R 307200"] = "R150k - R300k"
COLLAPSED_ANNUAL_INCOME_CATEGORIES["R 307201 - R 614400"] = "R300k - R600k"
# Note missing space is intentional to match SuperWeb export.
COLLAPSED_ANNUAL_INCOME_CATEGORIES["R 614401- R 1228800"] = "R600k - R1.2M"
COLLAPSED_ANNUAL_INCOME_CATEGORIES["R 1228801 - R 2457600"] = "R1.2M - R2.5M"
COLLAPSED_ANNUAL_INCOME_CATEGORIES["R2457601 or more"] = "Over R2.5M"

HOUSEHOLD_INCOME_ESTIMATE = {}
HOUSEHOLD_INCOME_ESTIMATE['R0'] = 0
HOUSEHOLD_INCOME_ESTIMATE['Under R4800'] = 2400
HOUSEHOLD_INCOME_ESTIMATE['R5k - R10k'] = 7200
HOUSEHOLD_INCOME_ESTIMATE['R10k - R20k'] = 14600
HOUSEHOLD_INCOME_ESTIMATE['R20k - R40k'] = 29400
HOUSEHOLD_INCOME_ESTIMATE['R40k - R75k'] = 57300
HOUSEHOLD_INCOME_ESTIMATE['R75k - R150k'] = 115100
HOUSEHOLD_INCOME_ESTIMATE['R150k - R300k'] = 230700
HOUSEHOLD_INCOME_ESTIMATE['R300k - R600k'] = 461000
HOUSEHOLD_INCOME_ESTIMATE['R600k - R1.2M'] = 921400
HOUSEHOLD_INCOME_ESTIMATE['R1.2M - R2.5M'] = 1843200
HOUSEHOLD_INCOME_ESTIMATE['Over R2.5M'] = 2500000
HOUSEHOLD_INCOME_ESTIMATE['Unspecified'] = None

HOUSEHOLD_OWNERSHIP_RECODE = {
    'Unspecified': 'Other',
    'Not applicable': 'Other',
    'Do not know': 'Other',
}

# Sanitation categories

SHORT_WATER_SOURCE_CATEGORIES = {
    "Regional/local water scheme (operated by municipality or other water services provider)":
    "Service provider",
    "Water tanker":
    "Tanker",
    "Spring":
    "Spring",
    "Other":
    "Other",
    "Dam/pool/stagnant water":
    "Dam",
    "River/stream":
    "River",
    "Not applicable":
    "N/A",
    "Borehole":
    "Borehole",
    "Rain water tank":
    "Rainwater tank",
    "Water vendor":
    "Vendor",
    # CS 2016:
    "Borehole in the yard":
    "Borehole in yard",
    "Borehole outside the yard":
    "Borehole outside yard",
    "Neighbours tap":
    "Neighbours tap",
    "Flowing water/stream/river":
    "River",
    "Piped (tap) water inside the dwelling/house":
    "Piped water inside house",
    "Piped (tap) water inside yard":
    "Piped water inside yard",
    "Piped water on community stand":
    "Piped water on community stand",
    "Public/communal tap":
    "Public/communal tap",
    "Rain-water tank in yard":
    "Rainwater tank",
    "Water-carrier/tanker":
    "Tanker",
    "Well":
    "Well"
}

SHORT_WATER_SUPPLIER_CATEGORIES = {
    "A municipality": "Service provider",
    "Other water scheme (e.g. community water supply)": "Water scheme",
    "A water vendor": "Vendor",
    "Own service (e.g. private borehole; own source on a farm; et":
    "Own service",
    "Flowing water/stream/river/spring/rain water": "Natural source",
    "Do not know": "Do not know",
    "Unspecified": "Unspecified"
}

SHORT_REFUSE_DISPOSAL_CATEGORIES = {
    "Removed by local authority/private company less often":
    "Service provider (not regularly)",
    "Own refuse dump":
    "Own dump",
    "Communal refuse dump":
    "Communal dump",
    "Other":
    "Other",
    "Not applicable":
    "N/A",
    "No rubbish disposal":
    "None",
    "Unspecified":
    "Unspecified",
    "Removed by local authority/private company at least once a week":
    "Service provider (regularly)",
    # CS 2016:
    "Removed by local authority/private company/community members at least once a week":
    "Service provider (regularly)",
    "Removed by local authority/private company/community members less often than once a week":
    "Service provider (not regularly)",
    "Communal container/central collection point":
    "Communal container",
    "Dump or leave rubbish anywhere (no rubbish disposal)":
    " None"
}

COLLAPSED_TOILET_CATEGORIES = {
    "Flush toilet (connected to sewerage system)":
    "Flush toilet",
    "Flush toilet (with septic tank)":
    "Flush toilet",
    "Chemical toilet":
    "Chemical toilet",
    "Pit toilet with ventilation (VIP)":
    "Pit toilet",
    "Pit toilet without ventilation":
    "Pit toilet",
    "Bucket toilet":
    "Bucket toilet",
    "Other":
    "Other",
    "None":
    "None",
    "Unspecified":
    "Unspecified",
    "Not applicable":
    "N/A",
    # CS 2016:
    "Flush toilet connected to a public sewerage system":
    "Flush toilet",
    "Flush toilet connected to a septic tank or conservancy tank":
    "Flush toilet",
    "Chemical toilet":
    "Chemical toilet",
    "Pit latrine/toilet with ventilation pipe":
    "Pit toilet",
    "Pit latrine/toilet without ventilation pipe":
    "Pit toilet",
    "Ecological toilet (e.g. urine diversion; enviroloo; etc.)":
    "Ecological toilet",
    "Bucket toilet (collected by municipality)":
    "Bucket toilet",
    "Bucket toilet (emptied by household)":
    "Bucket toilet"
}

HOUSEHOLD_GOODS_RECODE = {
    'cell phone': 'Cellphone',
    'computer': 'Computer',
    'dvd player': 'DVD player',
    'electric/gas stove': 'Stove',
    'landline/telephone': 'Telephone',
    'motor-car': 'Car',
    'radio': 'Radio',
    'refrigerator': 'Fridge',
    'satellite television': 'Satellite TV',
    'television': 'TV',
    'vacuum cleaner': 'Vacuum cleaner',
    'washing machine': 'Washing machine',
}

# Type of dwelling

TYPE_OF_DWELLING_RECODE = {
    'House or brick/concrete block structure on a separate stand or yard or on a farm':
    'House',
    'Traditional dwelling/hut/structure made of traditional materials':
    'Traditional',
    'Flat or apartment in a block of flats':
    'Apartment',
    'Cluster house in complex':
    'Cluster house',
    'Townhouse (semi-detached house in a complex)':
    'Townhouse',
    'Semi-detached house':
    'Semi-detached house',
    'House/flat/room in backyard':
    'Flat in backyard',
    'Informal dwelling (shack; in backyard)':
    'Shack',
    'Informal dwelling (shack; not in backyard; e.g. in an informal/squatter settlement or on a farm)':
    'Shack',
    'Room/flatlet on a property or larger dwelling/servants quarters/granny flat':
    'Room or flatlet',
    'Caravan/tent':
    'Caravan/tent',
    'Other':
    'Other',
    'Unspecified':
    'Unspecified',
    'Not applicable':
    'N/A',
    #Cs 2016:
    'Formal dwelling/house/flat/room in backyard':
    'Flat in backyard',
    'Informal dwelling/shack in backyard':
    'Shack',
    'Traditional dwelling/hut/structure made of traditional mater':
    'Traditional',
    'Room/flatlet on a property or larger dwelling/servants quart':
    'Room or flatlet',
    'Formal dwelling/house or brick/concrete block structure on a':
    'House',
    'Informal dwelling/shack not in backyard (e.g. in an informal':
    'Shack'
}

COLLAPSED_EMPLOYMENT_CATEGORIES = {
    'Employed': 'In labour force',
    'Unemployed': 'In labour force',
    'Discouraged work-seeker': 'In labour force',
    'Other not economically active': 'Not in labour force',
    'Age less than 15 years': 'Not in labour force',
    'Not applicable': 'Not in labour force'
}

INTERNET_ACCESS_RECODE = {
    "Connection from a library":
    "Library",
    "Connection in the dwelling":
    "In dwelling",
    "Other":
    "Other",
    "Any place via other mobile access service":
    "Other mobile service",
    "Any place via cellphone":
    "Cellphone",
    "Internet cafe > 2km from dwelling":
    "Internet cafe > 2km from dwelling",
    "Internet cafe 2km or less from dwelling":
    "Internet cafe < 2km from dwelling",
    "Connection at place of work":
    "Place of work",
    "At school/university/college":
    "Place of education"
}

ELECTRICITY_ACCESS_RECODE = {
    "Connected to other source which household is not paying for":
    "Other source (paying for)",
    "Connected to other source which household pays for (e.g. con":
    "Other source (not paying for)"
}


def get_profile(geo, profile_name, request):
    session = get_session()

    try:
        comparative_geos = geo_data.get_comparative_geos(geo)
        data = {}
        data['primary_release_year'] = current_context().get('year')

        sections = list(PROFILE_SECTIONS)
        if geo.geo_level in ['country', 'province']:
            sections.append('crime')

        for section in sections:
            function_name = 'get_%s_profile' % section
            if function_name in globals():
                func = globals()[function_name]
                data[section] = func(geo, session)

                # get profiles for comparative geometries
                for comp_geo in comparative_geos:
                    try:
                        merge_dicts(data[section], func(comp_geo, session),
                                    comp_geo.geo_level)
                    except KeyError as e:
                        msg = "Error merging data into %s for section '%s' from %s: KeyError: %s" % (
                            geo.geoid, section, comp_geo.geoid, e)
                        log.fatal(msg, exc_info=e)
                        raise ValueError(msg)
    finally:
        session.close()

    # tweaks to make the data nicer
    # show 3 largest groups on their own and group the rest as 'Other'
    #group_remainder(data['service_delivery']['water_source_distribution'], 5)
    # group_remainder(data['service_delivery']['refuse_disposal_distribution'],
    #                 5)
    # group_remainder(data['service_delivery']['toilet_facilities_distribution'],
    #                 5)
    group_remainder(data['demographics']['language_distribution'], 7)
    #group_remainder(data['demographics']['province_of_birth_distribution'], 7)
    #group_remainder(data['demographics']['region_of_birth_distribution'], 5)
    # group_remainder(data['households']['type_of_dwelling_distribution'], 5)
    # group_remainder(data['households']['tenure_distribution'], 6)
    # group_remainder(data['child_households']['type_of_dwelling_distribution'],
    #                 5)

    # if current_context().get('year') == 'latest':
    #     group_remainder(
    #         data['service_delivery']['water_supplier_distribution'], 5)
    #     group_remainder(data['service_delivery']['electricity_access'], 5)

    return data


def get_health_profile(geo, session):
    """
    Health informtion for older adults
    """
    seeing_dist_data, _ = get_stat_data(
        'seeing',
        geo,
        session,
        table_name='senior_population_seeing',
        order_by='-total')

    selfcare_data, _ = get_stat_data(
        'self care',
        geo,
        session,
        table_name='senior_population_selfcare',
        order_by='-total')

    walking_data, _ = get_stat_data(
        'walking or climbing stairs',
        geo,
        session,
        table_name='senior_population_walking',
        order_by='-total')

    hearing_data, _ = get_stat_data(
        'hearing',
        geo,
        session,
        table_name='senior_population_hearing',
        order_by='-total')

    final_data = {
        'senior_seeing_difficulty': seeing_dist_data,
        'senior_seeing_perc': {
            'name': 'Of older adults have difficulty seeing',
            'values': {
                'this':
                seeing_dist_data['A lot of difficulty']['values']['this']
            }
        },
        'senior_selfcare_difficulty': selfcare_data,
        'senior_selfcare_perc': {
            'name':
            'Of older adults have difficulty taking care of themselves',
            'values': {
                'this': selfcare_data['A lot of difficulty']['values']['this']
            }
        },
        'senior_walking_difficulty': walking_data,
        'senior_walking_perc': {
            'name':
            'Of older adults have difficulty walking or climbing the stairs',
            'values': {
                'this': walking_data['A lot of difficulty']['values']['this']
            }
        },
        'senior_hearing_difficulty': hearing_data,
        'senior_hearing_perc': {
            'name': 'Of older adults have difficulty hearing',
            'values': {
                'this': hearing_data['A lot of difficulty']['values']['this']
            }
        }
    }

    return final_data


def get_demographics_profile(geo, session):
    #Full population of area
    if geo.geo_level == 'subplace':
        pop_dist_data, total_census_pop = get_stat_data(
            ['population group'],
            geo,
            session,
            table_name='populationgroup_2016')
    else:
        pop_dist_data, total_census_pop = get_stat_data(
            ['population group'],
            geo,
            session,
            table_dataset='Census and Community Survey')
    # population group
    pop_dist_data, total_pop = get_stat_data(
        ['population group'],
        geo,
        session,
        table_name='senior_population_group')

    # language
    language_data, _ = get_stat_data(
        ['language'],
        geo,
        session,
        table_name='senior_language_age',
        order_by='-total')
    language_most_spoken = language_data[language_data.keys()[0]]

    # age groups
    age_dist_data, total_age = get_stat_data(
        ['age'], geo, session, table_name='senior_population_age')

    senior_age_per = (total_pop / total_census_pop) * 100

    # sex
    sex_data, _ = get_stat_data(
        ['gender'],
        geo,
        session,
        table_name='senior_population_gender',
    )

    final_data = {
        'language_distribution': language_data,
        'language_most_spoken': language_most_spoken,
        'population_group_distribution': pop_dist_data,
        'age_group_distribution': age_dist_data,
        'sex_ratio': sex_data,
        'senior_citizen_total_population': {
            'name': 'Older Adults',
            'values': {
                'this': total_pop
            }
        },
        'total_population': {
            "name": "People",
            "values": {
                "this": total_census_pop
            },
        },
        'total_population_perc': {
            'name': 'Of the population are older adults',
            'values': {
                'this': senior_age_per
            }
        }
    }

    if geo.square_kms:
        final_data['population_density'] = {
            'name': "people per square kilometre",
            'values': {
                "this": total_pop / geo.square_kms
            },
        }

    # # citizenship
    # citizenship_dist, _ = get_stat_data(
    #     ['citizenship'],
    #     geo,
    #     session,
    #     table_dataset='Census and Community Survey',
    #     order_by='-total')

    # sa_citizen = citizenship_dist['Yes']['numerators']['this']

    # final_data['citizenship_distribution'] = citizenship_dist
    # final_data['citizenship_south_african'] = {
    #     'name': 'South African citizens',
    #     'values': {
    #         'this': percent(sa_citizen, total_pop)
    #     },
    #     'numerators': {
    #         'this': sa_citizen
    #     },
    # }

    # # migration
    # province_of_birth_dist, _ = get_stat_data(
    #     ['province of birth'],
    #     geo,
    #     session,
    #     table_dataset='Census and Community Survey',
    #     exclude_zero=True,
    #     order_by='-total')

    # final_data['province_of_birth_distribution'] = province_of_birth_dist

    # def region_recode(field, key):
    #     if key == 'Born in South Africa':
    #         return 'South Africa'
    #     else:
    #         return {
    #             'Not applicable': 'Other',
    #         }.get(key, key)

    # region_of_birth_dist, _ = get_stat_data(
    #     ['region of birth'],
    #     geo,
    #     session,
    #     table_dataset='Census and Community Survey',
    #     exclude_zero=True,
    #     order_by='-total',
    #     recode=region_recode)

    # if 'South Africa' in region_of_birth_dist:
    #     born_in_sa = region_of_birth_dist['South Africa']['numerators']['this']
    # else:
    #     born_in_sa = 0

    # final_data['region_of_birth_distribution'] = region_of_birth_dist
    # final_data['born_in_south_africa'] = {
    #     'name': 'Born in South Africa',
    #     'values': {
    #         'this': percent(born_in_sa, total_pop)
    #     },
    #     'numerators': {
    #         'this': born_in_sa
    #     },
    # }

    return final_data


def get_households_profile(geo, session):
    # head of household
    # gender
    head_gender_dist, total_households = get_stat_data(
        ['gender of household head'],
        geo,
        session,
        table_universe='Households',
        order_by='gender of household head')
    female_heads = head_gender_dist['Female']['numerators']['this']

    # age
    u18_table = get_datatable('genderofheadofhouseholdunder18')
    objects = u18_table.get_rows_for_geo(geo, session)

    total_under_18 = float(sum(o[0] for o in objects))

    # tenure
    tenure_data, _ = get_stat_data(
        ['tenure status'],
        geo,
        session,
        table_universe='Households',
        recode=HOUSEHOLD_OWNERSHIP_RECODE,
        order_by='-total')
    owned = 0
    for key, data in tenure_data.iteritems():
        if key.startswith('Owned'):
            owned += data['numerators']['this']

    # annual household income
    if geo.version == '2011':
        HOUSEHOLD_INCOME_RECODE = HOUSEHOLD_INCOME_RECODE_2011
    else:
        HOUSEHOLD_INCOME_RECODE = COLLAPSED_ANNUAL_INCOME_CATEGORIES
    income_dist_data, _ = get_stat_data(
        ['annual household income'],
        geo,
        session,
        table_universe='Households',
        exclude=['Unspecified', 'Not applicable'],
        recode=HOUSEHOLD_INCOME_RECODE,
        key_order=HOUSEHOLD_INCOME_RECODE.values())

    # median income
    median = calculate_median_stat(income_dist_data)
    median_income = HOUSEHOLD_INCOME_ESTIMATE[median]

    # type of dwelling
    type_of_dwelling_dist, _ = get_stat_data(
        ['type of dwelling'],
        geo,
        session,
        table_universe='Households',
        recode=TYPE_OF_DWELLING_RECODE,
        order_by='-total')
    informal = type_of_dwelling_dist['Shack']['numerators']['this']

    # household goods
    household_goods, _ = get_stat_data(
        ['household goods'],
        geo,
        session,
        table_universe='Households',
        recode=HOUSEHOLD_GOODS_RECODE,
        key_order=sorted(HOUSEHOLD_GOODS_RECODE.values()))

    return {
        'total_households': {
            'name': 'Households',
            'values': {
                'this': total_households
            },
        },
        'owned': {
            'name': 'Households fully owned or being paid off',
            'values': {
                'this': percent(owned, total_households)
            },
            'numerators': {
                'this': owned
            },
        },
        'type_of_dwelling_distribution': type_of_dwelling_dist,
        'informal': {
            'name': 'Households that are informal dwellings (shacks)',
            'values': {
                'this': percent(informal, total_households)
            },
            'numerators': {
                'this': informal
            },
        },
        'tenure_distribution': tenure_data,
        'household_goods': household_goods,
        'annual_income_distribution': income_dist_data,
        'median_annual_income': {
            'name': 'Average annual household income',
            'values': {
                'this': median_income
            },
        },
        'head_of_household': {
            'gender_distribution': head_gender_dist,
            'female': {
                'name': 'Households with women as their head',
                'values': {
                    'this': percent(female_heads, total_households)
                },
                'numerators': {
                    'this': female_heads
                },
            },
            'under_18': {
                'name': 'Households with heads under 18 years old',
                'values': {
                    'this': total_under_18
                },
            }
        },
    }


def get_economics_profile(geo, session):
    senior_income, total_pop = get_stat_data(
        'individual monthly income',
        geo,
        session,
        exclude=['Not applicable'],
        recode=COLLAPSED_MONTHLY_INCOME_CATEGORIES,
        table_name='senior_individual_monthly_income',
        key_order=COLLAPSED_MONTHLY_INCOME_CATEGORIES.values())

    # # employment status
    # employ_status, total_workers = get_stat_data(
    #     ['official employment status'],
    #     geo,
    #     session,
    #     exclude=['Age less than 15 years', 'Not applicable'],
    #     order_by='official employment status',
    #     table_name='officialemploymentstatus')

    return {'senior_individual_income': senior_income}


def get_education_profile(geo, session):
    edu_dist_data, total_over_20 = get_stat_data(
        ['highest educational level'],
        geo,
        session,
        recode=COLLAPSED_EDUCATION_CATEGORIES,
        table_universe='Individuals 20 and older',
        key_order=EDUCATION_KEY_ORDER)

    GENERAL_EDU = EDUCATION_GET_OR_HIGHER if str(current_context().get(
        'year')) == '2011' else EDUCATION_GET_OR_HIGHER_2016
    general_edu, total_general_edu = get_stat_data(
        ['highest educational level'],
        geo,
        session,
        table_universe='Individuals 20 and older',
        only=GENERAL_EDU)

    FURTHER_EDU = EDUCATION_FET_OR_HIGHER if str(current_context().get(
        'year')) == '2011' else EDUCATION_FET_OR_HIGHER_2016
    further_edu, total_further_edu = get_stat_data(
        ['highest educational level'],
        geo,
        session,
        table_universe='Individuals 20 and older',
        only=FURTHER_EDU)

    edu_split_data = {
        'percent_general_edu': {
            "name": "Completed Grade 9 or higher",
            "numerators": {
                "this": total_general_edu
            },
            "values": {
                "this": round(total_general_edu / total_over_20 * 100, 2)
            }
        },
        'percent_further_edu': {
            "name": "Completed Matric or higher",
            "numerators": {
                "this": total_further_edu
            },
            "values": {
                "this": round(total_further_edu / total_over_20 * 100, 2)
            }
        },
        'metadata': general_edu['metadata']
    }

    profile = {
        'educational_attainment_distribution': edu_dist_data,
        'educational_attainment': edu_split_data
    }

    return profile
