from flask import Flask, request, render_template

import json
from globals import MyGlobals
import Pico
import HotTank, MashTank, BoilTank
import Regulation
import time
import argparse

import Queue
import pprint


app = Flask(__name__)
pico = Pico.Pico()

@app.route("/")
def main():
    return render_template('main.html')


@app.route("/temperature/<tank>.json")
def temperature(tank):
    history = []
    data = {}
    #history.append( ["16:00","16:05","16:10","16:15","16:20","16:25"])
    if (tank == "hot"):
        data["value"]   = pico.hottank.last_value
        history.append( pico.hottank.timing.array)
        history.append(pico.hottank.temperatures.array)
    elif (tank == "mash"):
        data["value"]   = pico.mashtank.last_value
        history.append( pico.mashtank.timing.array)
        history.append(pico.mashtank.temperatures.array)
    else:
        data["value"]   = pico.boiltank.last_value
        history.append( pico.boiltank.timing.array)
        history.append(pico.boiltank.temperatures.array)

    data["history"] = history

    return json.dumps(data)


@app.route("/volume.json")
def volume():

    data = {}
    data["label"] = pico.hottank.timing.array
    data["hot"]   = [50,45,42,44,48,50]
    data["mash"]  = [20, 25, 30, 30, 30, 30, 30]
    data["boil"]  = [0, 0, 7, 12, 20, 20, 20]

    return json.dumps(data)

@app.route("/power.json")
def power():
    data = {}
    data["label"] = ["16:00","16:05","16:10","16:15","16:20","16:25"]
    data["hot"]   = [1100, 1200, 1300, 1640, 1480, 1400, 1520]
    data["mash"]  = [600,520,550,480,450,500]
    data["boil"]  = [600, 400, 1000, 600, 500, 900, 800]

    return json.dumps(data)


@app.route("/task.json")
def task():
    data = {}
    data["task"] = []
    data["task"].append ({
     "task name": "Fill in malt for Dark IPA",
     "status": "done"
     })

    data["task"].append ({
     "task name": "Fill in malt for bitter",
     "status": "waiting"
    })
    data["task"].append ({
     "task name": "Dump Dark IPA",
     "status": "unavailable"
    })
    data["task"].append ({
     "task name": "Fill in malt for Stout",
     "status": "unavalaible"
    })

    return json.dumps(data)

@app.route("/add/recipe")
def add_recipe():

    if (request.args.get('url') is None):
        return json.dumps({ "error": error }), 500

    url = request.args.get('url')
    recipe = pico.fetch_recipe(url)
    pico.add_recipe(recipe)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/recipe.json")
def recipe():
    data = {}
    data["recipes"] = []
    data["recipes"].append({
    "recipe_name" : "Dark IPA",
    "step"        : "Boil",
    "time"        : "25m 10s",
    "status"      : "active"
    })

    data["recipes"].append({
    "recipe_name" : "Bitter",
    "step"        : "Mash",
    "time"        : "15m 56s",
    "status"      : "active"
    })

    data["recipes"].append({
    "recipe_name" : "Stout",
    "step"        : "",
    "time"        : "",
    "status"      : "pending"
    })

    return json.dumps(data)


@app.route("/valve.json")
def valve():
    data = {}
    data["switchs"] = []

    data["switchs"].append({
    "name"   :"valve-hot",
    "checked":pico.regule.lld.valve_setting["Hot"]
    })
    data["switchs"].append({
    "name"   :"valve-mash",
    "checked":pico.regule.lld.valve_setting["Mash"]
    })
    data["switchs"].append({
    "name"   :"valve-boil",
    "checked":pico.regule.lld.valve_setting["Boil"]
    })

    return json.dumps(data)


@app.route("/lock.json")
def lock():
    data = pico.regule.lld.lock
    return json.dumps(data)

@app.route("/lock")
def set_lock():
    error = False

    if (request.args.get('valve') is not None):
        pico.regule.lld.lock["valve"] = not pico.regule.lld.lock["valve"]

    if (request.args.get('resistor') is not None):
        pico.regule.lld.lock["resistor"] = not pico.regule.lld.lock["resistor"]

    if (request.args.get('pump') is not None):
        pico.regule.lld.lock["pump"] = not pico.regule.lld.lock["pump"]

    if error is True:
        return json.dumps({ "error": error }), 500
    else:
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route("/resistor.json", methods=['GET'])
def resistor_get():
    data = {}
    data["switchs"] = []

    data["switchs"].append({
    "name"   :"resistor-hot",
    "checked": pico.regule.lld.setting["Hot"]
    })
    data["switchs"].append({
    "name"   :"resistor-mash",
    "checked":pico.regule.lld.setting["Mash"]
    })
    data["switchs"].append({
    "name"   :"resistor-boil",
    "checked":pico.regule.lld.setting["Boil"]
    })

    return json.dumps(data)

@app.route("/switch")
def switch():

    error = False
    if (request.args.get('resistor-hot') is not None):
        pico.regule.lld.resistor_switch( pico.hottank, True if (request.args.get('resistor-hot') == 'True') else False)

    elif (request.args.get('resistor-mash') is not None):
        pico.regule.lld.resistor_switch( pico.mashtank, True if (request.args.get('resistor-mash') == 'True') else False)

    elif (request.args.get('resistor-boil') is not None):
        pico.regule.lld.resistor_switch( pico.boiltank, True if (request.args.get('resistor-boil') == 'True') else False)

    elif (request.args.get('valve-hot') is not None):
        pico.regule.lld.valve_switch( pico.hottank, True if (request.args.get('valve-hot') == 'True') else False)

    elif (request.args.get('valve-mash') is not None):
        pico.regule.lld.valve_switch( pico.mashtank, True if (request.args.get('valve-mash') == 'True') else False)

    elif (request.args.get('valve-boil') is not None):
        pico.regule.lld.valve_switch( pico.boiltank, True if (request.args.get('valve-boil') == 'True') else False)

    elif (request.args.get('pump') is not None):
        pico.regule.lld.pump_switch( True if (request.args.get('pump') == 'True') else False)
        #pico.regule.lld.pump_switch( False )

    if error is True:
        return json.dumps({ "error": error }), 500
    else:
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/pump.json")
def pump():
    data = {}
    data["switchs"] = []

    data["switchs"].append({
    "name"   :"pump",
    "checked":pico.regule.lld.pump_setting
    })

    return json.dumps(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Brewery software for a 3 tanks RIMS setup')
    parser.add_argument('--hardware_disconnected', action='store_false', help='set this switch if you have no arduino wired')
    MyGlobals.args = vars(parser.parse_args())

    hot = HotTank.HotTank(saturation=50, period=1)

    start_boil_queue      = Queue.Queue()
    start_heat_queue      = Queue.Queue()

    start_counting_queue = Queue.Queue()
    need_cleaning_queue  = Queue.Queue()

    boil = BoilTank.BoilTank(start_heat_queue, start_boil_queue, start_counting_queue, need_cleaning_queue)

    start_mash_queue    = Queue.Queue()
    need_cleaning_queue = Queue.Queue()

    mash = MashTank.MashTank(hot, boil, start_mash_queue, need_cleaning_queue)

    regule = Regulation.Regulation(hot, mash, boil)
    pico.real_init(hot, mash, boil, regule)
    app.run()
