import json
import time
import unittest
import urllib

import requests


__author__ = "Tatiana Al-Chueyr Pereira Martins"
__license__ = "GNU GPL v2"


class ElasticSearchException(Exception):
    """
    ESTester exception.
    """
    pass


class ExtendedTestCase(unittest.TestCase):
    """
    Extends unittest.TestCase providing two new methods:
        pre_setup :: run before method setUp (unittest.TestCase)
        post_teardown :: run after method tearDown (unittest.TestCase)
    """

    maxDiff = None

    def __call__(self, *args, **kwds):
        """
        Wrapper around default __call__ method to perform common test
        set up. This means that user-defined Test Cases aren't required to
        include a call to super().setUp().
        """
        try:
            self._pre_setup()
        except (KeyboardInterrupt, SystemExit):
            raise

        super(ExtendedTestCase, self).__call__(*args, **kwds)

        try:
            self._post_teardown()
        except (KeyboardInterrupt, SystemExit):
            raise

    def _pre_setup(self):
        "Hook method for setting up the test fixture before default setUp."
        pass

    def _post_teardown(self):
        "Hook method for setting up the test fixture after default tearDown."
        pass


class ElasticSearchQueryTestCase(ExtendedTestCase):
    """
    Extends unittest.TestCase (estester.ExtendedTestCase).

    Allows testing ElasticSearch queries in a easy way.
    """

    index = "sample.test"  # must be lower case
    reset_index = True  # warning: if this is True, index will be cleared up
    host = "http://0.0.0.0:9200/"
    mappings = {}
    proxies = {}
    fixtures = []
    timeout = 5
    settings = {}

    def _pre_setup(self):
        """
        Load self.fixtures to the ElasticSearch index. Read load_fixtures
        for more information.

        Uses the following class attributes:
            reset_index: delete index before loading data (default: True)
        """
        if self.reset_index:
            self.delete_index()
        self.create_index()
        self.load_fixtures()

    def _post_teardown(self):
        """
        Clear up ElasticSearch index, if reset_index is True.

        Uses the following class attributes:
            index: name of the index (default: sample.test)
            host: ElasticSearch host (default: http://localhost:9200/)
            reset_index: delete index after running tests (default: True)
        """
        if self.reset_index:
            self.delete_index()

    def create_index(self):
        """
        Use the following class attributes:
            index: name of the index (default: sample.test)
            host: ElasticSearch host (default: http://localhost:9200/)
            settings: used to define analyzers (optional) (i)
            mappings: attribute specific mappings according to types

        To create an empty index in ElasticSearch.

        (i) http://www.elasticsearch.org/guide/en/elasticsearch/guide/current/
        configuring-analyzers.html
        """
        url = "{0}{1}/"
        url = url.format(self.host, self.index)
        data = {}
        if self.mappings:
            data["mappings"] = self.mappings
        if self.settings:
            data["settings"] = self.settings
        json_data = json.dumps(data)
        response = requests.put(url, proxies=self.proxies, data=json_data)

    def load_fixtures(self):
        """
        Use the following class attributes:
            index: name of the index (default: sample.test)
            host: ElasticSearch host (default: http://localhost:9200/)
            fixtures: list of items to be loaded (default: [])
            timeout: time in seconds to wait index load (default: 5s)

        Example of fixtures:
        [
            {
                "type": "book",
                "id": "1",
                "body": {"title": "The Hitchhiker's Guide to the Galaxy"}
            },
            {
                "type": "book",
                "id": "2",
                "body": {"title": "The Restaurant at the End of the Universe"}
            }
        ]

        Each item of the fixtures list represents a document at ElasticSearch
        and must contain:
            type: type of the document
            id: unique identifier
            body: json with fields of values of document
        """
        for doc in self.fixtures:
            doc_type = urllib.quote_plus(doc["type"])
            doc_id = urllib.quote_plus(doc["id"])
            doc_body = doc["body"]
            url = "{0}{1}/{2}/{3}"
            url = url.format(self.host, self.index, doc_type, doc_id)
            response = requests.put(
                url,
                data=json.dumps(doc_body),
                proxies=self.proxies)
            if not response.status_code in [200, 201]:
                raise ElasticSearchException(response.text)
        time.sleep(self.timeout)
        # http://0.0.0.0:9200/sample.test/_search

    def delete_index(self):
        """
        Deletes test index. Uses class attribute:
            index: name of the index to be deleted
        """
        url = "{0}{1}/".format(self.host, self.index)
        requests.delete(url, proxies=self.proxies)

    def search(self, query=None):
        """
        Run a search <query> (JSON) and returns the JSON response.
        """
        url = "{0}{1}/_search".format(self.host, self.index)
        query = {} if query is None else query
        response = requests.post(
            url,
            data=json.dumps(query),
            proxies=self.proxies)
        return json.loads(response.text)

    def tokenize(self, text, analyzer):
        """
        Run <analyzer> on text and returns a dict containing the tokens.
        """
        url = "{0}{1}/_analyze".format(self.host, self.index)
        if analyzer != "default":
            url += "?analyzer={0}".format(analyzer)
        response = requests.post(
            url,
            data=json.dumps(text),
            proxies=self.proxies)
        return json.loads(response.text)


