# Zealdown

用于手动下载、安装Zeal的docset

由于种种原因，可能无法在zeal中直接安装docset，也无法通过feed安装docset，这个脚本用于手动下载压缩包，并且安装docset。

## 使用方法

TODO

## TODO

- 根据网络情况，选择可访问的源
- 搜索zealusercontent的docset
- 指定目录，一键安装docset
- ✅输出zeal中的docset列表
- ✅输出zeal中的docset的下载连接

--

## 一些文档

### docset

一个docset就是一个压缩包，要安装docset，可以：
1. 通过zeal的docset列表安装
2. 通过添加feed安装docset
3. 手动下载docset，并且解压到zeal的docset目录下

优先选择前面两种安装方法，因为这样安装的docset可能得到及时的更新。

### docset来源

docset的来源有：
- 官方来源
- 用户贡献

**官方来源**

官方的docset就是在zeal的docset列表中可以直接下载的docset，要获取所有docset的列表以及feed可以访问这个链接：
```
https://api.zealdocs.org/v1/docsets
```

**用户贡献**

用户贡献的docset可以在[这个网站](https://zealusercontributions.now.sh/)

虽说有两个来源，但是最终都是从同一个域名下载，即`kapeli.com`，存放docset的服务器在不同的地区有不同的域名，下面是域名列表：

```
singapore.kapeli.com
tokyo.kapeli.com
london.kapeli.com
newyork.kapeli.com
sanfrancisco.kapeli.com
frankfurt.kapeli.com
sydney.kapeli.com
mumbai.kapeli.com
```

这个脚本最重要的功能就是，找到可以访问的域名，并下载docset。

### 如何手动安装docset

下载docset的压缩包，然后解压到zeal的docset目录下即可。
