'''
Author: Thomas Theisen

Objective: Provide all functionality related to the use of Neo4j for graphing, querying,
           and data insertions. 

'''

#Python Modules
#-----------------------------------------------------------------------------#
from py2neo import Graph, Node, Relationship, NodeMatcher, cypher
from py2neo.ogm import Property, GraphObject
from py2neo.matching import RelationshipMatcher
import pandas as pd
import urllib3

#Interal Modules
#-----------------------------------------------------------------------------#
import credentials

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

username = credentials.configuration['GraphDatabaseCredentials']['USERNAME']
password = credentials.configuration['GraphDatabaseCredentials']['PASSWORD']

graph = Graph("https://hobby-dkkjnogldadkgbkenkemipcl.dbs.graphenedb.com:24780/db/data/", user=username, password=password) 

class Document(GraphObject):    
    __primarylabel__ = "Document"
    __primarykey__ = "identifier"     
    identifier = Property()    

class Keyword(GraphObject):    
    __primarylabel__ = "Keyword"
    __primarykey__ = "word"    
    word = Property()    

class Author(GraphObject):
    __primarylabel__ = "Author"
    __primarykey__ = "name"
    name = Property()

def add_keyword(keyword):
    k = Keyword()
    k.word = keyword
    graph.push(k)

def add_document(identifier):
    d = Document()
    d.identifier = identifier
    graph.push(d)

def add_author(name):
    a = Author()
    a.name = name
    graph.push(a)

def keyword_node_exists(keyword):
    matcher = NodeMatcher(graph)
    m = matcher.match("Keyword", word = keyword).first()
    if m is None:
        return False
    else:
        return True

def document_node_exists(document):
    matcher = NodeMatcher(graph)
    m = matcher.match("Document", identifier = document).first()
    if m is None:
        return False
    else:
        return True

def author_node_exists(author):
    matcher = NodeMatcher(graph)
    m = matcher.match("Author", name = author).first()
    if m is None:
        return False
    else:
        return True

def get_document_node(document):
    matcher = NodeMatcher(graph)
    node = matcher.match("Document", identifier = document).first()
    return node

def get_keyword_node(keyword):
    matcher = NodeMatcher(graph)
    node = matcher.match("Keyword", word = keyword).first()
    return node

def get_author_node(author):
    matcher = NodeMatcher(graph)
    node = matcher.match("Author", name = author).first()
    return node

def find_or_create_relationship_keywords(document, keywords):
    add_document(document)
    document_node = get_document_node(document)
    for keyword, weight in keywords.items():   
        if keyword_node_exists(keyword) is False:
            add_keyword(keyword)
        keyword_node = get_keyword_node(keyword)
        r = Relationship(document_node, "Contains", keyword_node, weight = weight)
        graph.create(r)
    print('Updated Keyword Graph')

def find_or_create_relationship_interaction(document, interaction):

    author1 = interaction[0]
    author2 = interaction[1]

    add_document(document)
    
    weight_author_to_author = get_weight_author_to_author(author1, author2)
    weight_document_to_author1 = get_weight_document_to_author(document, author1)
    weight_document_to_author2 = get_weight_document_to_author(document, author2)

    author_weight = {author1: weight_document_to_author1, author2: weight_document_to_author2}

    document_node = get_document_node(document)

    for author, weight in author_weight.items():
        if author_node_exists(author) is False:
            add_author(author)
        author_node = get_author_node(author)
        doc_auth_relation = Relationship(author_node, "Commented", document_node, weight = (weight + 1)) #Number of interactions with post
        graph.create(doc_auth_relation)
    auth_auth_relation = Relationship(get_author_node(author1), "Interacted", get_author_node(author2), weight = (weight_author_to_author + 1))
    graph.create(auth_auth_relation)
    print('Updated Associations Graph')

def get_number_of_nodes(nodeType):
    return graph.evaluate("MATCH (a:{}) RETURN count(a)".format(nodeType))

def get_nodes_with_keyword(keyword):
    query = """
    MATCH (:Keyword {word: {keyword}})-[:Contains]-(document:Document) 
    RETURN document.identifier AS identifier
    """
    returned_nodes = []
    for node in graph.run(query, keyword = keyword):
        returned_nodes.append(node.get('identifier'))
    return returned_nodes

def get_weight_document_to_author(document, author):
    doc = graph.nodes.match("Document", identifier = document).first()
    auth = graph.nodes.match("Author", name = author).first()
    if doc is None or auth is None:
        weight = 0
    else:
        info = list(graph.relationships.match((doc, auth), "Commented"))
        if not info:
            weight = 0
        else:
            weight = info[0]['weight']
    return weight

def get_weight_author_to_author(author1, author2):
    auth1 = graph.nodes.match("Author", name = author1).first()
    auth2 = graph.nodes.match("Author", name = author2).first()
    if auth1 is None or auth2 is None:
        weight = 0
    else:
        info = list(graph.relationships.match((auth1, auth2), "Interacted"))
        if not info:
            weight = 0
        else:
            weight = info[0]['weight']
    return weight

