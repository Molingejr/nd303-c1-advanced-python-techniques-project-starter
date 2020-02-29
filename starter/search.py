from collections import namedtuple, defaultdict
from enum import Enum
import operator
from exceptions import UnsupportedFeature
from models import NearEarthObject, OrbitPath


class DateSearch(Enum):
    """
    Enum representing supported date search on Near Earth Objects.
    """
    between = 'between'
    equals = 'equals'

    @staticmethod
    def list():
        """
        :return: list of string representations of DateSearchType enums
        """
        return list(map(lambda output: output.value, DateSearch))


class Query(object):
    """
    Object representing the desired search query operation to build. The Query uses the Selectors
    to structure the query information into a format the NEOSearcher can use for date search.
    """

    Selectors = namedtuple('Selectors', ['date_search', 'number', 'filters', 'return_object'])
    DateSearch = namedtuple('DateSearch', ['type', 'values'])
    ReturnObjects = {'NEO': NearEarthObject, 'Path': OrbitPath}

    def __init__(self, **kwargs):
        """
        :param kwargs: dict of search query parameters to determine which SearchOperation query to use
        """
        # TODO: What instance variables will be useful for storing on the Query object?
        self.number = kwargs.get('number')
        self.date = kwargs.get('date')
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('end_date')
        self.filter = kwargs.get('filter')
        self.return_object = kwargs.get('return_object')

    def build_query(self):
        """
        Transforms the provided query options, set upon initialization, into a set of Selectors that the NEOSearcher
        can use to perform the appropriate search functionality

        :return: QueryBuild.Selectors namedtuple that translates the dict of query options into a SearchOperation
        """

        # TODO: Translate the query parameters into a QueryBuild.Selectors object
        if self.date:
            date_search = Query.DateSearch(DateSearch.equals.name, self.date)
        else:
            date_search = Query.DateSearch(DateSearch.between.name, [self.start_date, self.end_date])

        return_object = Query.ReturnObjects.get(self.return_object)

        filters = []

        if self.filter:
            options = Filter.create_filter_options(self.filter)
            for k, v in options.items():
                for filter_ in v:
                    split_filter = filter_.split(':')
                    option, operation, value = split_filter[0], split_filter[1], split_filter[-1]
                    filters.append(Filter(option, k, operation, value))

        return Query.Selectors(date_search, self.number, filters, return_object)


class Filter(object):
    """
    Object representing optional filter options to be used in the date search for Near Earth Objects.
    Each filter is one of Filter.Operators provided with a field to filter on a value.
    """
    Options = {
        # TODO: Create a dict of filter name to the NearEarthObject or OrbitalPath property
        'diameter': 'diameter_min_km',
        'distance': 'miss_distance_kilometers',
        'is_hazardous': 'is_potentially_hazardous_asteroid'
    }

    Operators = {
        # TODO: Create a dict of operator symbol to an Operators method, see README Task 3 for hint
        '>': operator.gt,
        '=': operator.eq,
        '>=': operator.ge,
    }

    def __init__(self, field, object, operation, value):
        """
        :param field:  str representing field to filter on
        :param field:  str representing object to filter on
        :param operation: str representing filter operation to perform
        :param value: str representing value to filter for
        """
        self.field = field
        self.object = object
        self.operation = operation
        self.value = value

    @staticmethod
    def create_filter_options(filter_options):
        """
        Class function that transforms filter options raw input into filters

        :param input: list in format ["filter_option:operation:value_of_option", ...]
        :return: defaultdict with key of NearEarthObject or OrbitPath and value of empty list or list of Filters
        """

        # TODO: return a defaultdict of filters with key of NearEarthObject or OrbitPath and value of empty list or list of Filters
        data = defaultdict(list)

        for filter_option in filter_options:
            chosen_filter = filter_option.split(':')[0]

            if hasattr(NearEarthObject(), Filter.Options.get(chosen_filter)):
                data['NearEarthObject'].append(filter_option)
            elif hasattr(OrbitPath(), Filter.Options.get(chosen_filter)):
                data['OrbitPath'].append(filter_option)
        return data

    def apply(self, results):
        """
        Function that applies the filter operation onto a set of results

        :param results: List of Near Earth Object results
        :return: filtered list of Near Earth Object results
        """
        # TODO: Takes a list of NearEarthObjects and applies the value of its filter operation to the results
        neo_filtered_list = []

        for neo in results:
            field = Filter.Options.get(self.field)
            operation = Filter.Operators.get(self.operation)
            value = getattr(neo, field)

            if operation(str(value), str(self.value)):
                neo_filtered_list.append(neo)

        return neo_filtered_list


class NEOSearcher(object):
    """
    Object with date search functionality on Near Earth Objects exposed by a generic
    search interface get_objects, which, based on the query specifications, determines
    how to perform the search.
    """

    def __init__(self, db):
        """
        :param db: NEODatabase holding the NearEarthObject instances and their OrbitPath instances
        """
        self.db = db
        # TODO: What kind of an instance variable can we use to connect DateSearch to how we do search?
        self.orbit_date = dict(db.orbit_date)
        self.date_search = None

    def get_objects(self, query):
        """
        Generic search interface that, depending on the details in the QueryBuilder (query) calls the
        appropriate instance search function, then applys any filters, with distance as the last filter.

        Once any filters provided are applied, return the number of requested objects in the query.return_object
        specified.

        :param query: Query.Selectors object with query information
        :return: Dataset of NearEarthObjects or OrbitalPaths
        """
        # TODO: This is a generic method that will need to understand, using DateSearch, how to implement search
        # TODO: Write instance methods that get_objects can use to implement the two types of DateSearch your project
        # TODO: needs to support that then your filters can be applied to. Remember to return the number specified in
        # TODO: the Query.Selectors as well as in the return_type from Query.Selectors

        self.date_search = query.date_search.type
        date = query.date_search.values

        neos = []

        if self.date_search == DateSearch.between.name:
            neos = self.return_date_search_between(self.orbit_date, date[0], date[1])
        elif self.date_search == DateSearch.equals.name:
            neos = self.return_date_search_equal(self.orbit_date, date)

        dist_filter = None
        for chosen_filter in query.filters:
            if chosen_filter.field == 'distance':
                dist_filter = chosen_filter
                continue
            neos = chosen_filter.apply(neos)
        orbits = self.return_orbit_paths_from_neos(neos)

        filtered_orbits = orbits
        filtered_neos = neos

        if dist_filter:
            filtered_orbits = dist_filter.apply(orbits)
            filtered_neos = self.return_neo_from_orbit_path(filtered_orbits)

        filtered_neos = list(set(filtered_neos))
        filtered_orbits = list(set(filtered_orbits))

        if query.return_object == OrbitPath:
            return filtered_orbits[: int(query.number)]
        return filtered_neos[: int(query.number)]

    @staticmethod
    def return_date_search_equal(orbit_path, date):
        neos_date_equal = []
        for k, v in orbit_path.items():
            neos_date_equal = neos_date_equal + v if k == date else neos_date_equal
        return neos_date_equal

    @staticmethod
    def return_date_search_between(orbit_path, start_date, end_date):
        neos_date_between = []
        for k, v in orbit_path.items():
            if start_date <= k <= end_date:
                neos_date_between += v
        return neos_date_between

    @staticmethod
    def return_orbit_paths_from_neos(neos):
        neo_paths = []
        for neo in neos:
            neo_paths += neo.orbits
        return neo_paths

    def return_neo_from_orbit_path(self, orbit_paths):
        neo = [self.db.neo_name.get(path.neo_name) for path in orbit_paths]
        return neo
