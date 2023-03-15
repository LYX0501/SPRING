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
