from django.urls import path

from .views import GenerateLogoView

urlpatterns = [
    path("generate-logo/", GenerateLogoView.as_view(), name="generate-logo"),
]
