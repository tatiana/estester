import unittest
from mock import patch
from estester import ElasticSearchQueryTestCase, ExtendedTestCase,\
    MultipleIndexesQueryTestCase


SIMPLE_QUERY = {
    "query": {
        "query_string": {
            "fields": [
                "name"
            ],
            "query": "nina"
        }
    }
}


def raise_interruption(self):
    raise KeyboardInterrupt


class TestExtendedTestCase(ExtendedTestCase):

    value = 1

    def _pre_setup(self):
        self.value = self.value * 2

    def setUp(self):
        self.value = self.value ** 3

    def test_pre_setup(self):
        self.assertEqual(self.value, 8)


class DefaultValuesTestCase(unittest.TestCase):

    def test_default_values(self):
        ESQTC = ElasticSearchQueryTestCase
        self.assertEqual(ESQTC.index, "sample.test")
        self.assertEqual(ESQTC.reset_index, True)
        self.assertEqual(ESQTC.host, "http://0.0.0.0:9200/")
        self.assertEqual(ESQTC.fixtures, [])
        self.assertEqual(ESQTC.timeout, 5)
        self.assertEqual(ESQTC.proxies, {})


class SimpleMultipleIndexesQueryTestCase(MultipleIndexesQueryTestCase):

    data = {
        "personal": {
            "fixtures": [
                {
                    "type": "contact",
                    "id": "1",
                    "body": {"name": "Dmitriy"}
                },
                {
                    "type": "contact",
                    "id": "2",
                    "body": {"name": "Agnessa"}
                }
            ]
        },
        "professional": {
            "fixtures": [
                {
                    "type": "contact",
                    "id": "1",
                    "body": {"name": "Nikolay"}
                }
            ]
        }
    }

    def test_search_all_indexes(self):
        response = self.search()
        expected = [
            {
                u'_score': 1.0,
                u'_type': u'contact',
                u'_id': u'1',
                u'_source': {u'name': u'Dmitriy'},
                u'_index': u'personal'
            },
            {
                u'_score': 1.0,
                u'_type': u'contact',
                u'_id': u'2',
                u'_source': {u'name': u'Agnessa'},
                u'_index': u'personal'
            },
            {
                u'_score': 1.0,
                u'_type': u'contact',
                u'_id': u'1', u'_source': {u'name': u'Nikolay'},
                u'_index': u'professional'
            }
        ]
        self.assertEqual(response["hits"]["total"], 3)
        self.assertEqual(sorted(response["hits"]["hits"]), sorted(expected))

    def test_search_one_index_that_has_item(self):
        query = {
            "query": {
                "text": {
                    "name": "Agnessa"
                }
            }
        }
        response = self.search_in_index("personal", query)
        self.assertEqual(response["hits"]["total"], 1)
        expected = {u'name': u'Agnessa'}
        self.assertEqual(response["hits"]["hits"][0]["_source"], expected)

    def test_search_one_index_that_doesnt_have_item(self):
        query = {
            "query": {
                "text": {
                    "name": "Agnessa"
                }
            }
        }
        response = self.search_in_index("professional", query)
        self.assertEqual(response["hits"]["total"], 0)


class SimpleQueryTestCase(ElasticSearchQueryTestCase):

    fixtures = [
        {
            "type": "dog",
            "id": "1",
            "body": {"name": "Nina Fox"}
        },
        {
            "type": "dog",
            "id": "2",
            "body": {"name": "Charles M."}
        }
    ]
    timeout = 1

    def test_search_by_nothing_returns_two_results(self):
        response = self.search()
        expected = {u"name": u"Nina Fox"}
        self.assertEqual(response["hits"]["total"], 2)
        self.assertEqual(response["hits"]["hits"][0]["_id"], u"1")
        self.assertEqual(response["hits"]["hits"][1]["_id"], u"2")

    def test_search_by_nina_returns_one_result(self):
        response = self.search(SIMPLE_QUERY)
        expected = {u"name": u"Nina Fox"}
        self.assertEqual(response["hits"]["total"], 1)
        self.assertEqual(response["hits"]["hits"][0]["_id"], u"1")
        self.assertEqual(response["hits"]["hits"][0]["_source"], expected)

    def test_tokenize_with_default_analyzer(self):
        response = self.tokenize("Nothing to declare", "default")
        items_list = response["tokens"]
        self.assertEqual(len(items_list), 2)
        tokens = [item["token"] for item in items_list]
        self.assertEqual(sorted(tokens), ["declare", "nothing"])

    def test_tokenize_with_default_analyzer(self):
        response = self.tokenize("Nothing to declare", "whitespace")
        items_list = response["tokens"]
        self.assertEqual(len(items_list), 3)
        tokens = [item["token"] for item in items_list]
        self.assertEqual(sorted(tokens), ['"Nothing', 'declare"', "to"])
