import pan.xapi
import pan.config
import ssl

class PanosClientError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

def should_update(current, proposed):
    results_added = list(set(proposed) - set(current))
    results_removed = list(set(current) - set(proposed))

    if not results_added and not results_removed:
        return False, None

    results = {
        "removed": results_removed,
        "added": results_added
    }
    return True, results

def xml_python(xapi, result=False):
    xpath = None
    if result:
        if (xapi.element_result is None or
                not len(xapi.element_result)):
            return None
        elem = xapi.element_result
        # select all child elements
        xpath = '*'
    else:
        if xapi.element_root is None:
            return None
        elem = xapi.element_root

    try:
        conf = pan.config.PanConfig(config=elem)
    except pan.config.PanConfigError:
        raise pan.config.PanConfigError
    d = conf.python(xpath)
    return d

class PanosClient:
    """
    This is a PANOS-XML API client that will allow one to interact with PANOS-XAML API

    Attributes:
        xapi (xapi): Used by pan-python to interact with PANOS-XML API.
    """
    def __init__(self, api_key, hostname, ignore_cert_error=False):
        """
        The constructor for the PanosClient class.

        Parameters:
           api_key (str): The API key used for authenticating to the PANOS-XML API endpoint
           hostname (str): The FQDN/IP address of the PANOS appliance
           ignore_cert_error (bool): Used to determine the type of ssl context to create
        """
        try:
            if ignore_cert_error:
                ssl_context = ssl.SSLContext()
                ssl_context.verify_mode = ssl.CERT_NONE
            else:
                ssl_context = None

            self.xapi = pan.xapi.PanXapi(
                api_key=api_key,
                hostname=hostname,
                ssl_context=ssl_context
            )
        except pan.xapi.PanXapiError as e:
            raise Exception(e)

    def get(self, xpath):
        """
        A method for getting current configuration of specified xpath

        Parameters:
            xpath (str): The xpath to get current configuration from

        Returns:
            dict: A dictionary of the configuration
        """

        self.xapi.get(xpath=xpath)
        return xml_python(self.xapi)

    def delete(self, xpath):
        self.xapi.delete(xpath=xpath)

    def set(self, xpath, element):
        self.xapi.set(xpath, element)

    def edit(self, xpath, element):
        self.xapi.edit(xpath, element)

    def commit(self):
        self.xapi.commit()
