#!/usr/bin/env python
from contextlib import asynccontextmanager
import logging
import os
from typing import Optional

from fastapi import FastAPI
from neo4j import (
    basic_auth,
    AsyncGraphDatabase,
)
from starlette.responses import FileResponse


PATH = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

url = os.getenv("NEO4J_URI", "neo4j+s://demo.neo4jlabs.com")
username = os.getenv("NEO4J_USER", "movies")
password = os.getenv("NEO4J_PASSWORD", "movies")
neo4j_version = os.getenv("NEO4J_VERSION", "4")
database = os.getenv("NEO4J_DATABASE", "movies")

port = os.getenv("PORT", 8080)

driver = AsyncGraphDatabase.driver(url, auth=basic_auth(username, password))


@asynccontextmanager
async def get_db():
    if neo4j_version.startswith("4"):
        async with driver.session(database=database) as session_:
            yield session_
    else:
        async with driver.session() as session_:
            yield session_


@app.get("/")
async def get_index():
    return FileResponse(os.path.join(PATH, "static", "index.html"))


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


@app.get("/graph")
async def get_graph(limit: int = 100):
    async def work(tx):
        result = await tx.run(
            "MATCH (m:Movie)<-[:ACTED_IN]-(a:Person) "
            "RETURN m.title AS movie, collect(a.name) AS cast "
            "LIMIT $limit",
            {"limit": limit}
        )
        return [record_ async for record_ in result]

    async with get_db() as db:
        results = await db.read_transaction(work)
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
        return {"nodes": nodes, "links": rels}


@app.get("/search")
async def get_search(q: Optional[str] = None):
    async def work(tx, q_):
        result = await tx.run(
            "MATCH (movie:Movie) "
            "WHERE toLower(movie.title) CONTAINS toLower($title) "
            "RETURN movie", {"title": q_}
        )
        return [record async for record in result]

    if q is None:
        return []
    async with get_db() as db:
        results = await db.read_transaction(work, q)
        return [serialize_movie(record["movie"]) for record in results]


@app.get("/movie/{title}")
async def get_movie(title: str):
    async def work(tx):
        result_ = await tx.run(
            "MATCH (movie:Movie {title:$title}) "
            "OPTIONAL MATCH (movie)<-[r]-(person:Person) "
            "RETURN movie.title as title,"
            "COLLECT([person.name, "
            "HEAD(SPLIT(TOLOWER(TYPE(r)), '_')), r.roles]) AS cast "
            "LIMIT 1",
            {"title": title}
        )
        return await result_.single()

    async with get_db() as db:
        result = await db.read_transaction(work)

        return {"title": result["title"],
                "cast": [serialize_cast(member)
                         for member in result["cast"]]}


@app.post("/movie/{title}/vote")
async def vote_in_movie(title: str):
    async def work(tx):
        result = await tx.run(
            "MATCH (m:Movie {title: $title}) "
            "SET m.votes = coalesce(m.votes, 0) + 1;",
            {"title": title})
        return await result.consume()

    async with get_db() as db:
        summary = await db.write_transaction(work)
        updates = summary.counters.properties_set

        return {"updates": updates}


if __name__ == "__main__":
    import uvicorn

    logging.root.setLevel(logging.INFO)
    logging.info("Starting on port %d, database is at %s", port, url)

    uvicorn.run(app, port=port)
