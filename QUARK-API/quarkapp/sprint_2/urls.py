from django.conf.urls import url
from sprint_2 import views

urlpatterns = [
    url(r'^update_profile$', views.profile_update),
    url(r'^reset_password$', views.reset_password),
    url(r'^read_file$', views.read_file),
    url(r'^graph_data$', views.excel_data),
    url(r'^plot_graph$', views.plot_graph),
    url(r'^get_excel_data$', views.read_test_setup),
    url(r'^show_graph$', views.show_graph),
    url(r'^defects_by_severity$', views.defects_by_severity),
    url(r'^readRPAFile$', views.readRPAFile),
    url(r'^severity_by_cycle_by_modules$', views.severity_by_cycle_by_modules),
    url(r'^success_trend_graph$', views.success_trend_graph),
    url(r'^infoTileData$', views.infoTileData),
    url(r'^drill_down_DefectBySeverity$', views.drill_down_DefectBySeverity),
    url(r'^drill_down_TestCases$',views.drill_down_TestCases),
    url(r'^infotiledatadetails$', views.infoTileDataDetails),
    url(r'^read_test$', views.read_test),
    url(r'^update_table$', views.update_table)
]
