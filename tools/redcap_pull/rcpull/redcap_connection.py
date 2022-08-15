"""Module providing code to push and pull data from a REDCap project."""

from json import JSONDecodeError
from typing import Any, List, Mapping
from requests import Response
import requests


class REDCapConnection:
    """Class managing the connection to a REDCap project.

    Provides a post method to adapting classes.
    See `ProjectReader`
    """

    def __init__(self, *, token: str, url: str) -> None:
        """
        Initializes a REDCap connection using the given project token and URL.

        Args:
          token: API token for the REDCap project.
          url: URL of REDCap instance
        """
        self.__token = token
        self.__url = url

    def post_request(self,
                     *,
                     data: Mapping[str, str],
                     result_format: str = None,
                     return_format: str = 'json') -> Any:
        """
        Posts a request to the REDCap project with the given data object.

        Returns:
          The response from posting the request.

        Raises:
          REDCapConnectionException if there is an error connecting to the specified project
        """
        data.update({'token': self.__token, 'returnFormat': return_format})
        if result_format:
            data['format'] = result_format
        response = requests.post(self.__url, data=data)

        return response

    def request_json_value(self, *, data: Mapping[str, str],
                           message: str) -> Any:
        """
        Posts a request to the REDCap project with the given data object
        expecting a JSON value.

        Returns:
          The object for the JSON value.

        Raises:
          REDCapConnectionException if the response has an error.
        """
        response = self.post_request(data=data, result_format='json')
        if not response.ok:
            raise REDCapConnectionError(
                message=error_message(message=message, response=response))
        try:
            return response.json()
        except JSONDecodeError as error:
            raise REDCapConnectionError(message=message,
                                        error=error) from error

    def request_text_value(self,
                           *,
                           data: Mapping[str, str],
                           result_format: str = None,
                           message: str) -> str:
        """Posts a request to the REDCap project with the given data object
        expecting a text value.

        Returns:
          The text string for the returned value.

        Raises:
          REDCapConnectionError if the response has an error.
        """
        response = self.post_request(data=data, result_format=result_format)
        if not response.ok:
            message = "cannot get project XML"
            raise REDCapConnectionError(
                message=error_message(message=message, response=response))

        return response.text


def error_message(*, message: str, response: Response) -> str:
    """
    Build an error message from the given message and HTTP response.

    Returns:
      The error string
    """
    return (f"Error: {message}\nHTTP Error:{response.status_code} "
            f"{response.reason}: {response.text}")


class REDCapConnectionError(Exception):
    """Exception class representing error connecting to a REDCap project."""

    def __init__(self, *, error: Exception = None, message: str) -> None:
        super().__init__()
        self._error = error
        self._message = message

    def __str__(self) -> str:
        if self.error:
            return f"{self.message}\n{self.error}"

        return self.message

    @property
    def error(self):
        """The exception causing this error."""
        return self._error

    @property
    def message(self):
        """The error message."""
        return self._message


class ProjectReader:
    """
    Adapts a `REDCapConnection` with methods to read from the project of the
    connection. Caches instruments and fields of the project.
    """

    def __init__(self, *, connection: REDCapConnection) -> None:
        self.__connection = connection
        self.__instruments = None
        self.__fields = None

    @classmethod
    def create(cls, *, token: str, url: str):
        """Create a project reader with a new REDCap connection.

        Args:
          token: API token for the REDCap project.
          url: URL of REDCap instance
        """
        return ProjectReader(connection=REDCapConnection(token=token, url=url))

    def get_project_info(self) -> str:
        """Get the information for this project."""
        data = {'content': 'project'}
        message = "Unable to get project information"
        return self.__connection.request_json_value(data=data, message=message)

    def get_project_xml(self) -> str:
        """
        Get the XML configuration for the project.

        Returns:
          The XML for project.

        Raises:
          REDCapConnectionException if there is an error connecting to the specified project
        """
        return self.__connection.request_text_value(
            data={
                'content': 'project_xml',
                'returnMetadataOnly': 'true',
                'exportFiles': 'false',
                'exportSurveyFields': 'false',
                'exportDataAccessGroups': 'false',
            },
            message="cannot get project XML")

    def get_instruments(self) -> List[Mapping[str, str]]:
        """
        Get the instruments for the project.

        Returns:
          The list of instruments for the project.
          For example
          [{
            "instrument_name": "form_header",
            "instrument_label": "Form Header"
          }]

        Raises:
          REDCapConnectionException if there is an error connecting to the specified project
        """
        if self.__instruments is None:
            self.__instruments = self.__connection.request_json_value(
                data={'content': 'instrument'},
                message="Unable to get project instruments")

        return self.__instruments

    def get_data_dictionary(
            self,
            *,
            form: str = None,
            fields: List[str] = None) -> List[Mapping[str, str]]:
        """
        Get the data dictionary for the project.

        Note: this is what REDCap refers to as the metadata.

        Returns:
          The data dictionary for the project as CSV.

        Raises:
          REDCapConnectionException if there is an error connecting to the specified project
        """
        data = {'content': 'metadata'}
        if form:
            data['forms[0]'] = form

        if fields:
            for i, field in enumerate(fields):
                data[f'fields[{ i }]'] = field

        return self.__connection.request_text_value(
            data=data,
            result_format='csv',
            message="Unable to get project metadata")

    def get_fields(self) -> List[Mapping[str, str]]:
        """
        Get the fields for the project.

        Returns:
          The list of fields for the project.
          [{
            "original_field_name":"dsccttic",
            "choice_value":"",
            "export_field_name":"dsccttic"
          }]

        Raises:
          REDCapConnectionException if there is an error connecting to the specified project
        """
        if self.__fields is None:
            self.__fields = self.__connection.request_json_value(
                data={'content': 'exportFieldNames'},
                message="Unable to get project fields")

        return self.__fields
