# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def routes():
    return(f"Welcome to the Climate Homepage!!<br/>"
           f"Available Routes:<br/>" 
           f"/api/v1.0/precipitation<br/>" 
           f"/api/v1.0/stations<br/>" 
           f"/api/v1.0/tobs<br/>" 
           f"/api/v1.0/<start><br/>" 
           f"/api/v1.0/<start>/<end>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    date_last = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= (last_year)).order_by(measurement.date.desc())
    
    precipitation_dict = {}
    for i, x in data:
        precipitation_dict[i] = x
        session.close()
    return(jsonify(precipitation_dict))

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.stations).all()
    station = list(results)
    session.close()
    return(jsonify(station))

@app.route("/api/v1.0/tobs")
def tabs():
    session = Session(engine)
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    station_yearlast = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281', measurement.date >= last_year).all()
    station = list(station_yearlast)
    session.close()
    return(jsonify(np.ravel(stations)))

@app.route("/api/v1.0/<start>")
def start():
    session = Session(engine)
    summary_stats = [func.min(measurement.tobs), 
                     func.max(measurement.tobs), 
                     func.avg(measurement.tobs)]
    date_stats = session.query(*summary_stats).filter(measurement.date >= '2016-08-23').all()
    session.close()
    return(jsonify(list(np.ravel(date_stats))))

@app.route("/api/v1.0/<start>/<end>")
def start_end():
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d")
    summary_stats = [func.min(measurement.tobs), 
                     func.max(measurement.tobs), 
                     func.avg(measurement.tobs)]
    daterange_stats = session.query(*summary_stats).filter(measurement.date >= start).filter(measurement.date <= end).all()
    return(jsonify(list(np.ravel(daterange_stats))))

if __name__ == '__main__':
    app.run(debug=True)