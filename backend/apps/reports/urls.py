from django.urls import path
from .views import VehicleProfitabilityReportView, SettlementReportView

urlpatterns = [
    path('profitability/', VehicleProfitabilityReportView.as_view(), name='report-profitability'),
    path('settlements/', SettlementReportView.as_view(), name='report-settlements'),
]
