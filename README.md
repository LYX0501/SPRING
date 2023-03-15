# SPRING
<p align="center">
    <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-red.svg">
    </a>
    <a href="support os"><img src="https://img.shields.io/badge/os-linux%2C%20win%2C%20mac-pink.svg">
    </a>
    <a href=""><img src="https://img.shields.io/badge/python-3.6+-aff.svg">
    </a>
    <br />
</p>

## 🏴 **Overview**
we propose a [Situated Conversation Agent Pre-trained with Multimodal Questions from Incremental Layout Graph](https://arxiv.org/abs/2301.01949) (SPRING) with abilities of reasoning multi-hops spatial relationships and connecting them with visual attributes in crowded situated scenarios. Specifically, we design two types of Multimodal Question Answering (MQA) tasks to pretrain the agent. All QA pairs utilized during pretraining are generated from novel Increment Layout Graphs (ILG). QA pair difficulty labels automatically annotated by ILG are used to promote MQA-based Curriculum Learning. Experimental results verify the SPRING’s effectiveness, showing that it significantly outperforms state-of-the-art approaches on both SIMMC 1.0 and SIMMC 2.0 datasets.

![image1](./imgs/ILG.png)

![image2](./imgs/Spring.png)

## 🔥 News
- 2023.1.31: Code has been submitted to Security Department for check, which will be released in two weeks!
- 2023.1.5: Our paper is announced as AAAI 2023 Oral.
- 2022.11.18: Our paper is accepted by AAAI 2023 Main Track. 

## 🌏 Requirements
* python 3.6.12
* pytorch 1.8.2
* torchvision 0.9.2
* nltk 3.6.7

## 🔨 Installation
```
pip install -r requirements.txt
```

## 👐 Data Preparation
#### Download SIMMC 2.0 Dataset
Download the [SIMMC 2 dataset](https://github.com/facebookresearch/simmc2/tree/main/dstc10/data) via git-lfs and rearrange them in the **simmcdata** file as following format.
```
|-- simmc2_scene_images_dstc10_public_part1    # Images (unzip simmc2_scene_images_dstc10_public_part1.zip)
|   |-- cloth_store_1416238_woman_1_1.png
|   |-- cloth_store_1416238_woman_1_2.png
|   `-- ...
|-- simmc2_scene_images_dstc10_public_part2    # Images (unzip simmc2_scene_images_dstc10_public_part2.zip)
|   |-- cloth_store_1_1_1.png
|   |-- cloth_store_1_1_2.png

|-- public                                     # Scene (unzip simmc2_scene_jsons_dstc10_public.zip)
|   |-- cloth_store_1_1_1_bbox.json
|   |-- cloth_store_1_1_1_scene.json
|   `-- ...
|-- item2id.json                               # converted asset ID (provided by us)
|-- fashion_prefab_metadata_all.json           # fashion metadata
|-- furniture_prefab_metadata_all.json         # furniture metadata
|-- simmc2_dials_dstc10_train.json             # dialogue train split 
|-- simmc2_dials_dstc10_dev.json               # dialogue dev slit
|-- simmc2_dials_dstc10_devtest.json           # dialogue devtest split
```
**NOTE**: Some of the scene images are corrupted and therefore ignored. We do not make use of images in our model.
```
./data/images/cloth_store_1416238_woman_4_8.png
./data/images/cloth_store_1416238_woman_19_0.png
./data/images/cloth_store_1416238_woman_20_6.png
```
The final directory structure of the whole project is
```
|Project
|-- SPRING
|	| -- models
|	| -- tasks
|	| -- run_scripts
|	| -- dataset
|   `-- ...
|-- simmcdata
|	| -- simmc2_scene_images_dstc10_public_part
|	| -- simmc2_scene_images_dstc10_public_par2
|	| -- item2id.json
|	| -- fashion_prefab_metadata_all.json 
|   `-- ...
```

## 📝 **License**

Our repository is released under MIT License, see [LICENSE](LICENSE) for details.

## ✒ **Citation** 
Please cite our paper if you find it helpful :)

```
@article{long2023spring,
  author    = {Yuxing Long and
               Binyuan Hui and
               Fulong Ye and
               Yanyang Li and
               Zhuoxin Han and
               Caixia Yuan and
               Yongbin Li and
               Xiaojie Wang},
  title     = {{SPRING:} Situated Conversation Agent Pretrained with Multimodal Questions
               from Incremental Layout Graph},
  journal   = {CoRR},
  volume    = {abs/2301.01949},
  year      = {2023},
}
```
