from django.views.generic import View, TemplateView
from django.shortcuts import render

class VendorDashboardView(TemplateView):
    template_name = 'vendor/seller.html'
    title = "Seller Dashboard"

class InvoiceView(TemplateView):
    template_name = 'vendor/invoice.html'
    title = "Invoice"
