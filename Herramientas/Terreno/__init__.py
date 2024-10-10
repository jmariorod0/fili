def classFactory(iface):
    from .Terreno import CreateTerrenoLayerPlugin
    return CreateTerrenoLayerPlugin(iface)
