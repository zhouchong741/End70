# End Clothing 70% Off 折扣爬虫

这是一个 Python 脚本，用于自动从 End Clothing (CN) 网站的促销页面抓取所有折扣力度为 **70% off** 的商品，并将结果保存为 JSON 文件。

## 功能特点

- 自动遍历促销页面 (支持分页)
- **准确获取产品总数** - 使用 XPath 精确定位产品总数，自动计算总页数
- 筛选出折扣为 "70% off" 的商品
- 提取商品名称、原价、折后价、购买链接和**产品图片**
- 支持断点续传（每抓取 5 页自动保存一次）
- 自动去重

## 环境要求

- Python 3.x
- 需要安装以下 Python 库：
  - `requests`
  - `beautifulsoup4`

## 安装步骤

1. 确保已安装 Python。
2. 安装所需的依赖库：

```bash
pip install requests beautifulsoup4
```

## 使用方法

1. 打开终端 (Terminal) 或命令行窗口。
2. 切换到脚本所在目录。
3. 运行脚本：

```bash
python scrape_endclothing.py
```

脚本运行过程中会在控制台输出当前的抓取进度：

```
Fetching https://www.endclothing.com/cn/sale?page=1...
产品总数: 8021
每页商品数: 121
总页数: 67
Processing page 1...
Found 13 items on page 1.
Fetching https://www.endclothing.com/cn/sale?page=2...
...
```

## 输出结果

抓取完成后，结果将保存在当前目录下的 `endclothing_70off.json` 文件中。

**JSON 数据格式示例：**

```json
[
  {
    "name": "Adidas TaekwondoBlack & White",
    "original_price": "CN¥719",
    "sale_price": "CN¥216",
    "discount": "70% off",
    "url": "https://www.endclothing.com/cn/adidas-taekwondo-jq4775.html...",
    "productUrl": "https://media.endclothing.com/media/catalog/product/..."
  },
  ...
]
```

**数据字段说明：**
- `name`: 商品名称
- `original_price`: 原价
- `sale_price`: 折后价
- `discount`: 折扣标签（70% off）
- `url`: 商品详情页链接
- `productUrl`: 商品图片 URL

## 技术实现

### 准确获取产品总数

脚本使用 XPath 路径 `//*[@id="plpBody"]/div/div[2]/span` 准确获取页面显示的产品总数，然后根据每页商品数量自动计算总页数，确保遍历所有页面。

### 产品图片提取

脚本会自动提取每个产品的图片 URL，并转换为绝对路径保存到 `productUrl` 字段。

## 配置说明

如果需要调整抓取的页数限制，可以编辑 `scrape_endclothing.py` 文件：

- **修改输出文件名**：修改 `OUTPUT_FILE = "endclothing_70off.json"` 变量。
- **调整延时**：修改 `time.sleep(1)` 中的数值（单位：秒）。

## 注意事项

- 脚本包含延时 (`time.sleep(1)`) 以避免对服务器造成过大压力，请勿移除。
- 如果遇到网络错误，脚本会尝试跳过当前页面继续执行。
- 按 `Ctrl+C` 可以中断脚本，已抓取的数据会自动保存。
