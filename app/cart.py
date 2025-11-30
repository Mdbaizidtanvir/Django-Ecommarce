# cart.py
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart
        self.discount = self.session.get("discount", 0)

        # 🔧 Fix any legacy/broken values sitting in the session
        self._repair_legacy_items()

    def _to_float(self, v, fallback=0.0):
        try:
            if callable(v):
                v = v()
            return float(v)
        except Exception:
            return float(fallback)

    def _repair_legacy_items(self):
        changed = False
        for pid, item in list(self.cart.items()):
            # price
            price = item.get("price", 0)
            new_price = self._to_float(price, fallback=item.get("original_price", 0))
            if new_price != price:
                item["price"] = new_price
                changed = True

            # original_price
            original_price = item.get("original_price", 0)
            new_original = self._to_float(original_price, fallback=new_price)
            if new_original != original_price:
                item["original_price"] = new_original
                changed = True

            # quantity
            try:
                item["quantity"] = int(item.get("quantity", 1))
            except Exception:
                item["quantity"] = 1
                changed = True

            # offer
            try:
                item["offer"] = int(item.get("offer", 0) or 0)
            except Exception:
                item["offer"] = 0
                changed = True

            self.cart[pid] = item

        if changed:
            self.save()

    def add(self, product, quantity=1, size=None, color=None):
        product_id = str(product.id)
        final_price = product.get_final_price()  # ✅ discounted price
        original_price = product.price  # original
        
        if product_id in self.cart:
            self.cart[product_id]["quantity"] += quantity


        else:
            self.cart[product_id] = {
                "name": product.name,
                "original_price": float(product.price),                # ✅ numeric
                "price": str(final_price),            # ✅ numeric (call the method)
                "offer": int(product.discount_percentage or 0),
                "image": product.main_image.url if product.main_image else "",
                "quantity": int(quantity),
                "size": size or "",
                "color": color or "",
            }
        self.save()

    def apply_discount(self, discount_percentage):
        self.discount = discount_percentage
        self.session["discount"] = discount_percentage
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session["cart"] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def get_items(self):
        # Return normalized items (already repaired in __init__)
        return self.cart.items()
    
    
    def get_total_price(self):
        total = sum(float(item["price"]) * item["quantity"] for item in self.cart.values())
        if self.discount:
            total = total * (1 - self.discount / 100)
        return total


    def update(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            q = int(quantity)
            if q > 0:
                self.cart[product_id]["quantity"] = q
            else:
                del self.cart[product_id]
            self.save()
