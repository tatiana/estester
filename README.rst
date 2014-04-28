ESTester
========

ESTester is a Python package to help testing ElasticSearch queries.

It provides a TestCase which allows you to load data to a test index
and validate the behavior of your search queries.


How to install
--------------

Using pip to install from Cheeseshop ::

    pip install estester

Or, install from the source ::

    git clone git://github.com/tatiana/estester.git
    python setup.py install


How to use
----------

ESTester defines a main testing class, called ElasticSearchQueryTestCase.

In order to use it, you should subclass it and redefine one or more class attributes:

- index: name of the index (default: sample.test)
- host: ElasticSearch host (default: http://localhost:9200/)
- fixtures: list of items to be loaded (default: [])
- timeout: time in seconds to wait index load (default: 5s)
- reset_index: delete index after running tests (default: True)

Basic example, only re-defining fixtures: ::

    from estester import ElasticSearchQueryTestCase

    SAMPLE_QUERY = {
        "query": {
            "query_string": {
                "fields": [
                    "name"
                ],
                "query": "nina"
            }
        }
    }

    class QueryTestCase(ElasticSearchQueryTestCase):

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

        def test_query_by_nina_returns_one_result(self):
            response = self.search(SAMPLE_QUERY)
            self.assertEqual(response["hits"]["total"], 1)
            self.assertEqual(response["hits"]["hits"][0]["_id"], u"1")
            self.assertEqual(response["hits"]["hits"][0]["_source"], {u"name": u"Nina Fox"})


ESTester tests
--------------

In order to run ESTester tests, make sure you have ElasticSearch installed locally and it is up ::
    make setup
    make test


Compatibility
-------------

ESTester was successfully used to test queries on top of versions 19.x and 90.x of ElasticSearch.

For more information on this amazing open-source search engine, read:
http://www.elasticsearch.org/


License
-------

ESTester is GNU GPL 2: ::

    < ESTester: ElasticSearch Tester >
    Copyright (C) 2013 - Tatiana Al-Chueyr Pereira Martins

    ESTester is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 2 of the License.

    ESTester is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ESTester. If not, see <http://www.gnu.org/licenses/>.
