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

        #if self.settings:
        #    self.load_settings()

        #if self.mappings:
        #    self.load_mappings()

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

        (i) http://www.elasticsearch.org/guide/en/elasticsearch/guide/current/configuring-analyzers.html
        """
        url = "{0}{1}/"
        url = url.format(self.host, self.index)
        data = {}
        if self.mappings:
            data["mappings"] = self.mappings
        if self.settings:
            data["settings"] = self.settings
        response = requests.put(url, proxies=self.proxies, data=json.dumps(data))

    def load_mappings(self):
         """
         Use the following class attributes:
             index: name of the index (default: sample.test)
             host: ElasticSearch host (default: http://localhost:9200/)
             mapping: dictionary containing type mappings (default: {})
 
         And load mappings to existent index.
         """
         for doc_type, type_mapping in self.mappings.items():
             url = "{0}{1}/{2}/_mapping"
             url = url.format(self.host, self.index, doc_type)
             response = requests.put(
                 url,
                 data=json.dumps({doc_type: type_mapping}),
                 proxies=self.proxies)

    def load_settings(self):
         """
         Use the following class attributes:
             index: name of the index (default: sample.test)
             host: ElasticSearch host (default: http://localhost:9200/)
             mapping: dictionary containing type mappings (default: {})
 
         And load mappings to existent index.
         """
         url = "{0}{1}/_close".format(self.host, self.index)
         response = requests.post(url, proxies=self.proxies)

         url = "{0}{1}/_settings"
         url = url.format(self.host, self.index)
         response = requests.put(
             url,
             data=json.dumps(self.settings),
             proxies=self.proxies)
         import pdb; pdb.set_trace()
         url = "{0}{1}/_open".format(self.host, self.index)
         response = requests.post(url, proxies=self.proxies)

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
