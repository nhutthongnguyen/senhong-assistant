# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import datetime as dt
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
from woocommerce import API




def create_carousel(products):
    elements = []
    for product in products:
        image = product['images'][0]['src']
        elements.append({
            "id": product['id'],
            "title": product['name'],
            "subtitle": f'Giá: {product["price"]}',
            "price": product['price'],
            "regular_price": product["regular_price"],
            "sale_price": product["sale_price"],
            "image_url": image,
            "description": product['description'],
            "short_description": product['short_description'],
            "buttons": [
                {"title": "Xem chi tiết", "url": product['permalink'], "type": "web_url"},
                {"title": "Thêm vào giỏ hàng", "url": f"{product['permalink']}?add-to-cart={product['id']}",
                 "type": "web_url", "target": "_self"},
                {"title": "Sản phẩm khác", "type": "postback", "payload": '/show_products_categories'}
            ]
        })

    carousel = {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": elements}
    }
    return carousel


class ShowProductCategories(Action):
    def name(self) -> Text:
        return "action_show_products_categories"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        categories = api.get('products/categories').json()

        print("DAY LA DANH MUC SAN PHAM KHAC")
        buttons = []
        for category in categories:
            category_id = category['id']
            category_name = category['name']

            buttons.append({
                "title": category_name,
                "category_id": category_id,
                "payload": f'/show_products{{"category_id": {category_id}}}'
            })
        dispatcher.utter_message("Đây là danh mục sản phẩm của Sen Hồng, bạn muốn mua loại sản phẩm nào ạ?", buttons=buttons)
        return [AllSlotsReset()]


class ShowProducts(Action):
    def name(self) -> Text:
        return "action_show_products"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        text = tracker.latest_message.get('text')
        print("TEXT = ", text)
        category_id = tracker.get_slot("category_id")
        print("CATEGORY_ID = ", category_id)
        category = api.get(f"products/categories/{category_id}").json()
        products = api.get(f"products?category={category_id}").json()
        carousel = create_carousel(products)
        dispatcher.utter_message(text=f"Mời quý khách xem qua các sản phẩm thuộc loại {category['name']} ", attachment=carousel)
        return []


##########################

class SearchProduct(Action):
    def name(self) -> Text:
        return 'action_show_intent_categories'

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        category_id = 0
        name_category = ""

        entity = next(tracker.get_latest_entity_values("slug"), None)
        print("TEXT SEARCH ", entity.lower())
        entity = entity.lower()
        entity = entity.strip()

        if entity == "đặc sản" or entity == "dac san":
            name_category = "Đặc sản"
            category_id = 21
        
        if entity == "trái cây" or entity == "trai cay":
            name_category = "Trái cây"
            category_id = 22

        if entity == "rau củ quả" or entity == "rau" or entity == "củ quả":
            name_category = "Rau củ quả"
            category_id = 23

        if entity == "gạo" or entity == "gao":
            name_category = "Gạo"
            category_id == 24



        print("slug=", name_category, " va category_id=", category_id)
        products = api.get(f"products?category={category_id}").json()
        carousel = create_carousel(products)
        dispatcher.utter_message(text=f"Sản phẩm {name_category} mà bạn cần tìm ", attachment=carousel)

        return []


class ShowSaleProducts(Action):
    def name(self) -> Text:
        return 'action_show_sale_products'

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        text = tracker.latest_message.get('text')
        print("TEXT SALE = ", text)
        products = api.get('products?per_page=100&').json()
        sale_products = list(filter(lambda product: product['on_sale'], products))

        carousel = create_carousel(sale_products)
        dispatcher.utter_message(text="Sen Hồng hiện đang có các sản phẩm khuyến mãi như sau", attachment=carousel)

        return []

class ShowShippingMethods(Action):
    def name(self) -> Text:
        return 'action_show_shipping_methods'
    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        shipping_methods = api.get('shipping_methods').json()
        print(shipping_methods)
        message = ""
        count = 0

        for method in shipping_methods:
            message = message + method['title'] + ", "
            count = count + 1

        dispatcher.utter_message(text=f"Hiện tại cửa hàng có {count} phương thức giao hàng như: {message}")

        return []

class ShowPaymentGateways(Action):
    def name(self) -> Text:
        return 'action_show_payment_gateways'

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        payment_gateways = api.get('payment_gateways').json()

        num_methods = 0
        gateways = ""

        for method in payment_gateways:
            gateways = gateways + method['title'] + ", "
            num_methods = num_methods + 1

        dispatcher.utter_message(text=f"Hiện tại cửa hàng có {num_methods} thanh toán như: {gateways}")

        return []

