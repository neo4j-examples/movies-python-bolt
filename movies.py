#!/usr/bin/env python
from json import dumps
import logging
import os

from flask import (
    Flask,
    g,
    request,
    Response,
)
from neo4j import (
    GraphDatabase,
    basic_auth,
)


app = Flask(__name__, static_url_path="/static/")

url = os.getenv("NEO4J_URI", "neo4j+s://demo.neo4jlabs.com")
username = os.getenv("NEO4J_USER", "movies")
password = os.getenv("NEO4J_PASSWORD", "movies")
neo4j_version = os.getenv("NEO4J_VERSION", "4")
database = os.getenv("NEO4J_DATABASE", "movies")

port = os.getenv("PORT", 8080)

driver = GraphDatabase.driver(url, auth=basic_auth(username, password))


def get_db():
    if not hasattr(g, "neo4j_db"):
        if neo4j_version.startswith("4"):
            g.neo4j_db = driver.session(database=database)
        else:
            g.neo4j_db = driver.session()
    return g.neo4j_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "neo4j_db"):
        g.neo4j_db.close()


@app.route("/")
def get_index():
    return app.send_static_file("index.html")


def serialize_movie(movie):
    return {
        "id": movie["id"],
        "title": movie["title"],
        "summary": movie["summary"],
        "released": movie["released"],
        "duration": movie["duration"],
        "rated": movie["rated"],
        "tagline": movie["tagline"],
        "votes": movie.get("votes", 0)
    }


def serialize_cast(cast):
    return {
        "name": cast[0],
        "job": cast[1],
        "role": cast[2]
    }


@app.route("/graph")
def get_graph():
    def work(tx, limit):
        return list(tx.run(
            "MATCH (m:Movie)<-[:ACTED_IN]-(a:Person) "
            "RETURN m.title AS movie, collect(a.name) AS cast "
            "LIMIT $limit",
            {"limit": limit}
        ))

    db = get_db()
    results = db.read_transaction(work, request.args.get("limit", 100))
    nodes = []
    rels = []
    i = 0
    for record in results:
        nodes.append({"title": record["movie"], "label": "movie"})
        target = i
        i += 1
        for name in record["cast"]:
            actor = {"title": name, "label": "actor"}
            try:
                source = nodes.index(actor)
            except ValueError:
                nodes.append(actor)
                source = i
                i += 1
            rels.append({"source": source, "target": target})
    return Response(dumps({"nodes": nodes, "links": rels}),
                    mimetype="application/json")


@app.route("/search")
def get_search():
    def work(tx, q_):
        return list(tx.run(
            "MATCH (movie:Movie) "
            "WHERE toLower(movie.title) CONTAINS toLower($title) "
            "RETURN movie",
            {"title": q_}
        ))

    try:
        q = request.args["q"]
    except KeyError:
        return []
    else:
        db = get_db()
        results = db.read_transaction(work, q)
        return Response(
            dumps([serialize_movie(record["movie"]) for record in results]),
            mimetype="application/json"
        )


@app.route("/movie/<title>")
def get_movie(title):
    def work(tx, title_):
        return tx.run(
            "MATCH (movie:Movie {title:$title}) "
            "OPTIONAL MATCH (movie)<-[r]-(person:Person) "
            "RETURN movie.title as title,"
            "COLLECT([person.name, "
            "HEAD(SPLIT(TOLOWER(TYPE(r)), '_')), r.roles]) AS cast "
            "LIMIT 1",
            {"title": title_}
        ).single()

    db = get_db()
    result = db.read_transaction(work, title)

    return Response(dumps({"title": result["title"],
                           "cast": [serialize_cast(member)
                                    for member in result["cast"]]}),
                    mimetype="application/json")


@app.route("/movie/<title>/vote", methods=["POST"])
def vote_in_movie(title):
    def work(tx, title_):
        return tx.run(
            "MATCH (m:Movie {title: $title}) "
            "SET m.votes = coalesce(m.votes, 0) + 1;",
            {"title": title_}
        ).consume()

    db = get_db()
    summary = db.write_transaction(work, title)
    updates = summary.counters.properties_set

    db.close()

    return Response(dumps({"updates": updates}), mimetype="application/json")


if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    logging.info("Starting on port %d, database is at %s", port, url)
    app.run(port=port)
