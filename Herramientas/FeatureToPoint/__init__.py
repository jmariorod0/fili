def classFactory(iface):
    from .FeatureToPoint import FeatureToPointPlugin
    return FeatureToPointPlugin(iface)
