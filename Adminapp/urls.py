

from django.urls import path

from Adminapp.views import *
from . import views


urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('dashboard', DashboardView.as_view(), name='dashboard'),
    # path('add-category', AddCategoryView.as_view(), name='add-category'),
    # path('add-dish', AddDishView.as_view(), name='add-dish'),
    path('add-branch', AddBranchView.as_view(), name='add-branch'),
    path('add-carousel', AddCarouselView.as_view(), name='add-carousel'),
    path('dish-edit', EditDishView.as_view(), name='dish-edit'),
    path('add-offer', AddOfferView.as_view(), name='add-offer'),
    path('registerstaff', RegisterStaffView.as_view(), name='registerstaff'),
    path('branch-report', ViewBranchReportView.as_view(), name='branch-report'),
    path('view-branch', ViewBranchView.as_view(), name='view-branch'),
    path('delete-branch/<int:branch_id>', DeleteBranchView.as_view(), name='delete-branch'),
    path('branch-edit/<int:branch_id>/', EditBranchView.as_view(), name='branch-edit'),
    path('view-carousel', ViewcarouselView.as_view(), name='view-carousel'),
    path('view-categories', CategoryManagerView.as_view(), name='view_categories'),
    path('view-complaint', ViewComplaintView.as_view(), name='view-complaint'),
    path('view-dishes', ViewDishesView.as_view(), name='view-dishes'),
    path('view-offer', ViewOfferView.as_view(), name='view-offer'),
    path('view-staff', ViewStaffView.as_view(), name='view-staff'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('add-category/', views.add_category_ajax, name='add_category_ajax'),
    path('add-subcategory/', views.add_subcategory_ajax, name='add_subcategory_ajax'),
    path('add-subsubcategory/', views.add_subsubcategory_ajax, name='add_subsubcategory_ajax'),
    path('delete-category/<str:type>/<str:pk>/', delete_category, name='delete_category'),
    path('toggle-status/', views.toggle_staff_status, name='toggle_status'),
    path('delete-staff/<int:id>/', DeleteStaff.as_view(), name='delete_staff'),
    path('edit-staff/<int:id>/', EditStaffView.as_view(), name='edit_staff'),
    path('add-dish/', AddDishView.as_view(), name='add_dish'),
    path('get-subcategories/', get_subcategories, name='get_subcategories'),
    path('get-subsubcategories/', get_subsubcategories, name='get_subsubcategories'),
    path('delete-dish/<int:id>', DeleteDishes.as_view(), name='delete-dish'),
    path('edit-dish/<int:item_id>/', EditDishView.as_view(), name='edit_dish'),
    path('search-dishes/', views.search_dishes, name='search-dishes'),
    path('delete-offer/<int:id>/', DeleteOfferView.as_view(), name='delete-offer'),
    path('edit-offer/<int:offer_id>/', EditOfferView.as_view(), name='edit-offer'),
    path('delete-carousel/<int:id>/', DeleteCarousel.as_view(), name='delete-carousel'),
    # path('editcarousel/<int:carousel_id>/', EditCarousel.as_view(), name='editcarousel'),
    path('view-coupon', ViewCouponView.as_view(), name='view-coupon'),
    path('add-coupon', AddCouponView.as_view(), name='add-coupon'),
    path('edit-coupon/<int:coupon_id>/', EditCouponView.as_view(), name='edit_coupon'),
    path('delete-coupon/<int:id>', DeleteCouponView.as_view(), name='delete-coupon'),


]
