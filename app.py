''' This script is used to retrieve stock prices for a specified time interval from
the Quandl API. This script has been developed by Sina Bahrami as part of the preliminiary
preparation course for the Data Incubator Fall 2019 cohort.'''


#The following modules and libraries are used:
from flask import Flask, render_template, request, redirect #to handle web app.
import requests # to extract information from the API.
import simplejson as json # for data extraction. 
from bokeh.plotting import figure #for plotting with bokeh
from bokeh.embed import components
import datetime #for date and time manipulation
import math


################### Required Functions ######################

#The function below connects to the Quandl API.
#The input consists of: stock ticker, begin date, end date, type of data requested. 
#Note: As of now (11-09-2019) the newest API data is from 03-27-2018.
#Available data types are:  open (1), high (2), low (3), close (4),
#adjusted open (8), adjusted high (9), adjusted low (10), adjusted close (11).
#The user can request multiple data types.
#The api access requires a key, and here I have provided my personal key. 
def getinfo(ticker, begin_date, end_date, index=['1'], key='WSq-U_khyspTZfx-yMgV'):
    
    index_dictionary={'1':[], '2':[], '3':[], '4':[], '8':[], '9':[], '10':[], '11':[]}
    
    for i in index:
      link="https://www.quandl.com/api/v3/datasets/WIKI/"+ticker+".json?column_index="+i+"&start_date="+begin_date+"&end_date="+end_date+"&api_key="+key
      download=requests.get(url=link)
      index_dictionary[i]=download.json()['dataset']['data']
    
    return index_dictionary
 
#Now generate a plot using Bokeh:
def plot_generator(x):

    non_empty_dict={}
    
    for item in x.items():
        if item[1]!=[]:
            z=zip(*item[1])
            l=list(z)
            non_empty_dict[item[0]]=[list(l[0])[::-1],list(l[1])[::-1]]

  #non-empty_dict is used to generate plots:
  #first collect the dates, as all plots have the same x-axis:
    dates=[]
    for x in non_empty_dict.values():
        dates+=x[0]
        break
      
  #now express dates in a nicer form using datetime functions:
    dates1=[datetime.datetime.strptime(d,'%Y-%m-%d') for d in dates]
  
  #now the plot:
    p=figure(plot_width=550, plot_height=450, title='Various Price Indicators For The Selected Equity', x_axis_type='datetime')
    for i in non_empty_dict.items():
        if i[0]=='1':
            p.line(dates1,i[1][1],line_width=1, color='navy',legend='open')
        elif i[0]=='2':
              p.line(dates1,i[1][1],line_width=1, color='blue',legend='high')
        elif i[0]=='3':
              p.line(dates1,i[1][1],line_width=1, color='brown',legend='low')
        elif i[0]=='4':
              p.line(dates1,i[1][1],line_width=1, color='orange',legend='close')
        elif i[0]=='8':
              p.line(dates1,i[1][1],line_width=1, color='gray',legend='adj. open')
        elif i[0]=='9':
              p.line(dates1,i[1][1],line_width=1, color='black',legend='adj. high')
        elif i[0]=='10':
              p.line(dates1,i[1][1],line_width=1, color='purple',legend='adj. low')
        elif i[0]=='11':
              p.line(dates1,i[1][1],line_width=1, color='violet',legend='adj. close')  
    
    
    p.legend.location="top_left"
    p.xaxis.major_label_orientation = math.pi/3
    
    script, div= components(p)
    return script, div
    
################### Flask Codes ######################  
  
app = Flask(__name__)

app.vars={}

@app.route('/')
def main():
	return redirect('/index')

@app.route('/index', methods=['GET','POST'])
def index():
	return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
  ticker=request.form.get('ticker')
  bd=request.form.get('begin_date')
  ed=request.form.get('end_date')
  items=request.form.getlist('features')
    
  app.vars['ticker']=ticker
  app.vars['begin_date']=bd
  app.vars['end_date']=ed
  app.vars['features']=items
  
  data1=getinfo(app.vars['ticker'],app.vars['begin_date'],app.vars['end_date'],app.vars['features'])
    
  script, div= plot_generator(data1)
  

  return render_template('plot.html', script=script, div=div)


if __name__ == '__main__':
  app.run(port=33507)