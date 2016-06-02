# This file is contains print comments. Simply uncomment the lines and view the terminal to see output.

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import urllib2
from tethys_sdk.gizmos import TimeSeries
import xml.etree.ElementTree as et
from tethys_sdk.gizmos import DatePicker
from tethys_sdk.gizmos import Button
from tethys_sdk.gizmos import TextInput
from tethys_sdk.gizmos import SelectInput

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
    # print '**********************************************************'

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
                'name': 'Stage',
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
    # gaugeID = request.GET['gaugeid']
    # waterbody = request.GET['waterbody']

    start = request.GET.get("start", None)
    comid = None
    forecast_range = None
    forecast_date = None

    if start is None:
        gaugeID = request.GET['gaugeid']
        waterbody = request.GET['waterbody']
        date_start = request.GET['date_start']
        date_end = request.GET['date_end']
        forecast_range = request.GET['forecast_range']
        comid = request.GET['comid']
        forecast_date = request.GET['forecast_date']
        comid_time = request.GET['comid_time']

    else:
        gaugeID = request.GET['gaugeid']
        waterbody = request.GET['waterbody']
        date_start = request.GET['start']
        date_end = request.GET['end']
        # forecast_range = request.GET['forecast_range']
        # comid = request.GET['comid']
        # forecast_date = request.GET['forecast_date']

    # print forecast_range, '888888888888888888888888888888888888888'
    # # print comid, '333333333333333333333333333333333'
    # print forecast_date , '111111111111111111111111111111111'

    # forecast_range = 'medium'
    # comid = '10375794'
    # forecast_date = '2016-05-29'


    # if request.POST:
    #     comid = request.POST['comid']
    #     forecast_date = request.POST['forecast_date']

    # print date_start
    # print date_end
    # print '********************************************************'
    # print gaugeID

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


    url = 'http://nwis.waterdata.usgs.gov/usa/nwis/uv/?cb_00060=on&format=rdb&site_no={0}&period=&begin_date={1}&end_date={2}'.format(gaugeID, date_start, date_end)
    # if date_start <> "yyyy-mm-dd":
    #     url = 'http://nwis.waterdata.usgs.gov/usa/nwis/uv/?cb_00060=on&format=rdb&site_no={0}&period=&begin_date={1}&end_date={2}'.format(gaugeID, date_start, date_end)

    print url

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
            # print time_series_list, 'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii'

    gotdata = False
    if len(time_series_list) > 0:
        gotdata = True

    # url_api = urllib2.urlopen('https://appsdev.hydroshare.org/apps/nwm-forecasts/waterml/?config=medium_range&COMID=10375768&lon=-98&lat=38.5&date=2016-05-28&time=06&lag=t00z')
    time_series_list_api = []
    gotComid = False
    if comid is not None and len(comid) > 0:
        gotComid = True
        forecast_size = request.GET['forecast_range']
        comid_time = "06"
        if forecast_size == "short":
            comid_time = request.GET['comid_time']

        url_api = urllib2.urlopen('https://appsdev.hydroshare.org/apps/nwm-forecasts/waterml/?config={0}_range&COMID={1}&lon=-98&lat=38.5&date={2}&time={3}&lag=t00z'.format(forecast_range, comid, forecast_date, comid_time))
        data_api = url_api.read()
        print data_api

        x = data_api.split('dateTimeUTC=')
        x.pop(0)


        for elm in x:
            info = elm.split(' ')
            time1 = info[0].replace('T',' ')
            time2 = time1.replace('"','')
            time3 = time2[:-3]
            time4 = time3.split(' ')
            time5 = time4[0].split('-')
            timedate = time5
            year = int(timedate[0])
            month = int(timedate[1])
            day = int(timedate[2])
            timetime = time4[1]
            hour = timetime[0]
            minute = timetime[1]
            hourInt = int(hour)
            minuteInt = int(minute)
            value = info[7].split('<')
            value1 = value[0].replace('>','')
            value2 = float(value1)
            time_series_list_api.append([datetime(year, month, day, hourInt, minuteInt), value2])
            # print time_series_list_api, 'pppppppppppppppppppppppppppppppppppppppppppp'
        print time_series_list_api

        # gotdata_api = False
        # if len(time_series_list_api) > 0:
        #     gotdata_api = True

    # def getNWMWaterML(config, ID, date_start):
    #     url_api = urllib2.urlopen('https://appsdev.hydroshare.org/apps/nwm-forecasts/waterml/?config=' + config + '_range&COMID=' + ID +
    #                           '&lon=-98&lat=38.5&date=' + date_start + '&time=06&lag=t00z')
    #     # url_api = urllib2.urlopen('https://appsdev.hydroshare.org/apps/nwm-forecasts/waterml/?config=medium_range&COMID=10376606&lon=-98&lat=38.5&date=2016-05-28&time=06&lag=t00z')
    #     # data = url_api.read()
    #
    #
    #     x = data.split('dateTimeUTC=')
    #     x.pop(0)
    #
    #     time_series_list_api = []
    #     for elm in x:
    #         info = elm.split(' ')
    #         time1 = info[0].replace('T',' ')
    #         time2 = time1.replace('"','')
    #         time = time2[:-3]
    #         val = info[7].split('<')
    #         value = val[0].replace('>','')
    #         time_series_list_api.append([time, value])
    #         print time_series_list_api, '000000000000000000000000000000'
    #
    #     return time_series_list_api
    #
    #
    # print getNWMWaterML('medium', '10376606', '2016-05-28')
    # time_series_api = getNWMWaterML('medium', '10376606', '2016-05-28')

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
            'data': time_series_list,
        }]
    )

    timeseries_plot_api = TimeSeries(
        height='500px',
        width='500px',
        engine='highcharts',
        title='Streamflow Forecast',
        y_axis_title='Streamflow',
        y_axis_units='cfs',
        series=[{
            'name': 'Streamflow',
            'data': time_series_list_api
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
                             initial= '2016-05-29')

    date_picker2 = DatePicker(name='date_end',
                             display_text='End Date',
                             autoclose=True,
                             format='yyyy-mm-dd',
                             # start_date='2016-02-01',
                             start_view='month',
                             today_button=True,
                             # initial=t_now.strftime('%Y-%m-%d'))
                             initial= now_str)

    single_button = Button(display_text='Generate New Graphs',
                           name='Generate New Graph',
                           attributes={""},
                           submit=True)

    text_input1 = TextInput(display_text='COMID',
                            name='comid',
                            initial='', )

    date_picker3 = DatePicker(name='forecast_date',
                              display_text='Forecast Date',
                              autoclose=True,
                              format='yyyy-mm-dd',
                              start_view='month',
                              today_button=True,
                              initial='2016-05-29')

    select_input = SelectInput(display_text='Forecast Size',
                                name='forecast_range',
                                multiple=False,
                                options=[('short', 'short'), ('medium', 'medium')],
                                initial=['short'],
                                original=['short'])

    select_input1 = SelectInput(display_text='Starting Time',
                                name='comid_time',
                                multiple=False,
                                options=[('12:00 am', "00"), ('1:00 am', "01"), ('2:00 am', "02"), ('3:00 am', "03"), ('4:00 am', "04"), ('5:00 am', "05"), ('6:00 am', "06"), ('7:00 am', "07"), ('7:00 am', "07"), ('8:00 am', "08"), ('9:00 am', "09"), ('10:00 am', "10"), ('11:00 am', "11"), ('12:00 pm', "12"), ('1:00 pm', "13"), ('2:00 pm', "14"), ('3:00 pm', "15"), ('4:00 pm', "16"), ('5:00 pm', "17"), ('6:00 pm', "18"), ('7:00 pm', "19"), ('8:00 pm', "20"), ('9:00 pm', "21"), ('10:00 pm', "22"), ('11:00 pm', "23")],
                                initial=['12'],
                                original=['12'])

    single_button1 = Button(display_text='Graph Forecast',
                           name='forecast',
                           attributes='form=forecast-form',
                           submit=True)

    context = {"gaugeid": gaugeID, "waterbody": waterbody, "text_input1": text_input1, "date_picker3": date_picker3, "select_input": select_input, "select_input1": select_input1, "forecast_range": forecast_range, "comid": comid, "forecast_date": forecast_date,   "sinlge_button1": single_button1, "timeseries_plot": timeseries_plot, "timeseries_plot_api": timeseries_plot_api, "gotdata": gotdata, "date_picker1": date_picker1, "date_picker2": date_picker2, "single_button": single_button, "date_start": date_start, "date_end": date_end, "gotComid": gotComid}

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

@login_required()
def python(request):
    """
    Controller for the app home page.
    """
    def getNWMWaterML(config, ID, date_start):
        url = urllib2.urlopen('https://appsdev.hydroshare.org/apps/nwm-forecasts/waterml/?config=' + config + '_range&COMID=' + ID +
                              '&lon=-98&lat=38.5&date=' + date_start + '&time=06&lag=t00z')
        data = url.read()


        x = data.split('dateTimeUTC=')
        x.pop(0)

        time_series_list = []
        max_value_list = []
        for elm in x:
            info = elm.split(' ')
            time = info[0].replace('T',' ')
            val = info[7].split('<')
            value = val[0].replace('>','')
            time_series_list.append([time, value])

        return time_series_list

    print getNWMWaterML('medium', '10376606', '2016-05-28')

    context = {}

    return render(request, 'gaugeviewer/python.html', context)

