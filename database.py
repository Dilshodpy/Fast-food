import sqlite3

from config import DEBUG


def connect_database():
    connect = sqlite3.connect("pro_food_db.sqlite")
    cur = connect.cursor()
    return connect, cur


class InitDB:
    def __init__(self):
        self.__database, self.__cursor = connect_database()

    def __create_users_table(self):
        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name VARCHAR(100) NOT NULL,
            chat_id INTEGER NOT NULL UNIQUE 
        )""")

    def __create_carts_table(self):
        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS carts(
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(user_id),
            
            total_price DECIMAL(12, 2) DEFAULT 0,
            total_quantity INTEGER DEFAULT 0,
            in_order BOOL DEFAULT False
        )""")

    def __create_cart_products_table(self):
        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS cart_products(
            cart_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id INTEGER REFERENCES carts(cart_id),
            product_name VARCHAR(30) NOT NULL,
            product_id REFERENCES products(product_id),
            quantity INTEGER NOT NULL,
            final_price DECIMAL(12, 2) NOT NULL,
            
            UNIQUE(product_name, cart_id)
        )""")

    def __create_categories_table(self):
        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS categories(
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(30) NOT NULL UNIQUE
        )""")

    def __create_products_table(self):
        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS products(
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER REFERENCES categories(category_id),
            title VARCHAR(30) NOT NULL UNIQUE,
            price DECIMAL(9, 2) NOT NULL,
            preview VARCHAR(100) NOT NULL UNIQUE,
            ingredients VARCHAR(150)  
        )""")

    def __create_orders_table(self):
        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS orders(
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id INTEGER REFERENCES carts(cart_id) NOT NULL,
            user_id INTEGER REFERENCES users(user_id) NOT NULL,
            create_date TEXT NOT NULL,
            total_price DECIMAL(12, 2) DEFAULT 0,
            total_quantity INTEGER DEFAULT 0,
            pay_status BOOL DEFAULT False
        )""")

    def init(self):
        """Инициализация Базы данных"""
        self.__create_users_table()
        self.__create_carts_table()
        self.__create_cart_products_table()
        self.__create_categories_table()
        self.__create_products_table()
        self.__create_orders_table()

        self.__database.commit()
        self.__database.close()


