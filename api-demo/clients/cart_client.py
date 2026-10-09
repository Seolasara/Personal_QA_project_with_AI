import httpx

class CartClient:
    def __init__(self, client: httpx.Client):
        self.client = client

    def create_cart(self, body=None):
        if body is None:
            return self.client.post("/carts")
        return self.client.post("/carts", json=body)

    def get_cart(self, cart_id):
        response = self.client.get(f"/carts/{cart_id}")
        return response

    def add_item(self, cart_id, product_id, quantity):
        response = self.client.post(f"/carts/{cart_id}", json={"product_id": product_id, "quantity": quantity})
        return response

    def update_quantity(self, cart_id, product_id, quantity):
        response = self.client.put(f"/carts/{cart_id}/product/quantity", json={"product_id":product_id, "quantity":quantity})
        return response

    def remove_item(self, cart_id, product_id):
        response = self.client.delete(f"/carts/{cart_id}/product/{product_id}")
        return response

    def delete_cart(self, cart_id):
        response = self.client.delete(f"/carts/{cart_id}")
        return response

    def add_item_raw(self, cart_id, body):
        return self.client.post(f"/carts/{cart_id}", json=body)

    def update_quantity_raw(self, cart_id, body):
        return self.client.put(f"/carts/{cart_id}/product/quantity", json=body)
