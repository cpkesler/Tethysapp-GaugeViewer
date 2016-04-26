//Here we are declaring the projection object for Web Mercator
var projection = ol.proj.get('EPSG:3857');

//Here we are declaring the raster layer as a separate object to put in the map later
var rasterLayer = new ol.layer.Tile({
    source: new ol.source.MapQuest({layer: 'sat'})
});

//var USGSGauges = new ol.Layer.WMS(
//    "OpenLayers WMS",
//    "http://igems.doi.gov/arcgis/services/igems_info/MapServer/WMSServer?request=GetCapabilities&service=WMS",
//    {isBaselayer: false}
//);

//Let's create another layer from a kml file. We'll call it "Border_States" but it could be called anything
//var Border_States = new ol.layer.Vector({
//    source: new ol.source.KML({
//        projection: projection,
//        //normally this kml file would be sitting on your server
//        url: '/static/the_underground/kml/Border_States.kml'
//    })
//});
//
//var Union_States = new ol.layer.Vector({
//    source: new ol.source.KML({
//        projection: projection,
//        //normally this kml file would be sitting on your server
//        url: '/static/the_underground/kml/Union_States.kml'
//    })
//});
//
//var Confederate_States = new ol.layer.Vector({
//    source: new ol.source.KML({
//        projection: projection,
//        url: '/static/the_underground/kml/Confederate_States.kml'
//    })
//});
//
//var P1820 = new ol.layer.Vector({
//    source: new ol.source.KML({
//        projection: projection,
//        url: '/static/the_underground/kml/1820.kml'
//    })
//});
//
//
//var P1830 = new ol.layer.Vector({
//    source: new ol.source.KML({
//        projection: projection,
//        url: '/static/the_underground/kml/1830.kml'
//    })
//});
//
//
//var P1840 = new ol.layer.Vector({
//    source: new ol.source.KML({
//        projection: projection,
//        url: '/static/the_underground/kml/1840.kml'
//    })
//});
//
//
//var P1850 = new ol.layer.Vector({
//    source: new ol.source.KML({
//        projection: projection,
//        url: '/static/the_underground/kml/1850.kml'
//    })
//});
//
//
//var P1860 = new ol.layer.Vector({
//    source: new ol.source.KML({
//        projection: projection,
//        url: '/static/the_underground/kml/1860.kml'
//    })
//});
//
//
//var P1870 = new ol.layer.Vector({
//    source: new ol.source.KML({
//        projection: projection,
//        url: '/static/the_underground/kml/1870.kml'
//    })
//});
//
//var P1880 = new ol.layer.Vector({
//    source: new ol.source.KML({
//        projection: projection,
//        url: '/static/the_underground/kml/1880.kml'
//    })
//});
//
//var LineData = new ol.layer.Vector({
//    source: new ol.source.KML({
//        projection: projection,
//        url: '/static/the_underground/kml/LineData.kml'
//    })
//});

//    layers = [rasterLayer,Border_States,Union_States,Confederate_States,P1820,P1830,P1840,P1850,P1860,P1870,P1880,LineData];
    layers = [rasterLayer]

//Declare the map object itself.
var map = new ol.Map({
    target: document.getElementById("map"),

    //Set up the layers that will be loaded in the map
    layers: layers,

    //Establish the view area. Note the reprojection from lat long (EPSG:4326) to Web Mercator (EPSG:3857)
    view: new ol.View({
        center: [-9000000, 4735000],
        projection: projection,
        zoom: 5
    })
});


var element = document.getElementById('popup');

var popup = new ol.Overlay({
  element: element,
  positioning: 'bottom-center',
  stopEvent: false
});

map.addOverlay(popup);

// display popup on click

map.on('click', function(evt) {
  //try to destroy it before doing anything else...s
  $(element).popover('destroy');
  var clickCoord = evt.coordinate;

  //Try to get a feature at the point of interest
  var feature = map.forEachFeatureAtPixel(evt.pixel,
      function(feature, layer) {
        return feature;
      });

  //if we found a feature then create and show the popup.
  if (feature) {
    popup.setPosition(clickCoord);
    if (feature.get('name') == "0") {
    var displaycontent = "This is a common Underground Railroad Route";
    }
    else {
    var displaycontent = feature.get('description');
    }

    $(element).popover({
      'placement': 'top',
      'html': true,
      'content': displaycontent
    });

    $(element).popover('show');

  } else {
    $(element).popover('destroy');
  }
});

// change mouse cursor when over marker
map.on('pointermove', function(e) {
  if (e.dragging) {
    $(element).popover('destroy');
    return;
  }
  var pixel = map.getEventPixel(e.originalEvent);
  var hit = map.hasFeatureAtPixel(pixel);
  map.getTarget().style.cursor = hit ? 'pointer' : '';
});