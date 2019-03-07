import json
import sys
from collections import namedtuple

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext import baked

from cats_schema import CATS_SCHEMA
from cats_sqlalhemy import Cats, db_session
from helpers import validate_cats_params


Response = namedtuple("Response", "code content headers")


def ping(*args):
    return Response(
        code=200,
        content="Cats Service. Version 0.1",
        headers={"Content-type": "text/html"},
    )


def cats(data, session):

    if data:
        try:
            attr, order, offset, limit = validate_cats_params(data)
            if order and not attr:
                raise ValueError
        except ValueError as e:
            sys.stderr.write(str(e))
            return Response(
                code=400, content="Bad request", headers={"Content-type": "text/html"}
            )

        bakery = baked.bakery()
        cat = bakery(lambda session: session.query(Cats))

        if attr:
            sort_func = desc if order == "desc" else asc
            cat += lambda c: c.order_by(sort_func(getattr(Cats, attr)))

        if offset:
            cat += lambda c: c.offset(offset)
        if limit:
            cat += lambda c: c.limit(limit)

        cats = cat(session).all()
    else:
        cats = session.query(Cats)

    cats_list = []
    for i in cats:
        cats_list.extend([i.to_dict()])

    return Response(
        code=200,
        content=json.dumps(cats_list),
        headers={"Content-type": "application/json"},
    )


def post_cats(data: bytes, session):
    try:
        cats = json.loads(data)
        validate(cats, CATS_SCHEMA)
    except json.JSONDecodeError as err:
        return Response(
            code=400,
            content="Invalid JSON. %s" % err,  # !
            headers={"Content-type": "text/html"},
        )
    except ValidationError as err:
        return Response(
            code=400,
            content="Bad request. %s" % err.message,  # !
            headers={"Content-type": "text/html"},
        )

    cats_names = [name[0] for name in session.query(Cats.name)]
    if cats["name"].title() in cats_names:
        return Response(
            code=400,
            content="Bad request. %s is already in the database" % cats["name"],  # !
            headers={"Content-type": "text/html"},
        )
    session.add(
        Cats(
            name=cats["name"].title(),
            color=cats["color"],
            tail_length=cats["tail_length"],
            whiskers_length=cats["whiskers_length"],
        )
    )
    return Response(
        code=201,
        content="Cat added successfully",
        headers={"Content-type": "text/html"},
    )
