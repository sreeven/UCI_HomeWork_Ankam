# Import Dependencies

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Set Base

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Base Keys

MA = Base.classes.measurement
ST = Base.classes.station


# Flask

from flask import Flask, jsonify

app = Flask(__name__)

# Routes

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature for last year: /api/v1.0/tobs<br/>"
        f"Temperature stats from start date: /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stats from start to end dates: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<end><br/>"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    sel = [MA.date, MA.prcp]
    result = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in result:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [ST.station, ST.name, ST.latitude, ST.longitude, ST.elevation]
    result = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = session.query(MA.date).order_by(MA.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    query_date = dt.date(last_date.year -1, last_date.month, last_date.day)
    sel = [MA.date,MA.tobs]
    result = session.query(*sel).filter(MA.date >= query_date).all()
    session.close()

    all_tobs = []
    for date, tobs in result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    result = session.query(func.min(MA.tobs), func.avg(MA.tobs), func.max(MA.tobs)).\
        filter(MA.date >= start).all()
    session.close()

    all_tobs = []
    for min,avg,max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>/<stop>")
def start_stop(start,stop):
    session = Session(engine)
    result = session.query(func.min(MA.tobs), func.avg(MA.tobs), func.max(MA.tobs)).\
        filter(MA.date >= start).filter(MA.date <= stop).all()
    session.close()

    all_tobs = []
    for min,avg,max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


if __name__ == "__main__":
    app.run(debug=True)