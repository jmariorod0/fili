def classFactory(iface):
    from .SummaryStatistics import SummaryStatisticsPlugin
    return SummaryStatisticsPlugin(iface)
