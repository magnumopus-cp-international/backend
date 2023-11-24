from summery_creator.contrib.chunked_upload.models import ChunkedUpload
from summery_creator.contrib.chunked_upload.views import (
    ChunkedUploadCompleteView as ChunkedUploadABSCompleteView,
)
from summery_creator.contrib.chunked_upload.views import (
    ChunkedUploadView as ChunkedUploadABSView,
)
from summery_creator.summery.models import Lesson


class ChunkedUploadView(ChunkedUploadABSView):
    model = ChunkedUpload
    field_name = "file"

    def check_permissions(self, request):
        ...


class ChunkedUploadCompleteView(ChunkedUploadABSCompleteView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = {}

    model = ChunkedUpload

    def check_permissions(self, request):
        ...

    def on_completion(self, uploaded_file, request):
        f = Lesson.objects.create(
            file=uploaded_file,
        )
        self.message = {
            "message": f"File {f.file.name.split('/')[-1]} successfully uploaded",
            "file_id": f.id,
            "status": True,
        }

    def get_response_data(self, chunked_upload, request):
        return self.message