class DatabaseTools:
    def __init__(self):
        self.__database, self.__cursor = connect_database()

    def register_user(self, *, full_name: str, chat_id: int) -> None:
        try:
            self.__cursor.execute("""INSERT INTO users (full_name, chat_id)
                VALUES (?, ?)
            """, (full_name, chat_id))
        except Exception as exp:
            if DEBUG:
                print(f"{exp.__class__.__name__}: {exp}")
        else:
            self.__database.commit()
        finally:
            self.__database.close()

    def register_cart(self, *, user_id: int) -> None:
        try:
            self.__cursor.execute("""INSERT INTO carts (user_id)
                VALUES (?)
            """, (user_id,))
        except Exception as exp:
            if DEBUG:
                print(f"{exp.__class__.__name__}: {exp}")
        else:
            self.__database.commit()
        finally:
            self.__database.close()

    def get_cart(self, user_id: int) -> tuple:
        try:
            self.__cursor.execute("""SELECT cart_id, total_price, total_quantity
                FROM carts
                WHERE user_id = ? AND in_order = False
            """, (user_id,))
        except:
            pass

        cart = self.__cursor.fetchone()
        self.__database.close()
        return cart

    def get_user_id(self, chat_id: int) -> int:
        self.__cursor.execute("""SELECT user_id
            FROM users
            WHERE chat_id = ?
        """, (chat_id,))
        user_id = self.__cursor.fetchone()[0]
        self.__database.close()
        return user_id

    def get_cart_id(self, user_id: int) -> int:
        return self.get_cart(user_id)[0]

    def get_categories(self) -> list:
        self.__cursor.execute("""SELECT category_id, name
            FROM categories
        """)
        categories = self.__cursor.fetchall()
        self.__database.close()
        return categories

    def get_products(self, category_id: int) -> list:
        self.__cursor.execute("""SELECT product_id, title
            FROM products
            WHERE category_id = ?
        """, (category_id,))
        products = self.__cursor.fetchall()
        self.__database.close()
        return products

    def get_product(self, product_id: int) -> tuple:
        self.__cursor.execute("""SELECT title, price, preview, ingredients
            FROM products
            WHERE product_id = ?
        """, (product_id,))
        product = self.__cursor.fetchone()
        self.__database.close()
        return product

    def create_cart_product(self, cart_id: int, product_name: str,
                            product_id: int, quantity: int, final_price: float) -> bool:
        edit_status = False
        try:
            # Пытаемся добавить cart_product
            self.__cursor.execute("""INSERT INTO cart_products 
                (cart_id, product_name, product_id, quantity, final_price)
                VALUES (?, ?, ?, ?, ?)
            """, (cart_id, product_name, product_id, quantity, final_price))
        except Exception as exp:
            print(f"{exp.__class__.__name__}: {exp}")
            # Если cart_product существует, обновляем только quantity, final_price
            self.__cursor.execute("""UPDATE cart_products
                SET quantity = ?, final_price = ?
                WHERE cart_id = ? AND product_id = ?
            """, (quantity, final_price, cart_id, product_id))
            edit_status = True
        finally:
            self.__database.commit()
            self.__database.close()
        return edit_status

    def delete_cart_product(self, cart_product_id: int) -> None:
        self.__cursor.execute("""DELETE FROM cart_products
            WHERE cart_product_id = ?
        """, (cart_product_id,))
        self.__database.commit()
        self.__database.close()

    def get_cart_products(self, cart_id: int) -> list:
        """
        Возвращает список товаров, которые принадлежат определённой корзине
        :param cart_id: ID корзины
        :return: cart_product_id, product_name, quantity, final_price
        """
        self.__cursor.execute("""SELECT cart_product_id, product_name, quantity, final_price
            FROM cart_products
            WHERE cart_id = ?
        """, (cart_id,))
        cart_products = self.__cursor.fetchall()
        self.__database.close()
        return cart_products

    def recalc_cart(self, cart_id: int) -> None:
        # Получения cart_products, которые привязанны к определённой корзине
        self.__cursor.execute("""SELECT quantity, final_price
            FROM cart_products
            WHERE cart_id = ?
        """, (cart_id,))
        cart_products = self.__cursor.fetchall()
        quantity = sum([qty[0] for qty in cart_products])
        final_price = sum([price[1] for price in cart_products])

        # Обновление total_price, total_quantity определённой корзины
        self.__cursor.execute("""UPDATE carts
            SET total_price = ?, total_quantity = ?
            WHERE cart_id = ?
        """, (final_price, quantity, cart_id))
        self.__database.commit()
        self.__database.close()

    def get_info_cart(self, cart_id: int) -> tuple:
        """
        Возвращает состояние корзины
        :param cart_id: ID корзины
        :return: total_price, total_quantity
        """
        self.__cursor.execute("""SELECT total_price, total_quantity
            FROM carts
            WHERE cart_id = ?
        """, (cart_id,))
        cart_info = self.__cursor.fetchone()
        self.__database.close()
        return cart_info

    def create_order(self, cart_id: int, user_id: int, create_date: str,
                     total_price: float, total_quantity: int) -> None:
        self.__cursor.execute("""INSERT INTO orders 
            (cart_id, user_id, create_date, total_price, total_quantity)
            VALUES (?, ?, ?, ?, ?)
        """, (cart_id, user_id, create_date, total_price, total_quantity))
        self.__database.commit()
        self.__database.close()

    def get_orders(self, user_id: int) -> list:
        """
        Получить список заказов и названия товаров связанных с этими заказами

        :param user_id: ID пользователя
        :return: order_id, product_name, quantity, final_price, create_date, total_price, total_quantity, pay_status
        """
        self.__cursor.execute("""SELECT order_id, product_name, quantity, final_price, create_date, 
                                        orders.total_price, orders.total_quantity, pay_status
                                FROM orders
                                JOIN carts ON orders.cart_id = carts.cart_id
                                JOIN cart_products ON cart_products.cart_id = carts.cart_id
                                WHERE orders.user_id = ?
                            """, (user_id, ))
        orders = self.__cursor.fetchall()
        self.__database.close()
        return orders

    def cart_in_order(self, cart_id: int) -> None:
        """Добавление корзины в заказ"""
        self.__cursor.execute("""UPDATE carts
            SET in_order = True
            WHERE cart_id = ?
        """, (cart_id,))
        self.__database.commit()
        self.__database.close()

    def order_pay_status(self, order_id: int) -> None:
        """Меняем состояние заказа на "Оплачено" """
        self.__cursor.execute("""UPDATE orders
            SET pay_status = True
            WHERE order_id = ?
        """, (order_id,))
        self.__database.commit()
        self.__database.close()


class InsertData:
    def __init__(self):
        self.__database, self.__cursor = connect_database()

    def __insert_categories(self):
        categories = (
            "Лаваш",
            "Бургеры",
            "Донар",
            "Пицца",
            "Хот-доги",
            "Напитки",
            "Гарниры",
        )
        for category in categories:
            try:
                self.__cursor.execute("""INSERT INTO categories (name)
                    VALUES (?)
                """, (category,))
            except:
                pass
            else:
                self.__database.commit()

    def __insert_products(self):
        products = (
            (1, "Куринный Лаваш", 21000, "media/lavash_1.jpg"),
            (1, "Рыбный Лаваш", 24000, "media/lavash_2.jpg"),
            (3, "Донар", 40000, "media/donar_1.jpg"),
        )
        for product in products:
            try:
                self.__cursor.execute("""INSERT INTO products 
                    (category_id, title, price, preview)
                    VALUES (?, ?, ?, ?)
                """, product)
            except:
                pass
            else:
                self.__database.commit()

    def insert(self):
        self.__insert_categories()
        self.__insert_products()
        self.__database.close()


if __name__ == "__main__":
    InitDB().init()
    InsertData().insert()
