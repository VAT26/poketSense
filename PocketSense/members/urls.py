from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
#from .views import FriendViewSet, TransactionViewSet, SpendingViewSet, SpendingCategoryViewSet

# router = DefaultRouter()
# router.register(r'friends', FriendViewSet, basename='friend')
# router.register(r'transactions', TransactionViewSet, basename='transaction')
# router.register(r'spendings', SpendingViewSet, basename='spending')
# router.register(r'categories', SpendingCategoryViewSet, basename='category')

urlpatterns = [
    #path('api/', include(router.urls)),
    path('signup/',signup_view,name='signup'),
    path('login/',login_view,name='login'),
     path('dashboard/',dashboard, name='dashboard'),
    path('split_money/', split_money, name='split_money'),
    path('send_friend_request/<int:friend_id>/',   send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:friend_id>/', accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:friend_id>/', reject_friend_request, name='reject_friend_request'),
    path('logout/', user_logout, name='user_logout'),
    path('api/friends/', FriendListView.as_view(), name='friend-list'),
    path('api/transactions/', TransactionCreateView.as_view(), name='transaction-create'),
    path('api/monthly_spending/', MonthlySpendingAnalysisView.as_view(), name='monthly-spending'),

   
]   
