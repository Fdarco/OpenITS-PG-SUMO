# 说明

该仓库中的数据和路网是基于 [City-scale synthetic individual-level vehicle trip data](https://springernature.figshare.com/collections/City-Scale_Synthetic_Individual-level_Vehicle_Trip_Data/6148536/1) 的路网和数据生成的。提供了 PostgreSQL (+PostGIS) 数据库导入代码，方便查看相关数据。同时基于原数据提供了 SUMO 路网和交通流量，方便开展仿真等研究。当你使用该仓库中的数据和路网时，请务必引用原工作：

```latex
@article{li2023city,
  title={City-scale synthetic individual-level vehicle trip data},
  author={Li, Guilong and Chen, Yixian and Wang, Yimin and Nie, Peilin and Yu, Zhi and He, Zhaocheng},
  journal={Scientific Data},
  volume={10},
  number={1},
  pages={96},
  year={2023},
  publisher={Nature Publishing Group UK London}
}
```

# 使用手册

本仓库主要将 `City-scale synthetic individual-level vehicle trip data` 中的路网和数据转化为 PostgreSQL 数据库和 SUMO 仿真。该仓库不提供原数据，请点击[链接](https://springernature.figshare.com/collections/City-Scale_Synthetic_Individual-level_Vehicle_Trip_Data/6148536/1)，自行下载。

## 获取原数据

原始数据为安徽省宣城市的路网和交通流量，路网可视化如下图所示：

![img](assets/roadNetworkGIS.png)

下载原数据后，请在根目录下新建 `openits` 文件夹，然后将下载的数据如下排放，以方便后续的使用：

```txt
./
├──openits
│   ├── road_network
│   │   ├── topo_centerroad.cpg
│   │   ├── topo_centerroad.dbf
│   │   ├── topo_centerroad.prj
│   │   ├── topo_centerroad.qpj
│   │   ├── topo_centerroad.shp
│   │   └── topo_centerroad.shx
│   ├── The_synthetic_individual-level_trip_dataset.csv
│   └── zone_roads.csv
├── ...
└── readme.md
```

