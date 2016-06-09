from tethys_sdk.base import TethysAppBase, url_map_maker


class Gaugeviewer(TethysAppBase):
    """
    Tethys app class for GaugeViewer.
    """

    name = 'USGS and AHPS GaugeViewer'
    index = 'gaugeviewer:home'
    icon = 'gaugeviewer/images/gauge_icon.png'
    package = 'gaugeviewer'
    root_url = 'gaugeviewer'
    color = '#e74c3c'
    description = 'Place a brief description of your app here.'
    enable_feedback = False
    feedback_emails = []

        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='gaugeviewer',
                           controller='gaugeviewer.controllers.home'),
                    UrlMap(name='ahps',
                           url='ahps',
                           controller='gaugeviewer.controllers.ahps'),
                    UrlMap(name='usgs',
                           url='usgs',
                           controller='gaugeviewer.controllers.usgs'),
                    )

        return url_maps