# This file is contains print comments. Simply uncomment the lines and view the terminal to see output.

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import urllib2
from tethys_sdk.gizmos import TimeSeries
import xml.etree.ElementTree as et
from tethys_sdk.gizmos import DatePicker
from tethys_sdk.gizmos import Button
import csv
from django.http import HttpResponse

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

    url = 'http://water.weather.gov/ahps2/hydrograph_to_xml.php?gage={0}&output=xml'.format(gaugeID.lower())
    # print url

    response = urllib2.urlopen(url)
    data = response.read()
    # print data

    display_data = []  #Creates an empty list to contain data for later display
    value = float()
    total = float()
    site = et.fromstring(data)
    # print site.tag

    # The following sections parse returned XML data to find observed and forecast information for display.
    # The XML data can be viewed by uncommenting the print url line and copying the url into a browser.
    for child in site:
        if child.tag == "observed":
            observed = child  # This is to add clarity in the next loop
            for datum in observed:
                # print datum[0].text
                # print datum[2].tag
                # print datum[2].text
                for field in datum:
                    # print field
                    # print field.tag, 'tag'
                    # print field.attrib, 'attrib'
                    # print field.text, 'text'
                    # print field.keys()
                    # print field.get('name')
                    if field.get('name') == "Flow":
                        if field.get('units') == "kcfs":
                            value = float(field.text)*1000
                            # print value
                            total += value
                        if field.get('units') =="cfs":
                            value = float(field.text)
                            total += value
                        # print field.text, '******'
                    if field.get('timezone') == "UTC":
                        time = field.text
                        time1 = time.replace("T","-")
                        time_split = time1.split("-")
                        year = int(time_split[0])
                        month = int(time_split[1])
                        day = int(time_split[2])
                        hour_minute = time_split[3].split(":")
                        hour = int(hour_minute[0])
                        minute = int(hour_minute[1])
                display_data.append([datetime(year, month, day, hour, minute), value])
        if child.tag == "forecast":
            forecast = child
            for datum in forecast:
                for field in datum:
                    if field.get('name') == "Flow":
                        if field.get('units') == "kcfs":
                            value = float(field.text)*1000
                            # print value

                        if field.get('units') =="cfs":
                            value = float(field.text)
                        # print field.text, '******'

                    if field.get('timezone') == "UTC":
                        time = field.text
                        time1 = time.replace("T","-")
                        time_split = time1.split("-")
                        year = int(time_split[0])
                        month = int(time_split[1])
                        day = int(time_split[2])
                        hour_minute = time_split[3].split(":")
                        hour = int(hour_minute[0])
                        minute = int(hour_minute[1])

                display_data.append([datetime(year, month, day, hour, minute), value])

        display_data.sort()  # Due to XML formatting the sheet must be sorted to place forecasts after observations

    gotdata = False
    if total > 0:
        gotdata = True

    timeseries_plot = TimeSeries(
            height='500px',
            width='500px',
            engine='highcharts',
            title='Streamflow Plot',
            y_axis_title='Flow',
            y_axis_units='cfs',
            series=[{
                'name': 'Streamflow',
                'data': display_data
            }]
    )
        # print child.tag, child.attrib
    print '**********************************************************'

    observed_stage_data = []
    value_stage = float()
    total_stage = float()
    site = et.fromstring(data)
    for child in site:
        if child.tag == "observed":
            observed = child #This is to add clarity in the next loop
            for datum in observed:
                for field in datum:
                    if field.get('name') == "Stage":
                        if field.get('units') =="ft":
                            value_stage = float(field.text)
                            total_stage += value_stage

                    if field.get('timezone') == "UTC":
                        time = field.text
                        time1 = time.replace("T","-")
                        time_split = time1.split("-")
                        year = int(time_split[0])
                        month = int(time_split[1])
                        day = int(time_split[2])
                        hour_minute = time_split[3].split(":")
                        hour = int(hour_minute[0])
                        minute = int(hour_minute[1])

                observed_stage_data.append([datetime(year, month, day, hour, minute), value_stage])

    gotdata_stage = False
    if total_stage > 0:
        gotdata_stage = True

    timeseries_plot_stage = TimeSeries(
            height='500px',
            width='500px',
            engine='highcharts',
            title='Stage Plot',
            y_axis_title='Stage',
            y_axis_units='ft',
            series=[{
                'name': 'Streamflow',
                'data': observed_stage_data
            }]
    )

    context = {"gaugeno": gaugeID, "waterbody": waterbody, "timeseries_plot": timeseries_plot, "gotdata": gotdata, "timeseries_plot_stage": timeseries_plot_stage, "gotdata_stage": gotdata_stage}

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

    try:
        request.GET['start']
    except:
        gaugeID = request.POST['gaugeid']
        waterbody = request.POST['waterbody']
        date_start = request.POST['date_start']
        date_end = request.POST['date_end']
    else:
        gaugeID = request.GET['gaugeid']
        waterbody = request.GET['waterbody']
        date_start = request.GET['start']
        date_end = request.GET['end']

    print date_start
    print date_end
    print '********************************************************'

    # if request.GET['start']:
    #     date_start = request.GET['start']
    # else:
    #     date_start = request.POST['date_start']
    #
    # if request.GET['end']:
    #     date_end = request.GET['end']
    # else:
    #     date_end = request.POST['date_end']
    #
    # date_start = request.POST['date_start']
    # date_end = request.POST['date_end']

    t_now = datetime.now()
    now_str = "{0}-{1}-{2}".format(t_now.year,check_digit(t_now.month),check_digit(t_now.day))
    two_weeks = timedelta(days=14)
    t_2_weeks_ago = t_now - two_weeks
    two_weeks_ago_str = "{0}-{1}-{2}".format(t_2_weeks_ago.year,check_digit(t_2_weeks_ago.month),check_digit(t_2_weeks_ago.day))

    # url = 'http://waterdata.usgs.gov/nwis/uv?cb_00060=on&format=rdb&site_no={0}&period=&begin_date={1}&end_date={2}'.format(gaugeID, two_weeks_ago_str, now_str)

    url = 'http://nwis.waterdata.usgs.gov/usa/nwis/uv/?cb_00060=on&format=rdb&site_no={0}&period=&begin_date={1}&end_date={2}'.format(gaugeID, two_weeks_ago_str, now_str)
    # if date_start <> "yyyy-mm-dd":
    #     url = 'http://nwis.waterdata.usgs.gov/usa/nwis/uv/?cb_00060=on&format=rdb&site_no={0}&period=&begin_date={1}&end_date={2}'.format(gaugeID, date_start, date_end)

    # print url

    response = urllib2.urlopen(url)
    data = response.read()
    # print data

    time_series_list = []
    for line in data.splitlines():
        if line.startswith("USGS"):
            data_array = line.split('\t')
            time_str = data_array[2]
            value_str = data_array[4]
            if value_str == "Ice":
                value_str = "0"
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

    # print time_series_list
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

    date_picker1 = DatePicker(name='date_start',
                             display_text='Start Date',
                             autoclose=True,
                             format='yyyy-mm-dd',
                             # start_date='2015-12-01',
                             start_view='month',
                             today_button=True,
                             # initial= t_2_weeks_ago.strftime('%Y-%m-%d'))
                             initial= two_weeks_ago_str)

    date_picker2 = DatePicker(name='date_end',
                             display_text='End Date',
                             autoclose=True,
                             format='yyyy-mm-dd',
                             # start_date='2016-02-01',
                             start_view='month',
                             today_button=True,
                             # initial=t_now.strftime('%Y-%m-%d'))
                             initial= now_str)

    single_button = Button(display_text='Generate New Graph',
                           name='Generate New Graph',
                           attributes={""},
                           submit=True)

    context = {"gaugeid": gaugeID, "waterbody": waterbody, "timeseries_plot": timeseries_plot, "gotdata": gotdata, "date_picker1": date_picker1, "date_picker2": date_picker2, "single_button": single_button, "date_start": date_start, "date_end": date_end}

    return render(request, 'gaugeviewer/usgs.html', context)


