def classFactory(iface):
    from .FeatureVerticesToPoints import FeatureVerticesToPointsPlugin
    return FeatureVerticesToPointsPlugin(iface)
