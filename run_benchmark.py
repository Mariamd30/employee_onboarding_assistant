from benchmark import ejecutar_benchmark
from report import generar_reporte_md, guardar_csv

filas = ejecutar_benchmark()
csv_path = guardar_csv(filas)
md_path = generar_reporte_md(filas, csv_path)
print(csv_path, md_path)
