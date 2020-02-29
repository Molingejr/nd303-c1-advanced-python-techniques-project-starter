from models import OrbitPath, NearEarthObject
import csv


class NEODatabase(object):
    """
    Object to hold Near Earth Objects and their orbits.

    To support optimized date searching, a dict mapping of all orbit date paths to the Near Earth Objects
    recorded on a given day is maintained. Additionally, all unique instances of a Near Earth Object
    are contained in a dict mapping the Near Earth Object name to the NearEarthObject instance.
    """

    def __init__(self, filename):
        """
        :param filename: str representing the pathway of the filename containing the Near Earth Object data
        """
        # TODO: What data structures will be needed to store the NearEarthObjects and OrbitPaths?
        # TODO: Add relevant instance variables for this.
        self.filename = filename
        self.orbit_date = {}
        self.neo_name = {}

    def load_data(self, filename=None):
        """
        Loads data from a .csv file, instantiating Near Earth Objects and their OrbitPaths by:
           - Storing a dict of orbit date to list of NearEarthObject instances
           - Storing a dict of the Near Earth Object name to the single instance of NearEarthObject

        :param filename:
        :return:
        """

        if not (filename or self.filename):
            raise Exception('Cannot load data, no filename provided')

        filename = filename or self.filename

        # TODO: Load data from csv file.
        # TODO: Where will the data be stored?

        with open(filename, 'r') as neo_file:
            neo_data = csv.DictReader(neo_file)

            for row_data in neo_data:
                orbit_path = OrbitPath(**row_data)

                if not self.neo_name.get(row_data['name']):
                    self.neo_name[row_data['name']] = NearEarthObject(**row_data)

                neo = self.neo_name.get(row_data['name'])

                neo.update_orbits(orbit_path)

                if not self.orbit_date.get(row_data['close_approach_date']):
                    self.orbit_date[row_data['close_approach_date']] = []

                self.orbit_date[row_data['close_approach_date']].append(neo)

        return None
