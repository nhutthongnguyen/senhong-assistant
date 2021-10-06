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

    url='http://localhost/senhong',
    consumer_key='ck_5c04af2c04a32341677f9ae6797ee25f35211908',
    consumer_secret='cs_4d71ab59e2156249f483081bf1d62c9247a27823',
    version='wc/v3'
)

def create_carousel(products):
    elements = []
    for product in products:
        image = product['images'][0]['src']
        elements.append({
            "title": product['name'],
            "subtitle": f'Price: {product["price"]}',
            "image_url": image,
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

        buttons = []
        for category in categories:
            category_id = category['id']
            category_name = category['name']
            # if category_name == 'Glasshouse':
            #     continue
            buttons.append({
                "title": category_name,
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
        dispatcher.utter_message(text=f"Mời bạn xem qua các sản phẩm thuộc loại {category['name']} bên dưới. Để mua sản phẩm khách hàng vui lòng"
                                      f"chọn thêm vào giỏ hàng và điền đầy đủ thông tin để tiến hành thanh toán", attachment=carousel)
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

        entities = tracker.latest_message['entities']
        categories = api.get('products/categories').json()
        print('ENTITIES ', entities)
        name_category = ""
        slug = ""
        category_id = 0

        for e in entities:
            if e['entity'] == 'slug':
                category = e['value']
            if category == 'trái cây':
               slug = 'trai-cay'
               name_category = category

            if category == 'rau củ quả' or category == 'rau':
                slug = 'rau-cu'
                message = name_category

            if category == 'đặc sản':
                slug = 'dac-san'
                name_category = category


        for category in categories:
            if category['slug'] == slug:
                category_id = category['id']
                print('CATEGORY ID IN SEARCH ', slug)

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

        for sale in sale_products:
            print(sale['id'])

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
        message = ""
        count = 0

        for method in shipping_methods:
            message = message + method['title'] + ", "
            count = count + 1

        print('SAY HELLO')

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
