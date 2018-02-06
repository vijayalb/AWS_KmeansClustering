import csv
import uuid
from flask import Flask, render_template, request
import numpy as np
import pylab
from numpy import array
from scipy.cluster.vq import *

application = Flask(__name__, template_folder='static')


col_names = ["time","latitude","longitude","depth","mag","magType","nst","gap","dmin","rms","net","id","updated","place","type","horizontalError","depthError","magError","magNst"]
myfile = open("quakes.csv","r")
csv_reader = csv.DictReader(myfile, fieldnames=col_names)
csv_reader.__next__()
mylist = []


def getdata(attr1,attr2):
    c = 0
    for row in csv_reader:
        c += 1
        if c == 5000:
            break
        pair = []
        if row[attr1] == "":
            row[attr1] = 0
        if row[attr2] == "":
            row[attr2] = 0
        x = float(row[attr1])
        y = float(row[attr2])
        pair.append(x)
        pair.append(y)
        mylist.append(pair)
    return mylist


@application.route('/', methods=['POST', 'GET'])
def run():
    return render_template("index.html")


@application.route('/show', methods=['POST', 'GET'])
def show():
    return render_template("result.html")


@application.route('/execute', methods=['POST', 'GET'])
def main():
    distance = []
    point = []
    attr1 = str(request.form['attribute1'])
    attr2 = str(request.form['attribute2'])
    no_cluster = request.form['clusters']
    k = int(no_cluster)
    mylist = getdata(attr1,attr2)
    data = array(mylist)
    res, idx = kmeans2(data,k)
    for i in range(len(res)):
        x1 = res[i][0]
        y1 = res[i][1]
        x1 = float("{0:.3f}".format(x1))
        y1 = float("{0:.3f}".format(y1))
        for j in range(i+1,len(res)):
            x2 = res[j][0]
            y2 = res[j][1]
            x2 = float("{0:.3f}".format(x2))
            y2 = float("{0:.3f}".format(y2))
            dist = np.sqrt((x1-x2)**2 + (y1-y2)**2)
            distance.append(dist)
    clr = ([1, 1, 0.0],[0.2,1,0.2],[1,0.2,0.2],[0.3,0.3,1],[0.0,1.0,1.0],)
    colors = ([(clr)[i] for i in idx])
    clr_dict = {"yellow":0,"green":0,"red":0,"blue":0,"cyan":0}
    for x in colors:
        if str(x) == "[1, 1, 0.0]":
            clr_dict["yellow"] += 1
        if str(x) == "[0.2, 1, 0.2]":
            clr_dict["green"] += 1
        if str(x) == "[1, 0.2, 0.2]":
            clr_dict["red"] += 1
        if str(x) == "[0.3, 0.3, 1]":
            clr_dict["blue"] += 1
        if str(x) == "[0, 1.0, 1.0]":
            clr_dict["cyan"] += 1
    for i in clr_dict:
        if clr_dict[i] == 0:
            continue
        point.append(str(clr_dict[i]))
    pylab.scatter(data[:,0],data[:,1], c=colors)
    pylab.scatter(res[:,0],res[:,1], marker='o', s = 400, linewidths=3, c='none')
    pylab.scatter(res[:,0],res[:,1], marker='x', s = 400, linewidths=3)
    fname = uuid.uuid4()
    filename = str(fname) +".png"
    pylab.savefig('static/kmeans.png')
    return render_template("index.html", distances = distance, points = point)


if __name__ == "__main__":
    application.run(debug=True)
