from __future__ import division
from collections import OrderedDict
import logging
import copy

from wazimap.data.tables import get_datatable, get_table_id
from wazimap.data.utils import get_session, add_metadata
from wazimap.geo import geo_data
from wazimap.models.data import DataNotFound

from wazimap.data.utils import (
    collapse_categories,
    calculate_median,
    calculate_median_stat,
    merge_dicts,
    group_remainder,
    get_stat_data,
    percent,
    current_context,
    dataset_context,
)
from dynamic_profile.models import Profile, IndicatorProfile

log = logging.getLogger(__name__)

PROFILE_SECTIONS = ("indicator",)

# Education categories

COLLAPSED_ATTENDANCE_CATEGORIES = {
    "Unspecified": "Other",
    "Not applicable": "Other",
    "Do not know": "Other",
}

# Age categories

COLLAPSED_AGE_CATEGORIES = {
    "60 - 64": "60-69",
    "65 - 69": "60-69",
    "70 - 74": "70-79",
    "75 - 79": "70-79",
    "80 - 84": "80-84",
    "85 - 120": "85+",
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
HOUSEHOLD_INCOME_RECODE_2011["No income"] = "R0"
HOUSEHOLD_INCOME_RECODE_2011["R 1 - R 4800"] = "Under R4800"
HOUSEHOLD_INCOME_RECODE_2011["R 4801 - R 9600"] = "R5k - R10k"
HOUSEHOLD_INCOME_RECODE_2011["R 9601 - R 19 600"] = "R10k - R20k"
HOUSEHOLD_INCOME_RECODE_2011["R 19 601 - R 38 200"] = "R20k - R40k"
HOUSEHOLD_INCOME_RECODE_2011["R 38 201 - R 76 400"] = "R40k - R75k"
HOUSEHOLD_INCOME_RECODE_2011["R 76 401 - R 153 800"] = "R75k - R150k"
HOUSEHOLD_INCOME_RECODE_2011["R 153 801 - R 307 600"] = "R150k - R300k"
HOUSEHOLD_INCOME_RECODE_2011["R 307 601 - R 614 400"] = "R300k - R600k"
HOUSEHOLD_INCOME_RECODE_2011["R 614 001 - R 1 228 800"] = "R600k - R1.2M"
HOUSEHOLD_INCOME_RECODE_2011["R 1 228 801 - R 2 457 600"] = "R1.2M - R2.5M"
HOUSEHOLD_INCOME_RECODE_2011["R 2 457 601 or more"] = "Over R2.5M"

COLLAPSED_ANNUAL_INCOME_CATEGORIES = OrderedDict()
COLLAPSED_ANNUAL_INCOME_CATEGORIES["No income"] = "R0"
COLLAPSED_ANNUAL_INCOME_CATEGORIES["R 1 - R 4800"] = "Under R4800"
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
HOUSEHOLD_INCOME_ESTIMATE["R0"] = 0
HOUSEHOLD_INCOME_ESTIMATE["Under R4800"] = 2400
HOUSEHOLD_INCOME_ESTIMATE["R5k - R10k"] = 7200
HOUSEHOLD_INCOME_ESTIMATE["R10k - R20k"] = 14600
HOUSEHOLD_INCOME_ESTIMATE["R20k - R40k"] = 29400
HOUSEHOLD_INCOME_ESTIMATE["R40k - R75k"] = 57300
HOUSEHOLD_INCOME_ESTIMATE["R75k - R150k"] = 115100
HOUSEHOLD_INCOME_ESTIMATE["R150k - R300k"] = 230700
HOUSEHOLD_INCOME_ESTIMATE["R300k - R600k"] = 461000
HOUSEHOLD_INCOME_ESTIMATE["R600k - R1.2M"] = 921400
HOUSEHOLD_INCOME_ESTIMATE["R1.2M - R2.5M"] = 1843200
HOUSEHOLD_INCOME_ESTIMATE["Over R2.5M"] = 2500000
HOUSEHOLD_INCOME_ESTIMATE["Unspecified"] = None

HOUSEHOLD_OWNERSHIP_RECODE = {
    "Unspecified": "Other",
    "Not applicable": "Other",
    "Do not know": "Other",
}


def get_profile(geo, profile_name, request):
    session = get_session()

    try:
        comparative_geos = geo_data.get_comparative_geos(geo)
        data = {}
        data["primary_release_year"] = current_context().get("year")

        sections = list(PROFILE_SECTIONS)

        for section in sections:
            function_name = "get_%s_profile" % section
            if function_name in globals():
                func = globals()[function_name]
                data[section] = func(geo, session)

                # get profiles for comparative geometries
                for comp_geo in comparative_geos:
                    try:
                        merge_dicts(
                            data[section], func(comp_geo, session), comp_geo.geo_level
                        )
                    except KeyError as e:
                        msg = (
                            "Error merging data into %s for section '%s' from %s: KeyError: %s"
                            % (geo.geoid, section, comp_geo.geoid, e)
                        )
                        log.fatal(msg, exc_info=e)
                        raise ValueError(msg)
    finally:
        session.close()

    import json

    with open("example.json", "w") as f:
        json.dump(data, f)

    return data


def indicator_calculation(
    geo,
    session,
    column_name,
    table_name,
    order_by=False,
    percent=False,
    exclude_zero=False,
):
    """
    Get the statistics for the indicator
    """
    if order_by:
        data, total = get_stat_data(
            [column_name],
            geo,
            session,
            table_universe="Senior",
            table_dataset="Census and Community Survey",
            order_by="-total",
            exclude_zero=exclude_zero,
        )
    else:
        data, total = get_stat_data(
            [column_name],
            geo,
            session,
            table_dataset="Census and Community Survey",
            exclude_zero=exclude_zero,
        )

    return data, total


def calculate_highest(distribution, total, highest_type):
    """
    Calculate the highest in the distribution or the entire total
    """
    if highest_type == "Total":
        return total
    elif highest_type == "Distribution":
        return distribution[distribution.keys()[0]]

    else:
        return None


def column_field_value(distribution, column_field=None):
    if column_field:
        return distribution[column_field]["values"]["this"]
    return None


def group_indicators(indicator_profiles):
    """
    We need to go through all the indicators and check whether they have a parent profile indicator.
    If they do have a parent, we need to append the indicator to the parent indicator
    We will then remove all the top level indicators that have a parent.
    """
    for profile, values in indicator_profiles.items():
        for indicator in values:
            if indicator["parent_profile"]:
                header = indicator["parent_profile"]
                for i in values:
                    if i["header"] == header:
                        i["has_children"] = True
                        i["children"].append(indicator)
                        break

    for profile in indicator_profiles.keys():
        indicator_profiles[profile] = [
            indicator
            for indicator in indicator_profiles[profile]
            if indicator["parent_profile"] is None
        ]
    return indicator_profiles


def get_indicator_profile(geo, session):
    indicator_profiles = OrderedDict(
        (p.name, []) for p in Profile.objects.order_by("display_order").all()
    )
    for profile in IndicatorProfile.objects.all():
        try:
            distribution, total = indicator_calculation(
                geo,
                session,
                column_name=profile.column_name,
                table_name=profile.table_name.name,
                order_by=profile.order_by,
                exclude_zero=profile.exclude_zero,
            )
        except DataNotFound:
            indicator_profiles[profile.profile.name].append(
                {
                    "header": profile.header,
                    "summary": profile.summary,
                    "display_order": profile.display_order,
                    "data": False,
                    "parent_profile": profile.parent_profile.header
                    if profile.parent_profile
                    else None,
                    "has_children": False,
                    "children": [],
                }
            )
            indicator_profiles[profile.profile.name] = sorted(
                indicator_profiles[profile.profile.name],
                key=lambda profile: profile["display_order"],
            )
        else:
            if profile.group_remainder:
                group_remainder(distribution, profile.group_remainder)
            indicator_profiles[profile.profile.name].append(
                {
                    "header": profile.header,
                    "summary": profile.summary,
                    "chart_title": profile.chart_title,
                    "stat_values": distribution,
                    "total": total,
                    "distribution_maxima": calculate_highest(
                        distribution, total, profile.maximum_value
                    ),
                    "chart_type": profile.chart_type,
                    "column_field": column_field_value(
                        distribution, profile.column_field
                    ),
                    "display_order": profile.display_order,
                    "parent_profile": profile.parent_profile.header
                    if profile.parent_profile
                    else None,
                    "has_children": False,
                    "children": [],
                    "data": True,
                }
            )
            indicator_profiles[profile.profile.name] = sorted(
                indicator_profiles[profile.profile.name],
                key=lambda profile: profile["display_order"],
            )
    indicator_profiles = group_indicators(indicator_profiles)

    return indicator_profiles


def get_health_profile(geo, session):
    """
    Health informtion for older adults
s    """
    seeing_dist_data, _ = get_stat_data(
        "seeing",
        geo,
        session,
        table_universe="Senior",
        table_dataset="Census and Community Survey",
        order_by="-total",
    )

    selfcare_data, _ = get_stat_data(
        "self care",
        geo,
        session,
        table_universe="Senior",
        table_dataset="Census and Community Survey",
        order_by="-total",
    )

    walking_data, _ = get_stat_data(
        "walking or climbing stairs",
        geo,
        session,
        table_universe="Senior",
        table_dataset="Census and Community Survey",
        order_by="-total",
    )

    hearing_data, _ = get_stat_data(
        "hearing",
        geo,
        session,
        table_universe="Senior",
        table_dataset="Census and Community Survey",
        order_by="-total",
    )

    final_data = {
        "senior_seeing_difficulty": seeing_dist_data,
        "senior_seeing_perc": {
            "name": "Of older adults have difficulty seeing",
            "values": {
                "this": seeing_dist_data["A lot of difficulty"]["values"]["this"]
            },
        },
        "senior_selfcare_difficulty": selfcare_data,
        "senior_selfcare_perc": {
            "name": "Of older adults have difficulty taking care of themselves",
            "values": {"this": selfcare_data["A lot of difficulty"]["values"]["this"]},
        },
        "senior_walking_difficulty": walking_data,
        "senior_walking_perc": {
            "name": "Of older adults have difficulty walking or climbing the stairs",
            "values": {"this": walking_data["A lot of difficulty"]["values"]["this"]},
        },
        "senior_hearing_difficulty": hearing_data,
        "senior_hearing_perc": {
            "name": "Of older adults have difficulty hearing",
            "values": {"this": hearing_data["A lot of difficulty"]["values"]["this"]},
        },
    }

    return final_data


def birth_in_sa(birth_data):
    """
    Calculate all those born in South Africa
    """
    provinces = [
        "Western Cape",
        "Eastern Cape",
        "Northern Cape",
        "Free State",
        "North West",
        "Limpopo",
        "Gauteng",
        "Mpumalanga",
    ]
    total = 0
    for key in birth_data:
        if key in provinces:
            total += birth_data[key]["numerators"]["this"]
    return total


def get_demographics_profile(geo, session):
    # Full population of area
    # pdb.set_trace()
    pop_dist_data, total_census_pop = get_stat_data(
        ["population group"], geo, session, table_dataset="Census and Community Survey"
    )
    age_dist_data, senior_total_pop = get_stat_data(
        ["age"], geo, session, table_name="senior_population_age"
    )
    # table_universe='Senior',
    # table_dataset='Census and Community Survey')

    # language
    language_data, _ = get_stat_data(
        ["language"],
        geo,
        session,
        table_universe="Senior",
        table_dataset="Census and Community Survey",
        order_by="-total",
    )
    language_most_spoken = language_data[language_data.keys()[0]]

    # age groups
    pop_group_dist_data, _ = get_stat_data(
        ["population group"],
        geo,
        session,
        table_universe="Senior",
        table_dataset="Census and Community Survey",
    )

    senior_age_per = (senior_total_pop / total_census_pop) * 100

    # sex
    sex_data, _ = get_stat_data(
        ["gender"],
        geo,
        session,
        table_universe="Senior",
        table_dataset="Census and Community Survey",
    )

    citizen_data, _ = get_stat_data(
        ["citizenship"],
        geo,
        session,
        table_universe="Senior",
        table_dataset="Census and Community Survey",
        order_by="-total",
    )
    sa_citizen = citizen_data["Yes"]["numerators"]["this"]

    birth_data, _ = get_stat_data(
        ["birth"],
        geo,
        session,
        table_universe="Senior",
        table_dataset="Census and Community Survey",
        order_by="-total",
    )

    final_data = {
        "citizenship": citizen_data,
        "citizen_sa": {
            "name": "Of older adults are South African",
            "values": {"this": sa_citizen},
        },
        "province_of_birth_dist": birth_data,
        "province_of_birth_total": {
            "name": "older adults born in South Africa",
            "values": {"this": birth_in_sa(birth_data)},
        },
        "language_distribution": language_data,
        "language_most_spoken": language_most_spoken,
        "population_group_distribution": pop_group_dist_data,
        "age_group_distribution": age_dist_data,
        "sex_ratio": sex_data,
        "senior_citizen_total_population": {
            "name": "Older Adults",
            "values": {"this": senior_total_pop},
        },
        "total_population": {"name": "People", "values": {"this": total_census_pop}},
        "total_population_perc": {
            "name": "Of the population are older adults",
            "values": {"this": senior_age_per},
        },
    }

    if geo.square_kms:
        final_data["population_density"] = {
            "name": "people per square kilometre",
            "values": {"this": senior_total_pop / geo.square_kms},
        }

    return final_data


def get_households_profile(geo, session):
    # head of household
    # gender
    head_gender_dist, total_households = get_stat_data(
        ["gender of household head"],
        geo,
        session,
        table_universe="Households",
        order_by="gender of household head",
    )
    female_heads = head_gender_dist["Female"]["numerators"]["this"]

    # age
    u18_table = get_datatable("genderofheadofhouseholdunder18")
    objects = u18_table.get_rows_for_geo(geo, session)

    total_under_18 = float(sum(o[0] for o in objects))

    # tenure
    tenure_data, _ = get_stat_data(
        ["tenure status"],
        geo,
        session,
        table_universe="Households",
        recode=HOUSEHOLD_OWNERSHIP_RECODE,
        order_by="-total",
    )
    owned = 0
    for key, data in tenure_data.iteritems():
        if key.startswith("Owned"):
            owned += data["numerators"]["this"]

    # annual household income
    if geo.version == "2011":
        HOUSEHOLD_INCOME_RECODE = HOUSEHOLD_INCOME_RECODE_2011
    else:
        HOUSEHOLD_INCOME_RECODE = COLLAPSED_ANNUAL_INCOME_CATEGORIES
    income_dist_data, _ = get_stat_data(
        ["annual household income"],
        geo,
        session,
        table_universe="Households",
        exclude=["Unspecified", "Not applicable"],
        recode=HOUSEHOLD_INCOME_RECODE,
        key_order=HOUSEHOLD_INCOME_RECODE.values(),
    )

    # median income
    median = calculate_median_stat(income_dist_data)
    median_income = HOUSEHOLD_INCOME_ESTIMATE[median]

    # type of dwelling
    type_of_dwelling_dist, _ = get_stat_data(
        ["type of dwelling"],
        geo,
        session,
        table_universe="Households",
        recode=TYPE_OF_DWELLING_RECODE,
        order_by="-total",
    )
    informal = type_of_dwelling_dist["Shack"]["numerators"]["this"]

    # household goods
    household_goods, _ = get_stat_data(
        ["household goods"],
        geo,
        session,
        table_universe="Households",
        recode=HOUSEHOLD_GOODS_RECODE,
        key_order=sorted(HOUSEHOLD_GOODS_RECODE.values()),
    )

    return {
        "total_households": {
            "name": "Households",
            "values": {"this": total_households},
        },
        "owned": {
            "name": "Households fully owned or being paid off",
            "values": {"this": percent(owned, total_households)},
            "numerators": {"this": owned},
        },
        "type_of_dwelling_distribution": type_of_dwelling_dist,
        "informal": {
            "name": "Households that are informal dwellings (shacks)",
            "values": {"this": percent(informal, total_households)},
            "numerators": {"this": informal},
        },
        "tenure_distribution": tenure_data,
        "household_goods": household_goods,
        "annual_income_distribution": income_dist_data,
        "median_annual_income": {
            "name": "Average annual household income",
            "values": {"this": median_income},
        },
        "head_of_household": {
            "gender_distribution": head_gender_dist,
            "female": {
                "name": "Households with women as their head",
                "values": {"this": percent(female_heads, total_households)},
                "numerators": {"this": female_heads},
            },
            "under_18": {
                "name": "Households with heads under 18 years old",
                "values": {"this": total_under_18},
            },
        },
    }


def get_economics_profile(geo, session):
    if geo.version == "2016":
        return {"senior_individual_income": ""}
    senior_income, total_pop = get_stat_data(
        "individual monthly income",
        geo,
        session,
        exclude=["Not applicable"],
        recode=COLLAPSED_MONTHLY_INCOME_CATEGORIES,
        table_name="senior_individual_monthly_income",
        key_order=COLLAPSED_MONTHLY_INCOME_CATEGORIES.values(),
    )
    return {"senior_individual_income": senior_income}


def get_education_profile(geo, session):
    edu_dist_data, total_over_20 = get_stat_data(
        ["highest educational level"],
        geo,
        session,
        recode=COLLAPSED_EDUCATION_CATEGORIES,
        table_universe="Individuals 20 and older",
        key_order=EDUCATION_KEY_ORDER,
    )

    GENERAL_EDU = (
        EDUCATION_GET_OR_HIGHER
        if str(current_context().get("year")) == "2011"
        else EDUCATION_GET_OR_HIGHER_2016
    )
    general_edu, total_general_edu = get_stat_data(
        ["highest educational level"],
        geo,
        session,
        table_universe="Individuals 20 and older",
        only=GENERAL_EDU,
    )

    FURTHER_EDU = (
        EDUCATION_FET_OR_HIGHER
        if str(current_context().get("year")) == "2011"
        else EDUCATION_FET_OR_HIGHER_2016
    )
    further_edu, total_further_edu = get_stat_data(
        ["highest educational level"],
        geo,
        session,
        table_universe="Individuals 20 and older",
        only=FURTHER_EDU,
    )

    edu_split_data = {
        "percent_general_edu": {
            "name": "Completed Grade 9 or higher",
            "numerators": {"this": total_general_edu},
            "values": {"this": round(total_general_edu / total_over_20 * 100, 2)},
        },
        "percent_further_edu": {
            "name": "Completed Matric or higher",
            "numerators": {"this": total_further_edu},
            "values": {"this": round(total_further_edu / total_over_20 * 100, 2)},
        },
        "metadata": general_edu["metadata"],
    }

    profile = {
        "educational_attainment_distribution": edu_dist_data,
        "educational_attainment": edu_split_data,
    }

    return profile