# def usgs1(request):
#     """
#     Controller for the app home page.
#     """
#     gaugeID = 10163000
#     date_start = request.POST['date_start']
#     date_end = request.POST['date_end']
#
#     url_dl = 'http://nwis.waterdata.usgs.gov/usa/nwis/uv/?cb_00060=on&format=rdb&site_no={0}&period=&begin_date={1}&end_date={2}'.format(gaugeID, date_start, date_end)
#     # print url_dl
#
#     response = urllib2.urlopen(url_dl)
#     data = response.read()
#     # print data
#
#     time_series_list = []
#     for line in data.splitlines():
#         if line.startswith("USGS"):
#             data_array = line.split('\t')
#             time_str = data_array[2]
#             value_str = data_array[4]
#             if value_str == "Ice":
#                 value_str = "0"
#             time_str = time_str.replace(" ","-")
#             time_str_array = time_str.split("-")
#             year = int(time_str_array[0])
#             month = int(time_str_array[1])
#             day = int(time_str_array[2])
#             hour, minute = time_str_array[3].split(":")
#             hourInt = int(hour)
#             minuteInt = int(minute)
#             time_series_list.append([datetime(year, month, day, hourInt, minuteInt), float(value_str)])
#
#     # print time_series_list
#
#     gotdata = False
#     if len(time_series_list) > 0:
#         gotdata = True
#
#     print time_series_list
#     timeseries_plot = TimeSeries(
#         height='500px',
#         width='500px',
#         engine='highcharts',
#         title='Streamflow Plot',
#         y_axis_title='Flow',
#         y_axis_units='cfs',
#         series=[{
#             'name': 'Streamflow',
#             'data': time_series_list
#         }]
#     )
#
#     date_picker1 = DatePicker(name='date_start',
#                               display_text='Start Date',
#                               autoclose=True,
#                               format='yyyy-mm-dd',
#                               start_date='2/15/2014',
#                               start_view='month',
#                               today_button=True,
#                               initial='yyyy-mm-dd')
#
#     date_picker2 = DatePicker(name='date_end',
#                               display_text='End Date',
#                               autoclose=True,
#                               format='yyyy-mm-dd',
#                               start_date='2/15/2014',
#                               start_view='month',
#                               today_button=True,
#                               initial='yyyy-mm-dd')
#
#     single_button = Button(display_text='Generate New Graph',
#                            name='Generate New Graph',
#                            attributes={""},
#                            submit=True)
#
#
#
#     context = {"gaugeid": gaugeID, "date_start": date_start, "date_end": date_end, "time_series_list": time_series_list, "timeseries_plot": timeseries_plot, "gotdata": gotdata, "date_picker1": date_picker1, "date_picker2": date_picker2, "single_button": single_button}
#
#     return render(request, 'gaugeviewer/usgs1.html', context)