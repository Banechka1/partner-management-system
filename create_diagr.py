from graphviz import Digraph

# Добавляем путь к Graphviz (если нужно)
import os
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

# Создаем объект Graphviz
dot = Digraph(
    comment="ER Diagram",
    format="pdf",
    graph_attr={"splines": "ortho", "nodesep": "0.8", "ranksep": "1.5", "fontsize": "12"},
    node_attr={"shape": "record", "style": "filled", "fillcolor": "lightblue", "fontname": "Arial", "fontsize": "10"},
    edge_attr={"fontname": "Arial", "fontsize": "9"}
)

# Добавляем таблицы
dot.node("Partners", "{Партнеры | {<f0> PartnerID (PK) | Name | Phone | Email | Address | RegistrationDate}}")
dot.node("Products", "{Продукция | {<f0> ProductID (PK) | Name | Description | Price}}")
dot.node("SalesHistory", "{История продаж | {<f0> SaleID (PK) | PartnerID (FK) | ProductID (FK) | Quantity | SaleDate}}")

# Добавляем связи между таблицами
dot.edge("SalesHistory:f1", "Partners:f0", label="FK: PartnerID", arrowhead="none", color="darkgreen")
dot.edge("SalesHistory:f2", "Products:f0", label="FK: ProductID", arrowhead="none", color="darkgreen")

# Сохраняем диаграмму в файл
dot.render("er_diagram", view=True)