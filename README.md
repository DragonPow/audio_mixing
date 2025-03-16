# Installing a Package Using Conda

This tutorial will guide you through the steps to install a package using Conda.

## Prerequisites

- Ensure you have Conda installed on your system. You can download it from [Anaconda's official website](https://www.anaconda.com/products/distribution).

## Preparing Steps

### Installing a Package (First Time Installation)

Default `[[myenv]]` is `audio_mixing_env`. You can change it to any name you want.

1. Create and activate env:
      ```bash
      conda create -n [[myenv]] python=3.8 # only run this step 1 time when you first clone the repo
      conda activate [[myenv]] # run this command every time you open a new terminal
      ```
2. Export the environment to a file:
      ```bash
      conda env export > environment.yml # this command must be run every time you install a new package
      ```
3. Install all packages from the environment file:
      ```bash
      conda env create -f environment.yml # only run this step 1 time when you first clone the repo
      ```
4. Install a package:
      ```bash
      conda install package_name
      ```

### Activate environment (After First Time Installation)

1. Activate the environment:
      ```bash
      conda activate [[myenv]]
      ```
2. Install a package:
      ```bash
      conda install package_name
      ```
3. Export the environment to a file:
      ```bash
      conda env export > environment.yml
      ```

## Run script steps
### Generation annotation file from raw dataset
```bash
python scripts/annotation_gen \
      --dataset_type [dataset_type] \
      --dataset_dir [dataset_dir] \
      --annotation_file_name [annotation_file_name] \
      --output_file_name [output_file_name] \
```

Where:
- `dataset_type` is the type of dataset. It can be either `vivos`.
- `dataset_dir` is the directory of the dataset. The directory should contain the audio files.
- `annotation_file_name` is the raw annotation file of dataset.
- `output_file_name` is the name of the output file.

### Create mixing dataset
First, file config is in `configs/config.json`. Updated the config file to match your dataset.

Second, run the following command to create a mixing dataset:
```bash
python scripts/mixing_dataset
```

The output will be saved in the `output_dir` in the config file.