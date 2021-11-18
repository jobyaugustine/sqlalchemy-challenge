import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
#Passenger = Base.classes.passenger
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    #"""List all available api routes."""
    return (
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>Precipation Data<br/><br/>"
        f"/api/v1.0/stations<br/>List of Weather Stations<br/><br/>"
        f"/api/v1.0/startdate<br/>Min, Max and Avg Temperature Observations for dates from  the given date<br/><br/>"
        f"/api/v1.0/startdate/enddate<br/>Min, Max and Avg Temperature Observations Between two given dates <br/><br/>"
    )
#Measurement =station,date,prcp,tobs
#Station= station,name,latitude,longitude,elevation

#`/api/v1.0/precipitation`

#Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# # Return the JSON representation of your dictionary.
@app.route('/api/v1.0/precipitation')

def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all 
    results = session.query(Measurement.station, Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_precip = []
    for station, date, prcp in results:
        prcp_dict = {}
        prcp_dict["prcp"] = prcp
        prcp_dict["date"] = date
        
        all_precip.append(prcp_dict)

    return jsonify(all_precip)

#`/api/v1.0/stations`
@app.route('/api/v1.0/stations')
#Return a JSON list of stations from the dataset.

def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all 
    results = session.query(Station.station, Station.name).all()

    session.close()

    all_station = []
    for station, name in results:
        stn_dict = {}
        stn_dict["station"] = station
        stn_dict["name"] = name
        
        all_station.append(stn_dict)

    return jsonify(all_station)


#`/api/v1.0/tobs`
#Query the dates and temperature observations of the most active station for the last year of data.

#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date_fmt = dt.datetime.strptime(recent_date[0], "%Y-%m-%d")
    recent_date_fmt=recent_date_fmt.date()

# Subtract 12 months from current date
    n = 12
    past_date = recent_date_fmt - pd.DateOffset(months=n)
    date_format = '%Y-%m-%d'
    past_date_str = past_date.strftime(date_format)


    date_precip=session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date>=past_date_str).all()
    temp_list=[]
    for date,tobs in date_precip:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        
        temp_list.append(temp_dict)
    session.close()
    return jsonify(temp_list)
    

# `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

# Return a JSON list of the minimum temperature, 
# the average temperature, and the max temperature for a given start or start-end range.

@app.route('/api/v1.0/<start>')

def startdate(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #start_fmt = dt.datetime.strptime(start, "%Y-%m-%d")
   
    # Query all 
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).order_by(Measurement.date).all()

    session.close()


    startlist = []
    for date, min, max,avg in results:
        startlist_dict = {}
        startlist_dict["date"] = date
        startlist_dict["MinTemp"] = min
        startlist_dict["MaxTemp"] = max
        startlist_dict["AvgTemp"] = avg
        
        
        startlist.append(startlist_dict)

    return jsonify(startlist)


@app.route('/api/v1.0/<start>/<end>')

def startenddate(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start_fmt = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end_fmt= dt.datetime.strptime(end, "%Y-%m-%d").date()
    # Query all 
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start_fmt and Measurement.date <= end_fmt).all()

    session.close()

    startendlist = []
    for date, min, max,avg in results:
        startendlist_dict = {}
        startendlist_dict["date"] = date
        startendlist_dict["MinTemp"] = min
        startendlist_dict["MaxTemp"] = max
        startendlist_dict["AvgTemp"] = avg
        
        
        startendlist.append(startendlist_dict)

    return jsonify(startendlist)


if __name__ == '__main__':
    app.run(debug=True)
