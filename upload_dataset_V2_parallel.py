import os
import pathlib
import dtlpy as dl
import pandas as pd
import random
import numpy as np

######################
# CSV Attributes map #
######################
csv_attributes_types_map = {
    "airport": dl.AttributesTypes.FREE_TEXT,
    "runway": dl.AttributesTypes.FREE_TEXT,
    "time": dl.AttributesTypes.FREE_TEXT,
    "slant_distance": dl.AttributesTypes.FREE_TEXT,
    "along_track_distance": dl.AttributesTypes.FREE_TEXT,
    "height_above_runway": dl.AttributesTypes.FREE_TEXT,
    "lateral_path_angle": dl.AttributesTypes.FREE_TEXT,
    "vertical_path_angle": dl.AttributesTypes.FREE_TEXT,
    "yaw": dl.AttributesTypes.FREE_TEXT,
    "pitch": dl.AttributesTypes.FREE_TEXT,
    "roll": dl.AttributesTypes.FREE_TEXT,
    "watermark_height": dl.AttributesTypes.FREE_TEXT,
    "x_A": dl.AttributesTypes.FREE_TEXT,
    "y_A": dl.AttributesTypes.FREE_TEXT,
    "x_B": dl.AttributesTypes.FREE_TEXT,
    "y_B": dl.AttributesTypes.FREE_TEXT,
    "x_C": dl.AttributesTypes.FREE_TEXT,
    "y_C": dl.AttributesTypes.FREE_TEXT,
    "x_D": dl.AttributesTypes.FREE_TEXT,
    "y_D": dl.AttributesTypes.FREE_TEXT,
    # Special
    "time_to_landing": dl.AttributesTypes.FREE_TEXT,
    "weather": dl.AttributesTypes.FREE_TEXT,
    "night": dl.AttributesTypes.YES_NO,
}


# def sort_function(x: pathlib.Path):
#     path_components = x.stem.split("_")[1:]
#     image_number_components = "".join(path_components)
#     image_number = "".join([char for char in image_number_components if not char.isalpha()])
#     return int(image_number)


def upload_dataset(dataset: dl.Dataset, data_path: str, images_indices: list[int]):
    csv_labels = set()

    # Make annotations path
    annotations_path = pathlib.Path(data_path).joinpath("annotations_V2")
    os.makedirs(annotations_path, exist_ok=True)

    if pathlib.Path(data_path).name == "LARD_test_real_edge_cases":
        csv_filepath = pathlib.Path(data_path).joinpath("Test_Real_Edge_Cases.csv")
    elif pathlib.Path(data_path).name == "LARD_test_real_nominal":
        csv_filepath = pathlib.Path(data_path).joinpath("Test_Real_Nominal.csv")
    else:
        csv_filepath = pathlib.Path(data_path).joinpath(f"{pathlib.Path(data_path).stem}.csv")
    csv_data = pd.read_csv(csv_filepath, delimiter=";")

    image_filepaths = pathlib.Path(data_path).joinpath("images").glob("*.*")
    # image_filepaths = sorted(image_filepaths, key=sort_function)
    image_filepaths = sorted(image_filepaths)
    uploads = []
    for image_idx in images_indices:
        # annotations = dl.AnnotationCollection()
        image_full_path = str(image_filepaths[image_idx])
        image_relative_path = str(pathlib.Path(image_full_path).relative_to(data_path)).replace("\\", "/")

        image_row_data = None
        for index, row in csv_data.iterrows():
            if row["image"] == image_relative_path:
                image_row_data = row
                break
        if image_row_data is None:
            raise ValueError(f"Image {image_relative_path} not found in csv data")

        #######################
        # Annotation from CSV #
        #######################
        csv_label = image_row_data["type"]
        csv_labels.add(csv_label)
        csv_metadata = {"user": {}}
        for attribute_key_name in csv_attributes_types_map.keys():
            # Check if the attribute is None, empty, or NaN
            if (
                (image_row_data.get(attribute_key_name, None) is None) or 
                (image_row_data[attribute_key_name] == "") or
                (isinstance(image_row_data[attribute_key_name], float) and np.isnan(image_row_data[attribute_key_name]))
            ):
                continue
            if attribute_key_name == "runway":
                attribute_value = image_row_data[attribute_key_name]
                if isinstance(attribute_value, str):
                    attribute_value = "".join([char for char in attribute_value if not char.isalpha()])
                attribute_value = int(attribute_value)
            else:
                attribute_value = image_row_data[attribute_key_name]
            csv_metadata["user"][attribute_key_name] = attribute_value
        # csv_classification = dl.Classification(label=csv_label)
        # annotations.add(annotation_definition=csv_classification)

        # Export Annotations
        # annotations_filepath = str(annotations_path.joinpath(f"{pathlib.Path(image_relative_path).stem}.json"))
        # with open(annotations_filepath, "w") as f:
        #     json.dump(annotations.to_json(), f)

        uploads.append(
            {
                "local_path": image_full_path,
                "item_metadata": csv_metadata,
            }
        )

    dataset.items.upload(
        local_path=pd.DataFrame(data=uploads)
    )

    csv_label_list = list(csv_labels)
    dataset.update_labels(label_list=csv_label_list, upsert=True)


def main(dataset_id=None):
    """
    Notice:
    - You need to download "LARD_train_VABB.zip" from: https://share.deel.ai/s/3ZyWamJWrqzCf74
    - Extract the zip to the folder "./downloads"
    """
    if dataset_id is None:
        dataset_id = "68c7ce3b768617fbe2033b3c"

    dataset = dl.datasets.get(dataset_id=dataset_id)
    data_paths = [
        # TRAIN #
        "downloads/LARD_train_BIRK_LFST",
        "downloads/LARD_train_DAAG_DIAP",
        "downloads/LARD_train_domain_adaptation",
        "downloads/LARD_train_KMSY",
        "downloads/LARD_train_LFMP_LFPO",
        "downloads/LARD_train_LFQQ",
        "downloads/LARD_train_LPPT_SRLI",
        "downloads/LARD_train_VABB",

        # TEST #
        "downloads/LARD_test_real_edge_cases",
        "downloads/LARD_test_real_nominal",
        "downloads/LARD_test_synth",
    ]
    images_sample_size = -1
    for data_path in data_paths:
        images_max_index = len(list(pathlib.Path(data_path).joinpath("images").glob("*.*")))
        if images_sample_size == -1:
            images_indices = range(images_max_index)
        else:
            images_indices = random.sample(range(images_max_index), images_sample_size)
        upload_dataset(dataset, data_path, images_indices)


if __name__ == "__main__":
    main()
