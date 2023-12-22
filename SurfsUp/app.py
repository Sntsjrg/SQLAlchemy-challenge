from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# Create Flask app
app = Flask(__name__)

# Create SQLite engine and reflect the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)


# Create references to the necessary tables
measure = Base.classes.measurement
station = Base.classes.station

# Create session
session = Session(engine)

# Define routes

@app.route("/")
def home():
    """Homepage with a list of available routes."""
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary and return JSON."""
    # Calculate the date one year ago from the last date in the dataset
    one_year_ago = dt.datetime.strptime('2017-08-23', '%Y-%m-%d').date() - dt.timedelta(days=365)

    # Query to retrieve the last 12 months of precipitation data
    results = session.query(measure.date, measure.prcp).filter(measure.date >= one_year_ago).all()

    # Convert the results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in results}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    # Query to retrieve a list of stations
    results = session.query(station.station).all()

    # Convert the results to a list
    station_list = [result[0] for result in results]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the previous year of data."""
    # Assuming most_active_station_id is the ID of the most active station obtained from the previous query
    most_active_station_id = "USC00519281"

    # Calculate the date one year ago from the last date in the dataset
    one_year_ago = dt.datetime.strptime('2017-08-23', '%Y-%m-%d').date() - dt.timedelta(days=365)

    # Query to retrieve temperature observations for the most active station in the last 12 months
    results = (
        session.query(measure.date, measure.tobs)
        .filter(measure.station == most_active_station_id)
        .filter(measure.date >= one_year_ago)
        .all()
    )

    # Convert the results to a list of dictionaries
    tobs_list = [{"Date": date, "Temperature": tobs} for date, tobs in results]

    return jsonify(tobs_list)
        
@app.route("/api/v1.0/temp_stats/<start_date>")
def temperature_stats_start(start_date):
    """Return min, max, and average temperatures from the start date to the end of the dataset."""
    # Query to retrieve temperature statistics for the specified date range
    results = (
        session.query(
            func.min(measure.tobs).label('min_temp'),
            func.max(measure.tobs).label('max_temp'),
            func.avg(measure.tobs).label('avg_temp')
        )
        .filter(measure.date >= start_date)
        .first()
    )

    # Check if there is any result
    if results:
        # Create a dictionary with the temperature statistics
        temperature_stats = {
            'min_temp': results.min_temp,
            'max_temp': results.max_temp,
            'avg_temp': results.avg_temp
        }
        return jsonify(temperature_stats)
    else:
        return jsonify({'error': 'No data available for the specified date range'}), 404

@app.route("/api/v1.0/temp_stats/<start_date>/<end_date>")
def temperature_stats_range(start_date, end_date):
    """Return min, max, and average temperatures for the specified date range."""
    # Query to retrieve temperature statistics for the specified date range
    results = (
        session.query(
            func.min(measure.tobs).label('min_temp'),
            func.max(measure.tobs).label('max_temp'),
            func.avg(measure.tobs).label('avg_temp')
        )
        .filter(measure.date >= start_date, measure.date <= end_date)
        .first()
    )

    # Check if there is any result
    if results:
        # Create a dictionary with the temperature statistics
        temperature_stats = {
            'min_temp': results.min_temp,
            'max_temp': results.max_temp,
            'avg_temp': results.avg_temp
        }
        return jsonify(temperature_stats)
    else:
        return jsonify({'error': 'No data available for the specified date range'}), 404
        
if __name__ == "__main__":
    app.run(debug=True)
