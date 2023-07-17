from flask import Flask, jsonify 
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import csv
from os import path
from tensorflow.keras import models
import numpy
from numpy import array
import json
import random
from flask_sqlalchemy import SQLAlchemy
from flask.templating import render_template

app = Flask(__name__)
api = Api(app)
fileName="fsr-data-{}.csv"

Label_dict = {0: "No Slouch", 1: "Upper Back Slouch", 2: "Lower Back Slouch", 3: "Right Slouch", 4:"Left Slouch"}

curPos = -1
curVal = '0,0,0,0'


pp = 0
p = 0


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)


class ValueDb(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fsr1 = db.Column(db.Integer, unique=False, nullable=False)
    fsr2 = db.Column(db.Integer, unique=False, nullable=False)
    fsr3 = db.Column(db.Integer, unique=False, nullable=False)
    fsr5 = db.Column(db.Integer, unique=False, nullable=False)
    pred = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return "{self.fsr1}\t{self.fsr2}\t{self.fsr3}\t{self.fsr5}\t{pred}"



# Import for Migrations
from flask_migrate import Migrate, migrate
 
# Settings for migrations
migrate = Migrate(app, db)

def getString(dict):
    stri=''
    for i in [1,2,3]:
        stri+=dict["FSR"+str(i)]+","
    stri+=dict["FSR5"]
    return stri


class Data(Resource):
    def get(self):
        label = 0

        parser = reqparse.RequestParser()
        parser.add_argument('FSR1', required = True)
        parser.add_argument('FSR2', required = True)
        parser.add_argument('FSR3', required = True)
        parser.add_argument('FSR4', required = True)
        parser.add_argument('FSR5', required = True)
        parser.add_argument('FSR6', required = True)

        args = parser.parse_args()
        args["FSR4"], args["FSR6"] = 0, 0
        # 1>TR YO, 2>ML GB, 3> MR WP, 4>BL RB, 5>TL RB 6> BR WB

        #Labels 0>No slouch, 1>up slouch, 2>down slouhc, 3>right slouch, 4> left slouch
        if not path.exists(fileName.format(label)):
            with open(fileName.format(label), "w") as f:
                f.write("Sensor1,Sensor2,Sensor3,Sensor4,Sensor5,Sensor6,Label\n")

        with open(fileName.format(label), "a") as f:
            if int(args["FSR1"]) < 10 and int(args["FSR2"]) < 10 and int(args["FSR3"]) < 10 and int(args["FSR4"]) < 300 and int(args["FSR5"]) <10 and int(args["FSR6"]) < 300:
                pass
            else:
                f.write(args["FSR1"]+","+args["FSR2"]+","+args["FSR3"]+","+args["FSR4"]+","+args["FSR5"]+","+args["FSR6"]+"," +str(label) +"\n")


        print(args['FSR1'], args['FSR2'], args['FSR3'], args['FSR4'], args['FSR5'], args['FSR6'])
        return {'result': "OK"}, 200


class Predict(Resource):
    def get(self):
        global curPos, curVal
        global p
        global pp

        parser = reqparse.RequestParser()
        parser.add_argument('FSR1', required = True)
        parser.add_argument('FSR2', required = True)
        parser.add_argument('FSR3', required = True)
        #parser.add_argument('FSR4', required = True)
        parser.add_argument('FSR5', required = True)
        #parser.add_argument('FSR6', required = True)

        args = parser.parse_args()
        if int(args["FSR1"]) < 10 and int(args["FSR2"]) < 10 and int(args["FSR3"]) < 10 and int(args["FSR5"]) <10:
            curVal = '0,0,0,0'
            curPos = -1
        else:
            print(args["FSR1"]+","+args["FSR2"]+","+args["FSR3"]+","+args["FSR5"]+"\n")
            vals = array([[int(x) for x in args.values()]])

            model = models.load_model('model-5')

            preds = model.predict(vals)

            pred = preds.argmax()
            print(Label_dict[pred], type(json.dumps(args)))

            curPos = pred
            curVal = getString(args)
            print(vals)
            #pp = p
            #p = pred
            db_obj = ValueDb(fsr1 =vals[0][0], fsr2= vals[0][1], fsr3= vals[0][2], fsr5= vals[0][3], pred = pred)
            db.session.add(db_obj)
            db.session.commit()

            return {"prediction": str(pred)}, 200

class AppData(Resource):
    def get(self):
        vals = curVal.split(',')
        val = str(vals[3])+","+str(vals[0])+","+str(vals[1])+","+str(vals[2])
        return {"data": val, "prediction": str(curPos)}, 200
        #TR BL BR TL

class Try(Resource):
    def get(self):
        return {"prediction": str(curPos)}, 200

class Random(Resource):
    def get(self):
        val = random.randint(1,1000)
        r = ValueDb(value = val)
        db.session.add(r)
        db.session.commit()
        return val

@app.route('/')
def index():
    val = ValueDb.query.all()
    return render_template('index.html')


@app.route('/getdb')
def getdb():
    #val = ValueDb.query.all()
    return jsonify({'data': '111,11,111,111,111,111', 'prediction': '2'})
    return jsonify({'result': 'success ', 'id': random.randint(1,1000)})




class HistoryData(Resource):
    def get(self):
        preds = []
        for data in db.engine.execute('select * from value_db order by id desc limit 40;'):
            preds.append(int.from_bytes(data["fsr1"], "little"))
        properSlouch = round((preds.count(0)/40) * 100)
        return {"proper": properSlouch, "slouch": 100 - properSlouch}

class ChartData(Resource):
    def get(self):
        preds = []
        val = ValueDb.query.all()
        for v in val:
            preds.append(int.from_bytes(v.pred, "little"))
        properSlouch = preds.count(0)
        return {"proper": properSlouch, "slouch": len(preds)-properSlouch}
        



        


#api.add_resource(Data, '/sensors')  # add endpoints
api.add_resource(ChartData, '/chartData')
api.add_resource(HistoryData, '/historyData')
api.add_resource(Predict, '/sensors')
api.add_resource(AppData, '/chairData')
api.add_resource(Try,'/tryPos')
api.add_resource(Random, '/randomTry')

if __name__ == '__main__':
    app.run(debug = True)  # run our Flask app