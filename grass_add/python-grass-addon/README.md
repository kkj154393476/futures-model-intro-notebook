# 如何开发GRASS GIS7 Python 插件

本材料翻译自github：

https://github.com/wenzeslaus/python-grass-addon

## 使用指导

### 仅使用GRASS GIS 图形界面运行程序

启动GRASS GIS程序，将下载的后缀为`.ipynb`的文件打开。
在GRASS GIS的*Layer Manager*窗口中，选择底部的*Python shell*。
即可进入Python控制台，可以将`.ipynb`中的代码复制到*Python shell*中进行测试。


### 使用独立的jupyter notebook运行程序


在系统Terminal中，根据自己的需要创建项目文件夹：
    
    mkdir grass_addon
    cd grass_addon

    git clone https://github.com/wenzeslaus/python-grass-addon.git

未翻墙的情况下，为了加快下载速度，可以使用码云服务：
    
    git clone https://gitee.com/jiangroubao/python-grass-addon.git

项目克隆完成后，进入项目目录中：

    cd python-grass-addon

在项目目录下运行GRASS GIS程序，使用默认的北卡罗来纳州样例数据

    grass7

打开GRASS GIS的*Layer Manager*窗口，在下方的console中输入并回车：

    ipython notebook


然后会看到弹出浏览器，可以在其中选择单个的`.ipynb`，在Jupyter Notebook环境中编辑并运行示例。


## 摘要

GRASS GIS是地理数据分析的领先软件，它的核心版本提供了400多个模块以及许多附加组件（即用户提供的模块)。但是，如果要寻找的工具不在GRASS GIS中怎么办？ 因此，只需创建自己的，我们将在本教程中展示如何实现。


在GRASS GIS 7中，Python是用于创建插件的默认语言，GRASS GIS中包含两个主要的Python库，Python脚本库允许通过链接现有模块来创建自己的工作流程，执行分析和计算新数据。


使用C语言封装的PyGRASS函数库，可以直接通过Python调用创建新的数据集（矢量或栅格），从而大大提高了脚本的功能和性能。可以方便地将GRASS Python库与其他Python库（例如NumPy或SciPy）混合使用。在本教程中，将指导完成编写自己的Python脚本的基本步骤，从调用和链接GRASS GIS模块开始，然后是使用PyGRASS直接访问和修改数据等更多python体验。


然后，通过定义一个简单的界面来启用自动生成的GUI，从而将脚本升级为插件。教程的下一部分将探讨GRASS GIS 7功能的更高级用法，包括在插件中使用Python API处理时间序列数据，最后基于自己开发的插件创建自己的工具箱，最后介绍测试插件的测试框架 以确保插件状态良好。



## 需要的知识背景

学习者应具有GIS的基础知识，GRASS GIS的基础知识、Python的基础知识、Docker容器的基础知识。

## 安装服务

在学习过程中，借助于服务器搭建好的配置环境，使用IPython Notebook（Jupyter Notebook）的构建方式，而不是在每台计算机上设置环境。当IPython Notebook在服务器上使用，学习者只需要一个浏览器进行编程，服务器端的设置都可以基于`Docker`环境进行构建。构建步骤为：

    mkdir workdir
    cd workdir

    wget http://grass.osgeo.org/sampledata/north_carolina/nc_basic_spm_grass7.tar.gz
    wget https://github.com/wenzeslaus/python-grass-addon/archive/master.tar.gz

    tar xvf nc_basic_spm_grass7.tar.gz
    tar xvf master.tar.gz

如果下载比较慢，可以从百度云下载
链接：https://pan.baidu.com/s/10mYXgn2xt6RhMa7kQX5B7A 
提取码：h19p 

然后，获取GRASS GIS的`Docker`镜像，请注意，如果用户没有使用`Docker`的权限（通常为defaut），则必须在docker命令前加上`sudo`前缀。这一条在之后的Docker环境中的操作同样适用。
同样如果docker下载较慢的话，在上面提到的百度云下载，下载后解压执行docker build

    docker build github.com/wenzeslaus/grass-gis-docker

要创建镜像和容器，需要此存储库中的一些文件移动到`workdir`中（我们在前面的步骤中获取了它的内容），使用`mv`指令（移动而不是复制）是因为之后不需要将这些文件编译到容器中。

    mv python-grass-addon-master/Dockerfile .
    mv python-grass-addon-master/run_containers.sh .
    mv python-grass-addon-master/command_containers.sh .

然后，基于示例数据集和Notebook构建Docker镜像。如果将镜像用于GRASS GIS（请参见上文），请确保`Dockerfile`中具有正确的映像名称（由以下命令使用）。

    docker build -t wenzeslaus/python-grass-addon .

在创建镜像的同时，为每一个使用者创建配置文件，该文件的每行开头必须包含电子邮件格式（例如CSV，开头的双引号将被忽略）。

    john@university.edu
    jsmith@example.com

然后，开始创建镜像：

    ./run_containers.sh workshop_atendees.txt 9000

另外，可以仅指定要创建的容器数量，而不用配置具体的使用者：

    ./run_containers.sh 15 9000

这将然后会自动生成URL和密码列表以及相关的用户名，用户名仅用于跟踪容器和分发凭据。注意，使用者将必须在其浏览器中允许“不受信任的连接”对话框，因为所使用的证书是自签名的。

改指令同时也会创建一个名为`containers_workshop_atendees.txt`或者`containers_dateandtime.txt`的带有容器名称的文本文件。


如果要退出容器，请使用：

    ./command_conatiners.sh stop containers_workshop_atendees.txt
    ./command_conatiners.sh rm containers_workshop_atendees.txt


## 使用IPython Notebook服务器时的说明
学习者将会获得如下网址：

    https://fatra.cnr.ncsu.edu:9503

将url键入到Web浏览器中，包括末尾的*s*，注意使用的是`https`协议，还请注意已指定端口号（末尾的数字与域之间用冒号隔开）。

浏览器将警告您有关无效的安全证书，在这种情况下，您可以允许其运行，出现此消息的原因是证书是自签名的。

最后，输入您得到的密码，登陆到IPython Notebook环境中。

## 该教程的视频

(https://www.youtube.com/watch?v=PX2UpMhp2hc)


## 原作者

* Pietro Zambelli, European Research Academy
* Markus Neteler, Fondazione Edmund Mach
* Luca Delucchi, Fondazione Edmund Mach
* Vaclav Petras, NCSU OSGeoREL
* Anna Petrasova, NCSU OSGeoREL

Copyright (C) 2015 by authors.


## 协议

本文档根据CC BY-SA和GNU FDL 双重许可

代码示例执行GNU GPL 2 许可