from jinja2 import Environment, FileSystemLoader

# 加载模板文件所在目录
file_loader = FileSystemLoader('templates')  # 假设模板文件存放在 templates 文件夹中
env = Environment(loader=file_loader)

# 加载模板文件
template = env.get_template('template.html')

# 渲染模板数据
data = {
    "title": "My Page",
    "name": "Alice",
    "items": ["Item 1", "Item 2", "Item 3"]
}
output = template.render(data)

# 输出渲染结果
print(output)
