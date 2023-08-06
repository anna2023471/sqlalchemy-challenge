from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
import numpy as np

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save classes
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create date variable to retrieve last 12 months of data
year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

# Create selection variable to use in temp calculations
sel_temp = [
      func.min(Measurement.tobs),
      func.avg(Measurement.tobs),
      func.max(Measurement.tobs)]

# Create selection variable to use in station query
sel_station = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]

# Create app
app = Flask(__name__)

# Create homepage route and list available routes
@app.route("/")
def home():
    return (f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>"
        f"---use date format YYYY-MM-DD<br>"
        f"/api/v1.0/<start>/<end><br>"
        f"---use date format YYYY-MM-DD")

# Create static precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Retrieve precipitation data for last 12 months
    session = Session(engine)
    rain_query_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    session.close()

    # Create dictionary with date as key and precipitation as values, and append all values to list of obervations
    precipitation_data = []
    for date, prcp in rain_query_data:
        precipitation_dict = {date: prcp}
        precipitation_data.append(precipitation_dict)

    # Jsonify the output
    return jsonify(precipitation_data)

# Create static station route
@app.route("/api/v1.0/stations")
def station():

    # Retrieve station data
    session = Session(engine)
    station_query = session.query(*sel_station).filter(Measurement.station == Station.station).distinct().all()
    session.close()

    # Create dictionary with station ID as key and station details as values, and append all values to list of station records
    station_data = []
    for station, name, latitude, longitude, elevation in station_query:
        station_dict = {station: [name, latitude, longitude, elevation]}
        station_data.append(station_dict)

    # Jsonify output
    return jsonify(station_data)

# Create static temperature route
@app.route("/api/v1.0/tobs")
def tobs():

    # Retrieve last 12 months worth of data for most active station
    session = Session(engine)
    year_station_data = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= year_ago).all()
    session.close()

    # Create dictionary with date and temp as values, and append all values to list of obervations
    tobs_data = []
    for date, tobs in year_station_data:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["tobs"] = tobs
        tobs_data.append(tobs_dict)

    # Jsonify output
    return jsonify(tobs_data)

# Create dynamic start date route
@app.route("/api/v1.0/<start>")
def start_date(start):
    
    # Perform selected calculations on all data from the specified start date to end of dataset
    session = Session(engine)  
    start_date_data = session.query(*sel_temp).filter(Measurement.date >= start).all()
    session.close()
    
    # Convert query results to a list
    start_date_results = list(np.ravel(start_date_data))
    
    # Jsonify output
    return jsonify(start_date_results)

# Create dynamic start and end date route
@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):

    # Perform selected calculations on all data from the specified start date to the specified end date
    session = Session(engine)    
    date_range_data = session.query(*sel_temp).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    # Convert query results to a list
    date_range_results = list(np.ravel(date_range_data))

    # Jsonify output
    return jsonify(date_range_results)

# Run app
if __name__ == "__main__":
    app.run(debug=True)