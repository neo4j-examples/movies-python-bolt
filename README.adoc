== Neo4j Movies Application: Quick Start

image:https://github.com/neo4j-examples/movies-python-bolt/actions/workflows/python-app.yml/badge.svg?branch=main[alt="CI", link="https://github.com/neo4j-examples/movies-python-bolt/actions/workflows/python-app.yml"]
image:https://github.com/neo4j-examples/movies-python-bolt/actions/workflows/python-async-app.yml/badge.svg?branch=main[alt="CI", link="https://github.com/neo4j-examples/movies-python-bolt/actions/workflows/python-async-app.yml"]

image::http://dev.assets.neo4j.com.s3.amazonaws.com/wp-content/uploads/movie_application.png[float=right,width=400]

This example application demonstrates how easy it is to get started with http://neo4j.com/developer[Neo4j] in Python.

It is a very simple web application that uses our Movie graph dataset to provide a search with listing, a detail view and a graph visualization.

We offer two different ways to run the application: synchronous and asynchronous (using `asyncio`).

=== The Stack

These are the components of our Web Application:

* Application Type:         Python-Web Application
* Web framework:
  - sync: https://palletsprojects.com/p/flask/[Flask] (Micro-Webframework)
  - async: https://fastapi.tiangolo.com/[FastAPI] (Micro-Webframework)
* Neo4j Database Connector: https://github.com/neo4j/neo4j-python-driver[Neo4j Python Driver] for Cypher https://neo4j.com/developer/python[Docs]
* Database:                 Neo4j-Server (4.x) with multi-database
* Frontend:                 jquery, bootstrap, https://d3js.org/[d3.js]

Provision a database quickly with https://sandbox.neo4j.com/?usecase=movies[Neo4j Sandbox] or https://neo4j.com/cloud/aura/[Neo4j Aura].

=== Setup

Install Python 3.6-3.9 (sync) or 3.7-3.10 (async).

Then get yourself set up with link:http://docs.python-guide.org/en/latest/dev/virtualenvs/[virtualenv] so we don't break any other Python stuff you have on your machine. After you've got that installed let's set up an environment for our app:

[source]
----
virtualenv neo4j-movies
source neo4j-movies/bin/activate
----

The next step is to install the dependencies for the app with pip (or pip3 for python3):

sync:

[source]
----
pip install -r requirements.txt
----

async:

[source]
----
pip install -r requirements-async.txt
----

=== Run locally

And finally let's start up a web server:

sync:

[source]
----
python movies.py
# or python3 movies.py

Running on http://127.0.0.1:8080/
----

async:

[source]
----
python movies-async.py
# or python3 movies-async.py

Running on http://127.0.0.1:8080/
----

Navigate to http://localhost:8080 and you should see your first Neo4j application


=== Changing the Database
By default, this example application connects to a remote Neo4j database run by
Neo4j for this purpose. If you want to connect to a local database, follow these
instructions.

Start your local Neo4j Server (http://neo4j.com/download[Download & Install]),
open the http://localhost:7474[Neo4j Browser]. Then install the Movies data set
with `:play movies`, click the `CREATE` statement (in some versions, this will not
be directly on the first page of the movies example), and hit the triangular
"Run" button.

If you haven't touched the configuration of your Neo4j Server, the database will
be reachable at `neo4j://localhost:7687`.

Use environment variables to let the application know where to connect to the
database.

sync:

[source]
----
NEO4J_URI=neo4j://localhost:7687 NEO4J_DATABASE=neo4j NEO4J_USER="<username>" NEO4J_PASSWORD="<password>" python movies.py

Running on http://127.0.0.1:8080/
----

async:

[source]
----
NEO4J_URI=neo4j://localhost:7687 NEO4J_DATABASE=neo4j NEO4J_USER="<username>" NEO4J_PASSWORD="<password>" python movies-async.py

Running on http://127.0.0.1:8080/
----


=== All Configuration Options

Here are all environment variables that can be used to configure the
application.

[%header,cols=2*]
|===
|Environment Variable Name
|Default Value (or N/A)

|PORT
|8080

|NEO4J_URI
|neo4j+s://demo.neo4jlabs.com

|NEO4J_USER
|movies

|NEO4J_PASSWORD
|movies

|NEO4J_DATABASE
|movies
|===
