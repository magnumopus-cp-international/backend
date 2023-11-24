from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from summery_creator.summery.views import ChunkedUploadCompleteView, ChunkedUploadView

urlpatterns = [
    path(
        "api/chunked_upload_complete/",
        csrf_exempt(ChunkedUploadCompleteView.as_view()),
        name="api_chunked_upload_complete",
    ),
    path(
        "api/chunked_upload/",
        csrf_exempt(ChunkedUploadView.as_view()),
        name="api_chunked_upload",
    ),
]
