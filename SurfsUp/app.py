# Import the dependencies.
import numpy as np
import datetime as dt
import flask 
print(flask.__version__)
import sqlalchemy
print(sqlalchemy.__version__)
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


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

#################################################
# Flask Routes
#################################################

# Homepage
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


# Precipitaion analysis
@app.route("/api/v1.0/precipitation")
def prcp():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365) 
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= previous_year).all()

    session.close()

    precipitation = {date:prcp for date,prcp in results}
    return jsonify(precipitation)


# All the stations
@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    stations = session.query(station.station).all()

    session.close()

    all_stations = list(np.ravel(stations))
    return jsonify(all_stations)


# Date and temeratures of 'USC00519281' during the last 12 months
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperatures = session.query(measurement.date, measurement.tobs).filter(measurement.date >= previous_year).filter(measurement.station == 'USC00519281').all()

    session.close()

    temperatures_list = list(np.ravel(temperatures))
    return jsonify(temperatures_list)


# Specified temperature for a start or start and end range
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def start(start=None, end=None):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)]
    
    if not end:
        start = dt.datetime.strptime(start,"%m%d%Y")

        temperatures = session.query(*sel).filter(measurement.date >= start).all()

        session.close()

        temperatures_list = list(np.ravel(temperatures))
        return jsonify(temperatures_list)
    
    start = dt.datetime.strptime(start,"%m%d%Y")
    end = dt.datetime.strptime(end,"%m%d%Y")

    temperatures = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()

    session.close()

    temperatures_list = list(np.ravel(temperatures))
    return jsonify(temperatures_list)


if __name__ == '__main__':
    app.run(debug=True)