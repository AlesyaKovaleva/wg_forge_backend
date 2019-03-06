import sys
from collections import Counter
from statistics import mean, median

from sqlalchemy.exc import SQLAlchemyError

from cats_sqlalhemy import CatColor, CatColorsInfo, Cats, CatsStat, db_session
from helpers import moda


def main():
    try:
        with db_session() as session:
            data = session.query(Cats)
            colors = [cat.color for cat in data]
            tails = [cat.tail_length for cat in data]
            whiskers = [cat.whiskers_length for cat in data]

            count_colors = dict(Counter(colors))

            for color, count in count_colors.items():
                entry = session.query(CatColorsInfo).get(color)
                if entry:
                    entry.count = count
                else:
                    entry = CatColorsInfo(color, count)
                    session.add(entry)

            if tails and whiskers:

                DATA_FOR_CATS_STAT = {
                    "tail_length_mean": round(mean(tails), 2),
                    "tail_length_median": round(median(tails), 2),
                    "tail_length_mode": tuple(moda(tails)),
                    "whiskers_length_mean": round(mean(whiskers), 2),
                    "whiskers_length_median": round(median(whiskers), 2),
                    "whiskers_length_mode": tuple(moda(whiskers)),
                }

                stats = CatsStat(*DATA_FOR_CATS_STAT.values())
                session.add(stats)
    except SQLAlchemyError as err:
        sys.stderr.write("ERROR: " + str(err))


if __name__ == "__main__":
    main()
