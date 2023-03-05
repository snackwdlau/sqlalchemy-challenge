#################################################
# Imports 
#################################################
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify, request

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

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# #################################################
# Datas
# #################################################
session = Session(engine)

# Calculate the most recent date in the data set. 
recent_date = session.query(measurement.date).\
    order_by(measurement.date.desc()).first()
    
# Calculate the date one year from the last date in data set. 
year = dt.timedelta(days=365)
last_yr = dt.date(2017, 8, 23) - year 

# Create a query to retrieve the data & precipitation scores
prcp = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= last_yr).\
        order_by(measurement.date).all()
        
# Create a query to retrieve the station name & station
station = session.query(station.name, station.station).all()

# Create a query to retrieve the most active station
active = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()
    
# Create a query to retrieve the dates & temperatures observations for the most active station
temp = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date >= last_yr).\
        filter(measurement.station == 'USC00519281').all()
        
# Create a query to retrieve the dates
dates = session.query(measurement.date).all()

session.close

# #################################################
# # Flask Routes - HOME
# #################################################
@app.route("/")
def home():
    return(
    f"Welcome to the Climate Analysis API! <br/>"
    f"Available Routes:<br/>"
    f"Precipitation ----> /api/v1.0/precipitations <br/>"
    f"Station -----------> /api/v1.0/stations <br/>"
    f"Tobs -------------> /api/v1.0/tobs <br/>"
    f"Dates ------------> /api/v1.0/dates <br/>"
    f"Start -------------> /api/v1.0/dates/<start> <br/>"
    f"Start/End -------> /api/v1.0/dates/<start>/<end> <br/>"
    )
# #################################################
# # Flask Routes - PRECIPITATION
# #################################################
@app.route('/api/v1.0/precipitations')
def get_precipitation():
    return jsonify([p._asdict() for p in prcp])

# #################################################
# # Flask Routes - STATION
# #################################################
@app.route('/api/v1.0/stations')
def get_station():
    return jsonify([s._asdict() for s in station])

# #################################################
# # Flask Routes - TOBS
# #################################################
@app.route('/api/v1.0/tobs')
def get_tobs():
    return jsonify([t._asdict() for t in temp])

# #################################################
# # Flask Routes - DATES
# #################################################
@app.route('/api/v1.0/dates')
def get_dates():
    return jsonify([d._asdict() for d in dates])

# #################################################
# # Flask Routes - START
# #################################################
@app.route("/api/v1.0/dates/<start>")
def get_start(start):
    session = Session(engine)
    calc = session.query(measurement.station, measurement.date,
                     func.min(measurement.tobs),
                     func.max(measurement.tobs),
                     func.avg(measurement.tobs)).\
                        filter(measurement.date >= start).all()
    dict = []
    for row in calc:
        column = {}
        column["date"] = start
        column["min"] = row[2]
        column["max"] = row[3]
        column["avg"] = round(row[4], 1)
        dict.append(column)
    session.close()
    return jsonify(dict)

# #################################################
# # Flask Routes - START/END
# #################################################
@app.route("/api/v1.0/dates/<start>/<end>")
def get_end(start, end):
    # def date(start="YYYY-MM-DD"):
    session = Session(engine)
    calc = session.query(measurement.station, measurement.date,
                     func.min(measurement.tobs),
                     func.max(measurement.tobs),
                     func.avg(measurement.tobs).\
                        filter(measurement.date >= start).\
                        filter(measurement.date <= end)).all()
    dict = []
    for row in calc:
        column = {}
        column["date"] = start
        column["end date"] = end 
        column["min"] = row[2]
        column["max"] = row[3]
        column["avg"] = round(row[4], 1)
        dict.append(column)
    session.close()
    return jsonify(dict)

if __name__ == "__main__":
    app.run(debug=True)