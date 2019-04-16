# Import Dependencies 
from flask import Flask, render_template, redirect, jsonify
from flask_pymongo import PyMongo
import pymongo
import scrape_mars
import os

# Create an instance of Flask app
app = Flask(__name__)

client = pymongo.MongoClient()
db = client.mars_db
collection = db.mars_facts
# Use flask_pymongo to set up mongo connection locally 
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")

# Create route that renders index.html template and finds documents from mongo
@app.route("/")
def home(): 

    # Find data
    mars_info = list(db.mars_facts.find())
    print(mars_info)

    # Return template and data
    return render_template("index.html", mars_info=mars_info)

# Route that will trigger scrape function
@app.route("/scrape")
def scrape(): 

    # Run scrapped functions
    mars_info = scrape_mars.scrape()
    print('\n')
    db.mars_facts.insert_one(mars_info)

    return redirect("/")

if __name__ == "__main__": 
    app.run(debug= True)