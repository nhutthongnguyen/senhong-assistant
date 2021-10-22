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


api = API(

    url='https://nongsandongthap.000webhostapp.com/',
    consumer_key='ck_e3bee011df97a906fc332eaea7dd4094f543b4bb',
    consumer_secret='cs_3f1e29b028f404d65dda908d7be6b4b0d4cb000d',
    version='wc/v3'
)

def create_carousel(products):
    elements = []
    for product in products:
        image = product['images'][0]['src']
        elements.append({
            "id": product['id'],
            "title": product['name'],
            "subtitle": f'Price: {product["price"]}',
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

        dispatcher.utter_message("Đây là danh mục sản phẩm của Sen Hồng, bạn muốn mua loại sản phẩm nào?", buttons=buttons)
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
        slug = ""
        name_category = ""

        list_slug = []

        entities = tracker.latest_message['entities']
        for entity in entities:
            slug = entity['value']
            if slug == 'đặc sản':
                category_id = 21
                slug = 'dac-san'
                name_category = 'Đặc sản'
                list_slug.append(slug)

            if slug == 'trái cây' or slug == 'cây':
                category_id = 22
                slug = 'trai-cay'
                name_category = 'Trái cây'
                list_slug.append(slug)

            if slug == 'rau củ quả' or slug == 'rau' or slug == 'rau củ':
                category_id = 23
                slug = 'rau-cu-qua'
                name_category = 'Rau củ quả'
                list_slug.append(slug)

            if slug == 'gạo':
                category_id = 24
                slug = 'gao'
                name_category = 'Gạo'
                list_slug.append(slug)

            print(list_slug)
            print("slug = ", slug, " va category_id = ", category_id)
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

class ActionShowTime(Action):
    def name(self) -> Text:
        return 'action_show_time'

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=f"Bây giờ là {dt.datetime.now()}")

        return []

