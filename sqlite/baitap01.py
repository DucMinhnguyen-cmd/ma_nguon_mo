import sqlite3

conn = sqlite3.connect("inventory.db")

cursor= conn.cursor()
# lệnh sql để tạo bảng products
sql1="""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price NUMERIC NOT NULL,
    quantity INTEGER
)
"""
# THỰC THI CÂU LỆNH TẠO BẢNG
cursor.execute(sql1)
conn.commit() #lưu thay đổi vào DB

#3 CRUD
#3.1 thêm (insert)
products_data=[
    ("laptop A100", 1200.50, 10),
    ("smartphone B200", 800.00, 25),
    ("tablet C300", 500.75, 15),
    ("smartwatch D400", 250.00, 30),
    ("headphones E500", 150.00, 50)
]
# lệnh sql để chèn dữ liệu. dùng "?" để tráng lỗi SQL injection
sql2="""
INSERT INTO products (name, price, quantity)
VALUES
(?,?,?)
"""
#THÊM NHIỀU BẢN GHI CÙNG LÚC
cursor.executemany(sql2, products_data) 
conn.commit() #lưu thay đổi
#3.2
sql3="SELECT* FROM products"
cursor.execute(sql3)
#lấy tất cả kết quả
all_products= cursor.fetchall()
#in tiêu đề
print(f"{'ID':<4} | {'tên sản phẩm':<20} | {'giá':<10} | {'số lượng':<10}")
#lặp và in ra
for p in all_products:
    print(f"{p[0]:<4} | {p[1]:<20} | {p[2]:<10} | {p[3]:<10}")
#3.3 UPDATE
sql4="""
UPDATE products
SET price=?, quantity=?
WHERE id=?
"""

update_data=(1050.00, 12, 1) #giá mới, số lượng mới, id cần cập nhật
cursor.execute(sql4, update_data)
conn.commit()
print("Cập nhật thành công!")

#3.4 DELETE
sql5="""
DELETE FROM products
WHERE id=?
"""
delete_id=(5,) #id cần xóa
cursor.execute(sql5, delete_id)
conn.commit()
print("Xóa thành công!")