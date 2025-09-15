import dtlpy as dl
from download_zip import main as zip_downloader
from upload_dataset_V2_parallel import main as parallel_uploader


class Runner(dl.BaseServiceRunner):
    def __init__(self, dataset_id=None):
        if dataset_id is None:
            self.dataset_id = "68c7d8a00d74887f4810da29"
        else:
            self.dataset_id = dataset_id
        super().__init__()

    def run(self):
        zip_downloader()
        parallel_uploader(dataset_id=self.dataset_id)


def publish():
    project_id = "4192fb37-51c7-4f32-9632-15cc8cf45b85"
    project = dl.projects.get(project_id=project_id)
    project.dpks.publish()


def execute():
    project_id = "4192fb37-51c7-4f32-9632-15cc8cf45b85"
    function_name = "run"
    service_id = "fill"
    service = dl.services.get(service_id=service_id)
    service.execute(function_name=function_name, project_id=project_id)


if __name__ == "__main__":
    publish()
    # execute()
