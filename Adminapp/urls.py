

from django.urls import path

from Adminapp.views import *

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('dashboard', DashboardView.as_view(), name='dashboard'),
    path('add-category', AddCategoryView.as_view(), name='add-category'),
    path('add-dish', AddDishView.as_view(), name='add-dish'),
    path('add-branch', AddBranchView.as_view(), name='add-branch'),
    path('add-carousel', AddCarouselView.as_view(), name='add-carousel'),
    path('dish-edit', EditDishView.as_view(), name='dish-edit'),
    path('add-offer', AddOfferView.as_view(), name='add-offer'),
    path('registerstaff', RegisterStaffView.as_view(), name='registerstaff'),
    path('branch-report', ViewBranchReportView.as_view(), name='branch-report'),
    path('view-branch', ViewBranchView.as_view(), name='view-branch'),
    path('view-carousel', ViewcarouselView.as_view(), name='view-carousel'),
    path('view-category', ViewCategoryView.as_view(), name='view-category'),
    path('view-complaint', ViewComplaintView.as_view(), name='view-complaint'),
    path('view-dishes', ViewDishesView.as_view(), name='view-dishes'),
    path('view-offer', ViewOfferView.as_view(), name='view-offer'),
    path('view-staff', ViewStaffView.as_view(), name='view-staff'),
]
