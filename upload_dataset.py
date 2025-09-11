import os
import pathlib
import dtlpy as dl
import pandas as pd
import json


def sort_function(x: pathlib.Path):
    path_components = x.stem.split("_")[1:]
    image_number = "".join(path_components)
    return int(image_number)


def upload_dataset(dataset: dl.Dataset, data_path: str, num_images: int):
    labels = set()

    # Make annotations path
    annotations_path = pathlib.Path(data_path).joinpath("annotations")
    os.makedirs(annotations_path, exist_ok=True)

    csv_data = pd.read_csv(pathlib.Path(data_path).joinpath(f"{pathlib.Path(data_path).stem}.csv"), delimiter=";")

    image_filepaths = pathlib.Path(data_path).joinpath("images").glob("*.jpeg")
    image_filepaths = sorted(image_filepaths, key=sort_function)
    for i in range(num_images):
        annotations = dl.AnnotationCollection()
        image_full_path = str(image_filepaths[i])
        image_relative_path = str(pathlib.Path(image_full_path).relative_to(data_path)).replace("\\", "/")

        image_row_data = None
        for index, row in csv_data.iterrows():
            if row["image"] == image_relative_path:
                image_row_data = row
                break
        if image_row_data is None:
            raise ValueError(f"Image {image_relative_path} not found in csv data")

        # Annotation from CSV
        label = image_row_data["type"]
        labels.add(label)
        attributes = {
            "airport": image_row_data["airport"],
            "runway": image_row_data["runway"],
            # "time_to_landing": image_row_data["time_to_landing"],
            # "weather": image_row_data["weather"],
            # "night": image_row_data["night"],
            "time": image_row_data["time"],
            "slant_distance": image_row_data["slant_distance"],
            "along_track_distance": image_row_data["along_track_distance"],
            "height_above_runway": image_row_data["height_above_runway"],
            "lateral_path_angle": image_row_data["lateral_path_angle"],
            "vertical_path_angle": image_row_data["vertical_path_angle"],
            "yaw": image_row_data["yaw"],
            "pitch": image_row_data["pitch"],
            "roll": image_row_data["roll"],
            "watermark_height": image_row_data["watermark_height"],
            "x_A": image_row_data["x_A"],
            "y_A": image_row_data["y_A"],
            "x_B": image_row_data["x_B"],
            "y_B": image_row_data["y_B"],
            "x_C": image_row_data["x_C"],
            "y_C": image_row_data["y_C"],
            "x_D": image_row_data["x_D"],
            "y_D": image_row_data["y_D"],
        }
        classification = dl.Classification(label=label, attributes=attributes)
        annotations.add(annotation_definition=classification)

        annotations_filepath = str(annotations_path.joinpath(f"{pathlib.Path(image_relative_path).stem}.json"))
        with open(annotations_filepath, "w") as f:
            json.dump(annotations.to_json(), f)

        dataset.items.upload(local_path=image_full_path, local_annotations_path=annotations_filepath, overwrite=True)

    dataset.update_labels(label_list=list(labels), upsert=True)


def main():
    dataset_id = "68c28dae5d72d76d05b2ea79"
    data_path = "downloads/LARD_train_VABB"
    num_images = 10

    dataset = dl.datasets.get(dataset_id=dataset_id)
    upload_dataset(dataset, data_path, num_images)


if __name__ == "__main__":
    main()
