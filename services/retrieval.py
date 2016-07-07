import db, json, flask

from utils import jsonp
from flask import Response
from flask.ext.restful import Resource


class Doc(Resource):
    """
    Container class for all web requests for single documents
    """

    @jsonp
    def get(self, lang, smallkey):
        """
        A REST endpoint for fetching a single document from the doc store.

        :param lang: A two letter language code for the response
        :param smallkey: A short key which uniquely identifies the dataset
        :type smallkey: str
        :returns: Response -- a JSON response object; None with a 404 code if the key was not matched
        """
        doc = db.get_doc(smallkey, lang, self.version)
        if doc is None:
            return None, 404
        return Response(json.dumps(doc), mimetype='application/json')


class Docs(Resource):
    """
    Container class for all web requests for sets of documents
    """

    @jsonp
    def get(self, lang, smallkeylist, sortarg=''):
        """
        A REST endpoint for fetching a single document from the doc store.

        :param lang: A two letter language code for the response
        :type lang: str
        :param smallkeylist: A comma separated string of short keys each of which identifies a single dataset
        :type smallkeylist: str
        :param sortargs: 'sort' if returned list should be sorted based on geometry
        :type sortargs: str
        :returns: list -- an array of JSON configuration fragments
        (empty error objects are added where keys do not match)
        """
        keys = [x.strip() for x in smallkeylist.split(',')]
        unsorted_docs = [db.get_doc(smallkey, lang, self.version) for smallkey in keys]
        if sortarg == 'sort':
            # used to retrieve geometryType
            dbdata = [db.get_raw(smallkey) for smallkey in keys]
            lines = []
            polys = []
            points = []
            for rawdata, doc in zip(dbdata, unsorted_docs):
                # Point
                if rawdata["data"]["en"]["geometryType"] == "esriGeometryPoint":
                    points.append(doc)
                # Polygon
                elif rawdata["data"]["en"]["geometryType"] == "esriGeometryPolygon":
                    polys.append(doc)
                # Line
                else:
                    lines.append(doc)
            # Concat lists (first in docs = bottom of layer list)
            docs = polys + lines + points
        else:
            docs = unsorted_docs
        return Response(json.dumps(docs), mimetype='application/json')


class DocV1(Doc):
    def __init__(self):
        super(DocV1, self).__init__()
        self.version = '1'


class DocsV1(Docs):
    def __init__(self):
        super(DocsV1, self).__init__()
        self.version = '1'


class DocV2(Doc):
    def __init__(self):
        super(DocV2, self).__init__()
        self.version = '2'


class DocsV2(Docs):
    def __init__(self):
        super(DocsV2, self).__init__()
        self.version = '2'


class Version(Doc):
    def get(self):
        return flask.g.version_no
