from django.urls import path
from .views import AdvisorSignUp, AddClient, ListClients, UserSignUp, AddProduct, AdvisorPurchaseProduct

urlpatterns = [
    path('advisor-signup/', AdvisorSignUp.as_view()),
    path('add-client/',AddClient.as_view()),
    path('list-clients/<int:advisor_id>/',ListClients.as_view()),
    path('user-signup/',UserSignUp.as_view()),
    path('add-product/',AddProduct.as_view()),
    path('advisor-purchase-product/',AdvisorPurchaseProduct.as_view()),

]