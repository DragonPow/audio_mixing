# Installing a Package Using Conda

This tutorial will guide you through the steps to install a package using Conda.

## Prerequisites

- Ensure you have Conda installed on your system. You can download it from [Anaconda's official website](https://www.anaconda.com/products/distribution).

## Steps

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