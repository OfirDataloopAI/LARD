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
    attributes_types_map = {
        "airport": dl.AttributesTypes.FREE_TEXT,
        "runway": dl.AttributesTypes.NUMBER,
        # "time_to_landing": dl.AttributesTypes.FREE_TEXT,
        # "weather": dl.AttributesTypes.FREE_TEXT,
        # "night": dl.AttributesTypes.FREE_TEXT,
        "time": dl.AttributesTypes.FREE_TEXT,
        "slant_distance": dl.AttributesTypes.NUMBER,
        "along_track_distance": dl.AttributesTypes.NUMBER,
        "height_above_runway": dl.AttributesTypes.NUMBER,
        "lateral_path_angle": dl.AttributesTypes.NUMBER,
        "vertical_path_angle": dl.AttributesTypes.NUMBER,
        "yaw": dl.AttributesTypes.NUMBER,
        "pitch": dl.AttributesTypes.NUMBER,
        "roll": dl.AttributesTypes.NUMBER,
        "watermark_height": dl.AttributesTypes.NUMBER,
        "x_A": dl.AttributesTypes.NUMBER,
        "y_A": dl.AttributesTypes.NUMBER,
        "x_B": dl.AttributesTypes.NUMBER,
        "y_B": dl.AttributesTypes.NUMBER,
        "x_C": dl.AttributesTypes.NUMBER,
        "y_C": dl.AttributesTypes.NUMBER,
        "x_D": dl.AttributesTypes.NUMBER,
        "y_D": dl.AttributesTypes.NUMBER,
    }
    attributes_keys_map = {
        "airport": 1,
        "runway": 2,
        # "time_to_landing": -1,
        # "weather": -1,
        # "night": -1,
        "time": 3,
        "slant_distance": 4,
        "along_track_distance": 5,
        "height_above_runway": 6,
        "lateral_path_angle": 7,
        "vertical_path_angle": 8,
        "yaw": 9,
        "pitch": 10,
        "roll": 11,
        "watermark_height": 12,
        "x_A": 13,
        "y_A": 14,
        "x_B": 15,
        "y_B": 16,
        "x_C": 17,
        "y_C": 18,
        "x_D": 19,
        "y_D": 20,
    }
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
        attributes = {}
        for attribute_key_name, attribute_key_id in attributes_keys_map.items():
            attributes[attribute_key_id] = image_row_data[attribute_key_name]
        classification = dl.Classification(label=label, attributes=attributes)
        annotations.add(annotation_definition=classification)

        # Export Annotations
        annotations_filepath = str(annotations_path.joinpath(f"{pathlib.Path(image_relative_path).stem}.json"))
        with open(annotations_filepath, "w") as f:
            json.dump(annotations.to_json(), f)

        dataset.items.upload(local_path=image_full_path, local_annotations_path=annotations_filepath, overwrite=True)

    dataset.update_labels(label_list=list(labels), upsert=True)
    ontology = dataset._get_ontology()
    for attribute_key_name, attribute_type in attributes_types_map.items():
        ontology.update_attributes(
            title=attribute_key_name, key=attributes_keys_map[attribute_key_name], attribute_type=attribute_type
        )


def main():
    dataset_id = "68c28dae5d72d76d05b2ea79"
    data_path = "downloads/LARD_train_VABB"
    num_images = 10

    dataset = dl.datasets.get(dataset_id=dataset_id)
    upload_dataset(dataset, data_path, num_images)


if __name__ == "__main__":
    main()
