# Import the dependencies.

from flask import Flask, jsonify
import pandas as pd
import datetime as dt 
import numpy as  np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,desc,inspect


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)
Base

#inspection = inspect(engine)
#inspection.get_table_names()
Base.classes.keys()

# Save references to each table
Measure = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


for table_name in Base.classes.keys():
      table = Base.classes[table_name]
      print(table_name)
      for column in table.__table__.columns:
          print(f"\t{column.name} - {column.type}")

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


@app.route("/")
def home():
    return (
        f"Welcome to the CLIMATE  API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )


#################################################
# Flask Routes
 # Precipitacion

@app.route("/api/v1.0/precipitation")
def precipitacion():
    session = Session(engine)
    max_date = session.query(func.max(Measure.date)).scalar()
    print(max_date)
    year_2016 = (pd.to_datetime(max_date) - pd.offsets.Day(365)).strftime("%Y-%m-%d")
    data_year = (
    session
    .query(Measure.date,Measure.prcp)
    .filter(Measure.date>=year_2016)
    .all()
    )
    session.close()
    preci_data= {date: prcp for date,prcp in data_year }

    return jsonify(preci_data)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    meas_stat = (
    session.query(Measure.station, func.count(Measure.station).label("count"))
    .group_by(Measure.station)
    .order_by(desc("count"))  
    .all()
    )
    session.close()
    stati_date = list(np.ravel(meas_stat))
    
    return (stati_date)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    max_date = session.query(func.max(Measure.date)).scalar()
    year_2016 = (pd.to_datetime(max_date) - pd.offsets.Day(365)).strftime("%Y-%m-%d")
    data_year = (
    session
    .query(Measure.date,Measure.tobs)
    .filter(Measure.date>=year_2016)
    .filter(Measure.station=='USC00519281')
    .all()
    )
    session.close()
    
    tobs_results  = [{"date": date, "tobs": tobs} for date, tobs in data_year]    
    return jsonify(tobs_results)
    
 


if __name__ == '__main__':
    app.run(debug=True)

