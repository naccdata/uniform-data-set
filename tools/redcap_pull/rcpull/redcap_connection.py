import requests

class REDCapConnection:

    def __init__(self, *, token: str, url: str) -> None:
        """
        Initializes a REDCap connection using the given project token and URL.

        Args:
          token: API token for the REDCap project.
          url: URL of REDCap instance

        Raises:
          REDCapConnectionException if there is an error connecting to the specified project
        """
        self.__token = token
        self.__url = url

    def get_project_xml(self):
        data = {
            'token': self.__token,
            'content': 'project_xml',
            'format': 'json',
            'returnMetadataOnly': 'true',
            'exportFiles': 'false',
            'exportSurveyFields': 'false',
            'exportDataAccessGroups': 'false',
            'returnFormat': 'json'
        }
        r = requests.post(self.__url, data=data)
        print('HTTP Status: ' + str(r.status_code))
        print(r.json())

    def get_instrument(self):
        data = {
            'token': '47391AC17215AD7D531A2550C71035F2',
            'content': 'instrument',
            'format': 'json',
            'returnFormat': 'json'
        }
        r = requests.post('https://nacc.redcap.rit.uw.edu/api/',data=data)

class REDCapConnectionException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)