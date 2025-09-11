import os
import pathlib
import dtlpy as dl
import pandas as pd
import json
import yaml


######################
# CSV Attributes map #
######################
csv_attributes_types_map = {
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
csv_attributes_keys_map = {
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


def sort_function(x: pathlib.Path):
    path_components = x.stem.split("_")[1:]
    image_number = "".join(path_components)
    return int(image_number)


def upload_dataset(dataset: dl.Dataset, data_path: str, num_images: int):
    csv_labels = set()

    # Make annotations path
    annotations_path = pathlib.Path(data_path).joinpath("annotations")
    os.makedirs(annotations_path, exist_ok=True)

    csv_filepath = pathlib.Path(data_path).joinpath(f"{pathlib.Path(data_path).stem}.csv")
    csv_data = pd.read_csv(csv_filepath, delimiter=";")

    image_filepaths = pathlib.Path(data_path).joinpath("images").glob("*.jpeg")
    image_filepaths = sorted(image_filepaths, key=sort_function)
    for image_idx in range(num_images):
        annotations = dl.AnnotationCollection()
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
        csv_attributes = {}
        for attribute_key_name, attribute_key_id in csv_attributes_keys_map.items():
            csv_attributes[attribute_key_id] = image_row_data[attribute_key_name]
        csv_classification = dl.Classification(label=csv_label, attributes=csv_attributes)
        annotations.add(annotation_definition=csv_classification)

        ########################
        # Annotation from YAML #
        ########################
        yaml_filepath = pathlib.Path(data_path).joinpath(f"{pathlib.Path(data_path).stem}_scenarios").joinpath(
            f"{pathlib.Path(image_relative_path).stem.rsplit("_", 1)[0]}.yaml"
        )
        with open(yaml_filepath, "r") as f:
            yaml_data = yaml.safe_load(f)
        yaml_label = "yaml_data"
        yaml_attributes = {
            # "airport": yaml_data["airport"],
            "fov": yaml_data["image"]["fov"],
            # "watermark_height": yaml_data["image"]["watermark_height"],
        }
        pose_info = yaml_data["poses"][image_idx]
        # yaml_attributes["poses.airport"] = pose_info["airport"]
        yaml_attributes["pose.0"] = pose_info["pose"][0]
        yaml_attributes["pose.1"] = pose_info["pose"][1]
        yaml_attributes["pose.2"] = pose_info["pose"][2]
        yaml_attributes["pose.3"] = pose_info["pose"][3]
        yaml_attributes["pose.4"] = pose_info["pose"][4]
        yaml_attributes["pose.5"] = pose_info["pose"][5]
        # yaml_attributes["runway"] = pose_info["runway"]
        # yaml_attributes["time.day"] = pose_info["time"]["day"]
        # yaml_attributes["time.hour"] = pose_info["time"]["hour"]
        # yaml_attributes["time.minute"] = pose_info["time"]["minute"]
        # yaml_attributes["time.month"] = pose_info["time"]["month"]
        # yaml_attributes["time.second"] = pose_info["time"]["second"]
        # yaml_attributes["time.year"] = pose_info["time"]["year"]
        yaml_classification = dl.Classification(label=yaml_label, attributes=yaml_attributes)
        annotations.add(annotation_definition=yaml_classification)

        ####################### 
        # Annotation from ESP #
        #######################
        esp_filepath = pathlib.Path(data_path).joinpath(f"{pathlib.Path(data_path).stem}_scenarios").joinpath(
            f"{pathlib.Path(image_relative_path).stem.rsplit("_", 1)[0]}.esp"
        )
        with open(esp_filepath, "r") as f:
            esp_data = json.load(f)
        esp_label = "esp_data"
        esp_attributes = {
            "modelVersion": esp_data["modelVersion"],
            "frameRate": esp_data["settings"]["frameRate"],
            "duration": esp_data["settings"]["duration"],
            "timeFormat": esp_data["settings"]["timeFormat"],
            "animationModel.roving": esp_data["scenes"][0]["animationModel"]["roving"],
            "animationModel.logarithmic": esp_data["scenes"][0]["animationModel"]["logarithmic"],
            "animationModel.groupedPosition": esp_data["scenes"][0]["animationModel"]["groupedPosition"],

            ###############################
            # 'scene[0].attributes' start #
            ###############################

            "longitude.relative": esp_data["scenes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["value"]["relative"],
            "longitude.time": esp_data["scenes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["keyframes"][image_idx]["time"],
            "longitude.value": esp_data["scenes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["keyframes"][image_idx]["value"],

            "latitude.relative": esp_data["scenes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["attributes"][1]["value"]["relative"],
            "latitude.time": esp_data["scenes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["attributes"][1]["keyframes"][image_idx]["time"],
            "latitude.value": esp_data["scenes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["attributes"][1]["keyframes"][image_idx]["value"],

            "altitude.relative": esp_data["scenes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["attributes"][2]["value"]["relative"],
            "altitude.logarithmic": esp_data["scenes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["attributes"][2]["value"]["logarithmic"],
            "altitude.time": esp_data["scenes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["attributes"][2]["keyframes"][image_idx]["time"],
            "altitude.value": esp_data["scenes"][0]["attributes"][0]["attributes"][0]["attributes"][0]["attributes"][2]["keyframes"][image_idx]["value"],

            # UNKNOWN format #
            # "cameraTargetEffect.type": esp_data["scenes"][0]["attributes"][0]["attributes"][0]["attributes"][1]["attributes"][0]["type"],
            # "cameraTargetEffect.value":
            # "cameraTargetEffect.longitudePOI":
            # "cameraTargetEffect.latitudePOI":
            # "cameraTargetEffect.altitudePOI":
            # "cameraTargetEffect.altitudePOI.logarithmic":
            # "cameraTargetEffect.influence":

            "rotationX.maxValueRange": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][0]["value"]["maxValueRange"],
            "rotationX.minValueRange": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][0]["value"]["minValueRange"],
            "rotationX.relative": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][0]["value"]["relative"],
            "rotationX.time": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][0]["keyframes"][image_idx]["time"],
            "rotationX.value": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][0]["keyframes"][image_idx]["value"],

            "rotationY.maxValueRange": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][1]["value"]["maxValueRange"],
            "rotationY.minValueRange": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][1]["value"]["minValueRange"],
            "rotationY.relative": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][1]["value"]["relative"],
            "rotationY.time": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][1]["keyframes"][image_idx]["time"],
            "rotationY.value": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][1]["keyframes"][image_idx]["value"],

            "rotationZ.maxValueRange": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][2]["value"]["maxValueRange"],
            "rotationZ.minValueRange": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][2]["value"]["minValueRange"],
            "rotationZ.relative": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][2]["value"]["relative"],
            "rotationZ.time": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][2]["keyframes"][image_idx]["time"],
            "rotationZ.value": esp_data["scenes"][0]["attributes"][0]["attributes"][2]["attributes"][2]["keyframes"][image_idx]["value"],

            "fov.relative": esp_data["scenes"][0]["attributes"][0]["attributes"][3]["attributes"][0]["value"]["relative"],
            "fov.time": esp_data["scenes"][0]["attributes"][0]["attributes"][3]["attributes"][0]["keyframes"][image_idx]["time"],
            "fov.value": esp_data["scenes"][0]["attributes"][0]["attributes"][3]["attributes"][0]["keyframes"][image_idx]["value"],

            # UNKNOWN format #
            # "exposure":
            # "aperture":
            # "minFocusLength":

            "sunVisibility.relative": esp_data["scenes"][0]["attributes"][1]["attributes"][0]["value"]["relative"],

            "worldTime.maxValueRange": esp_data["scenes"][0]["attributes"][1]["attributes"][1]["value"]["maxValueRange"],
            "worldTime.minValueRange": esp_data["scenes"][0]["attributes"][1]["attributes"][1]["value"]["minValueRange"],
            "worldTime.relative": esp_data["scenes"][0]["attributes"][1]["attributes"][1]["value"]["relative"],
            "worldTime.time": esp_data["scenes"][0]["attributes"][1]["attributes"][1]["keyframes"][image_idx]["time"],
            "worldTime.value": esp_data["scenes"][0]["attributes"][1]["attributes"][1]["keyframes"][image_idx]["value"],

            "cloudVisibility.time": esp_data["scenes"][0]["attributes"][1]["attributes"][1]["attributes"][0]["keyframes"][image_idx]["time"],
            "cloudVisibility.value": esp_data["scenes"][0]["attributes"][1]["attributes"][1]["attributes"][0]["keyframes"][image_idx]["value"],

            # UNKNOWN format #
            # "cloudopacity":
            # "cloudheight"

            "clouddate.maxValueRange": esp_data["scenes"][0]["attributes"][1]["attributes"][1]["attributes"][3]["value"]["maxValueRange"],
            "clouddate.minValueRange": esp_data["scenes"][0]["attributes"][1]["attributes"][1]["attributes"][3]["value"]["minValueRange"],
            "clouddate.relative": esp_data["scenes"][0]["attributes"][1]["attributes"][1]["attributes"][3]["value"]["relative"],

            "starsEnabled.relative": esp_data["scenes"][0]["attributes"][1]["attributes"][2]["attributes"][0]["value"]["relative"],

            # UNKNOWN format #
            # "seawaterGroup.seawater":

            "seawaterGroup.influence.relative": esp_data["scenes"][0]["attributes"][1]["attributes"][3]["attributes"][1]["value"]["relative"],

            "buildingsEnabled.time": esp_data["scenes"][0]["attributes"][1]["attributes"][4]["keyframes"][image_idx]["time"],
            "buildingsEnabled.value": esp_data["scenes"][0]["attributes"][1]["attributes"][4]["keyframes"][image_idx]["value"],

            #############################
            # 'scene[0].attributes' end #
            #############################

            "cameraExport.logarithmic": esp_data["scenes"][0]["cameraExport"]["logarithmic"],
            "cameraExport.modelVersion": esp_data["scenes"][0]["cameraExport"]["modelVersion"],
        }
        esp_classification = dl.Classification(label=esp_label, attributes=esp_attributes)
        annotations.add(annotation_definition=esp_classification)

        # Export Annotations
        annotations_filepath = str(annotations_path.joinpath(f"{pathlib.Path(image_relative_path).stem}.json"))
        with open(annotations_filepath, "w") as f:
            json.dump(annotations.to_json(), f)

        dataset.items.upload(local_path=image_full_path, local_annotations_path=annotations_filepath, overwrite=True)

    csv_label_list = list(csv_labels)
    dataset.update_labels(label_list=csv_label_list, upsert=True)
    ontology = dataset._get_ontology()

    # Updating CSV attributes
    for attribute_key_name, attribute_type in csv_attributes_types_map.items():
        ontology.update_attributes(
            title=attribute_key_name,
            key=csv_attributes_keys_map[attribute_key_name],
            attribute_type=str(attribute_type),
            scope=csv_label_list,
        )

    # TODO: Updating YAML attributes

    # TODO: Updating ESP attributes


def main():
    dataset_id = "68c28dae5d72d76d05b2ea79"
    data_path = "downloads/LARD_train_VABB"
    num_images = 1

    dataset = dl.datasets.get(dataset_id=dataset_id)
    upload_dataset(dataset, data_path, num_images)


if __name__ == "__main__":
    main()
