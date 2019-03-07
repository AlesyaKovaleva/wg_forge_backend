import json
import sys

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext import baked

from cats_schema import CATS_SCHEMA
from cats_sqlalhemy import Cats, db_session
from helpers import validate_cats_params


def ping(*args):
    return (200, "Cats Service. Version 0.1", {"Content-type": "text/html"})


def cats(data, session):

    if data:
        try:
            attr, order, offset, limit = validate_cats_params(data)
            if order and not attr:
                raise ValueError
        except ValueError:
            return (
                400,
                {"status": "Bad request.", "exception": ""},
                {"Content-type": "application/json"},
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

    return (200, cats_list, {"Content-type": "application/json"})


def post_cats(data: bytes, session):
    try:
        cats = json.loads(data)
        validate(cats, CATS_SCHEMA)
    except json.JSONDecodeError as err:
        return (
            400,
            {"status": "Invalid JSON.", "exception": err.msg},
            {"Content-type": "application/json"},
        )
    except ValidationError as err:
        return (
            400,
            {"status": "Bad request.", "exception": err.message},
            {"Content-type": "application/json"},
        )

    cats_names = [name[0] for name in session.query(Cats.name)]
    if cats["name"].title() in cats_names:
        return (
            400,
            {
                "status": "Bad request.",
                "exception": "%s is already in the database" % cats["name"],
            },
            {"Content-type": "application/json"},
        )
    session.add(
        Cats(
            name=cats["name"].title(),
            color=cats["color"],
            tail_length=cats["tail_length"],
            whiskers_length=cats["whiskers_length"],
        )
    )
    return (201, "Cat added successfully", {"Content-type": "text/html"})
