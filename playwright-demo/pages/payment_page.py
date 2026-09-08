class PaymentPage:
    def __init__(self, page):
        self.page = page

        # cart
        self.product = page.locator('[data-test=product-quantity]')
        self.button1 = page.get_by_role("button", name="Proceed to checkout")

        # sign in
        self.button2 = page.get_by_role("button", name="Proceed to checkout")
        self.confirmation = page.get_by_text("you are already logged in. You can proceed to checkout.")

        # billing address 
        self.address = page.get_by_role("heading", name="Billing Address", level=3)
        self.dropdown1 = page.get_by_role("combobox")
        self.postcode = page.get_by_placeholder("Your Postcode *")
        self.house = page.get_by_placeholder("e.g. 42 *")
        self.street = page.get_by_placeholder("Your Street *")
        self.city = page.get_by_placeholder("Your City *")
        self.state = page.get_by_placeholder("State *")
        self.button3 = page.get_by_role("button", name="Proceed to checkout")

        # payment
        self.dropdown2 = page.locator('[data-test="payment-method"]')
        self.confirm = page.get_by_role("button", name="Confirm")
        self.message = page.get_by_text("Payment was successful")


    def cart_step(self):
        self.button1.click()

    def signin_step(self):
        self.button2.click()

    def filling_address(self, method, postcode, house, street, city, state):
        self.dropdown1.select_option(label=method)
        self.postcode.fill(postcode)
        self.house.fill(house)
        self.street.fill(street)
        self.city.fill(city)
        self.city.fill(state)

    def address_step(self):
        self.button3.click()

    def payment_step(self, method):
        self.dropdown2.select_option(label=method)

    def confirm_button(self):
        self.confirm.click()