class MultipleIndexesQueryTestCase(ElasticSearchQueryTestCase):
    """
    Extends unittest.TestCase (estester.ElasticSearchQueryTestCase).

    Allows testing ElasticSearch queries in multiple indexes.

    Same:
    - timeout
    - proxies
    - host
    - reset_index

    Main difference:
    - index
    - mappings
    - settings

    Are replaced by:
        data = {
            "index.name": {
                "mappings": {}
                "settings": {}
                "fixtures": []
            }
        }
    """

    data = {}

    def _pre_setup(self):
        """
        Load self.fixtures to the ElasticSearch index. Read load_fixtures
        for more information.

        Uses the following class attributes:
            reset_index: delete index before loading data (default: True)
        """
        for index_name, index in self.data.items():
            if self.reset_index:
                self.delete_index(index_name)
            settings = index.get("settings", {})
            mappings = index.get("mappings", {})
            fixtures = index.get("fixtures", {})
            self.create_index(index_name, settings, mappings)
            self.load_fixtures(index_name, fixtures)

    def _post_teardown(self):
        """
        Clear up ElasticSearch index, if reset_index is True.

        Uses the following class attributes:
            index: name of the index (default: sample.test)
            host: ElasticSearch host (default: http://localhost:9200/)
            reset_index: delete index after running tests (default: True)
        """
        for index_name, index in self.data.items():
            if self.reset_index:
                self.delete_index(index_name)

    def create_index(self, index_name="", settings="", mappings=""):
        """
        Use the following class attributes:
            index: name of the index (default: sample.test)
            host: ElasticSearch host (default: http://localhost:9200/)
            settings: used to define analyzers (optional) (i)
            mappings: attribute specific mappings according to types

        To create an empty index in ElasticSearch.

        (i) http://www.elasticsearch.org/guide/en/elasticsearch/guide/current/
        configuring-analyzers.html
        """
        url = "{0}{1}/"
        index = index_name or self.index
        url = url.format(self.host, index)
        data = {}
        if self.mappings:
            data["mappings"] = mappings or self.mappings
        if self.settings:
            data["settings"] = settings or self.settings
        json_data = json.dumps(data)
        response = requests.put(url, proxies=self.proxies, data=json_data)

    def load_fixtures(self, index_name="", fixtures=""):
        """
        Use the following class attributes:
            index: name of the index (default: sample.test)
            host: ElasticSearch host (default: http://localhost:9200/)
            fixtures: list of items to be loaded (default: [])
            timeout: time in seconds to wait index load (default: 5s)

        Example of fixtures:
        [
            {
                "type": "book",
                "id": "1",
                "body": {"title": "The Hitchhiker's Guide to the Galaxy"}
            },
            {
                "type": "book",
                "id": "2",
                "body": {"title": "The Restaurant at the End of the Universe"}
            }
        ]

        Each item of the fixtures list represents a document at ElasticSearch
        and must contain:
            type: type of the document
            id: unique identifier
            body: json with fields of values of document
        """
        index = index_name or self.index
        fixtures = fixtures or self.fixtures
        for doc in fixtures:
            doc_type = urllib.quote_plus(doc["type"])
            doc_id = urllib.quote_plus(doc["id"])
            doc_body = doc["body"]
            url = "{0}{1}/{2}/{3}"
            url = url.format(self.host, index, doc_type, doc_id)
            response = requests.put(
                url,
                data=json.dumps(doc_body),
                proxies=self.proxies)
            if not response.status_code in [200, 201]:
                raise ElasticSearchException(response.text)
        time.sleep(self.timeout)
        # http://0.0.0.0:9200/sample.test/_search

    def delete_index(self, index_name=""):
        """
        Deletes test index. Uses class attribute:
            index: name of the index to be deleted
        """
        index = index_name or self.index
        url = "{0}{1}/".format(self.host, self.index)
        requests.delete(url, proxies=self.proxies)

    def search(self, query=None):
        """
        Run a search <query> (JSON) and returns the JSON response.
        """
        url = "{0}/_search".format(self.host)
        query = {} if query is None else query
        response = requests.post(
            url,
            data=json.dumps(query),
            proxies=self.proxies)
        return json.loads(response.text)

    def search_in_index(self, index, query=None):
        """
        Run a search <query> (JSON) and returns the JSON response.
        """
        url = "{0}/{1}/_search".format(self.host, index)
        query = {} if query is None else query
        response = requests.post(
            url,
            data=json.dumps(query),
            proxies=self.proxies)
        return json.loads(response.text)
