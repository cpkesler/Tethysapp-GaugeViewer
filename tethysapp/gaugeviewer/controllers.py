from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import urllib2
from tethys_sdk.gizmos import TimeSeries
import webbrowser



@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    context = {}

    return render(request, 'gaugeviewer/home.html', context)

def ahps(request):
    """
    Controller for the app ahps page.
    """
    gaugeID = request.GET['gaugeno']
    waterbody = request.GET['waterbody']


    url = 'http://water.weather.gov/resources/hydrographs/{0}_hg.png'.format(gaugeID.lower())


    context = {"gauge_figure": url, "gaugeno": gaugeID, "waterbody": waterbody}

    return render(request, 'gaugeviewer/ahps.html', context)

def check_digit(num):
    num_str = str(num)
    if len(num_str) < 2:
        num_str = '0' + num_str
    return num_str

def usgs(request):
    """
    Controller for the app usgs page.
    """
    gaugeID = request.GET['gaugeid']
    waterbody = request.GET['waterbody']
    t_now = datetime.now()
    now_str = "{0}-{1}-{2}".format(t_now.year,check_digit(t_now.month),check_digit(t_now.day))
    two_weeks = timedelta(days=14)
    t_2_weeks_ago = t_now - two_weeks
    two_weeks_ago_str = "{0}-{1}-{2}".format(t_2_weeks_ago.year,check_digit(t_2_weeks_ago.month),check_digit(t_2_weeks_ago.day))



    url = 'http://waterdata.usgs.gov/nwis/uv?cb_00060=on&format=rdb&site_no={0}&period=&begin_date={1}&end_date={2}'.format(gaugeID, two_weeks_ago_str, now_str)

    print url
    response = urllib2.urlopen(url)
    data = response.read()
    print data
    time_series_list = []
    for line in data.splitlines():
        if line.startswith("USGS"):
            data_array = line.split('\t')
            time_str = data_array[2]
            value_str = data_array[4]
            time_str = time_str.replace(" ","-")
            time_str_array = time_str.split("-")
            year = int(time_str_array[0])
            month = int(time_str_array[1])
            day = int(time_str_array[2])
            hour, minute = time_str_array[3].split(":")
            hourInt = int(hour)
            minuteInt = int(minute)

            time_series_list.append([datetime(year, month, day, hourInt, minuteInt), float(value_str)])

    gotdata = False
    if len(time_series_list) > 0:
        gotdata = True

    print time_series_list
    timeseries_plot = TimeSeries(
        height='500px',
        width='500px',
        engine='highcharts',
        title='Streamflow Plot',
        y_axis_title='Flow',
        y_axis_units='cfs',
        series=[{
            'name': 'Streamflow',
            'data': time_series_list
        }]
    )

    context = {"gaugeid": gaugeID, "waterbody": waterbody, "timeseries_plot": timeseries_plot, "gotdata": gotdata}

    return render(request, 'gaugeviewer/usgs.html', context)