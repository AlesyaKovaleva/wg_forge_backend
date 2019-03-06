import enum
from contextlib import contextmanager

from sqlalchemy import (
    ARRAY,
    Column,
    Enum,
    Integer,
    Numeric,
    String,
    create_engine,
    inspect,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER


DB_PATH = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


@contextmanager
def db_session():
    """Provide a transactional scope around a series of operations."""
    try:
        engine = create_engine(DB_PATH)
        Session = sessionmaker(bind=engine)
        session = Session()

        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


Base = declarative_base()


class CatColor(enum.Enum):
    black = "black"
    white = "white"
    black_white = "black & white"
    red = "red"
    red_white = "red & white"
    red_black_white = "red & black & white"


class Cats(Base):
    __tablename__ = "cats"
    name = Column("name", String, primary_key=True)
    color = Column("color", String, Enum(CatColor))
    tail_length = Column("tail_length", Integer)
    whiskers_length = Column("whiskers_length", Integer)

    def __init__(self, name, color, tail_length, whiskers_length):
        self.name = name
        self.color = color
        self.tail_length = tail_length
        self.whiskers_length = whiskers_length

    def __repr__(self):
        return "{}, {}, {}, {}".format(
            self.name, self.color, self.tail_length, self.whiskers_length
        )

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class CatColorsInfo(Base):
    __tablename__ = "cat_colors_info"

    color = Column("color", String, Enum(CatColor), unique=True)
    count = Column("count", Integer)

    __mapper_args__ = {"primary_key": [color]}

    def __init__(self, color, count):
        self.color = color
        self.count = count

    def __repr__(self):
        return "{}, {}".format(self.color, self.count)


class CatsStat(Base):
    __tablename__ = "cats_stat"
    tail_length_mean = Column("tail_length_mean", Numeric, primary_key=True)
    tail_length_median = Column("tail_length_median", Numeric, primary_key=True)
    tail_length_mode = Column(
        "tail_length_mode", ARRAY(Integer, as_tuple=True), primary_key=True
    )
    whiskers_length_mean = Column("whiskers_length_mean", Numeric, primary_key=True)
    whiskers_length_median = Column("whiskers_length_median", Numeric, primary_key=True)
    whiskers_length_mode = Column(
        "whiskers_length_mode", ARRAY(Integer, as_tuple=True), primary_key=True
    )

    def __init__(
        self,
        tail_length_mean,
        tail_length_median,
        tail_length_mode,
        whiskers_length_mean,
        whiskers_length_median,
        whiskers_length_mode,
    ):
        self.tail_length_mean = tail_length_mean
        self.tail_length_median = tail_length_median
        self.tail_length_mode = tail_length_mode
        self.whiskers_length_mean = whiskers_length_mean
        self.whiskers_length_median = whiskers_length_median
        self.whiskers_length_mode = whiskers_length_mode

    # __mapper_args__ = {
    #     "primary_key": [
    #         tail_length_mean,
    #         tail_length_median,
    #         tail_length_mode,
    #         whiskers_length_mean,
    #         whiskers_length_median,
    #         whiskers_length_mode,
    #     ]
    # }


# with db_session() as session:
#     cats = session.query(Cats)
# print(cats)

# colors = [cat.color for cat in cats]
# print(colors)

# colors_counts = session.query(CatColorsInfo)
# colors = [cat.count for cat in colors_counts]
# print(colors)

# with db_session() as session:
#     cats = session.query(Cats)
#     # session.add(Cats(name='QWERertttt', color='red', tail_length=122222, whiskers_length=8888888))
#     # session.commit()

#     for cat in cats:
#         print(cat.whiskers_length)

# for i in cats:
#     print(i.name, i.color, i.tail_length, i.whiskers_length)

# for name, fullname in session.query(User.name, User.fullname):
#     print(name, fullname)

# Cat = namedtuple("Cat", ["name", "color", "tail_length", "whiskers_length"])
# b = [[Cat(cat.name, cat.color, cat.tail_length, cat.whiskers_length)] for cat in cats]
# print(b)
# print(type(b[0][0]))
# x = [Cat(*x) for x in b]
# print(x)

# u = session.query(Cats)[0]
# print(u)

# e = session.query(func.count(Cats.name))
# print(e.all())

# w = session.query(func.count(distinct(Cats.name)))
# print(w.all())

# cat1 = Cat('Nina', 'black', 12, 12)
# print(cat1)
