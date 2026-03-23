from fastapi import FastAPI, Query
from typing import Optional
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the Product API!"}

#---------------------------------------------Day 1-----------------------------------------------

#--------------------------------------------- Q 1 -----------------------------------------------
products = [
    {"id": 1, "name": "Smartphone", "price": 15000, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Headphones", "price": 2000, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},

    {"id": 5, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 6, "name": "Pen Pack", "price": 149, "category": "Stationery", "in_stock": True},
    {"id": 7, "name": "Marker Set", "price": 199, "category": "Stationery", "in_stock": False},
]

@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }

#--------------------------------------------- Q 2 -----------------------------------------------
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    result = [p for p in products if p["category"] == category_name]

    if not result:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": result,
        "total": len(result)
    }

#--------------------------------------------- Q 3 -----------------------------------------------
@app.get("/products/instock")
def get_instock():
    available = [p for p in products if p["in_stock"] == True]

    return {
        "in_stock_products": available,
        "count": len(available)
    }

#--------------------------------------------- Q 4 -----------------------------------------------
@app.get("/store/summary")
def store_summary():
    in_stock_count = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count
    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": categories
    }

#--------------------------------------------- Q 5 -----------------------------------------------
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": "No products matched your search"}

    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }

#----------------------------------------- Bonus Question -------------------------------------------
@app.get("/products/deals")
def get_deals():
    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }


#---------------------------------------------Day 2-----------------------------------------------

#--------------------------------------------- Q 1 -----------------------------------------------
@app.get("/products/filter")
def filter_products(
    category: str = Query(None),
    max_price: int = Query(None),
    min_price: int = Query(None, description="Minimum price")
):
    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    return {
        "filtered_products": result,
        "total": len(result)
    }

#--------------------------------------------- Q 2 -----------------------------------------------
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}

#--------------------------------------------- Q 3 -----------------------------------------------
feedback = []

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback)
    }

#--------------------------------------------- Q 4 -----------------------------------------------
@app.get("/products/summary")
def product_summary():
    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {
            "name": expensive["name"],
            "price": expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }

#--------------------------------------------- Q 5 -----------------------------------------------
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
        elif not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal

            confirmed.append({
                "product": product["name"],
                "qty": item.quantity,
                "subtotal": subtotal
            })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

#----------------------------------------- Bonus Question -------------------------------------------
orders = []
class OrderRequest(BaseModel):
    product_id: int
    quantity: int

@app.post("/orders")
def place_order(order: OrderRequest):
    product = next((p for p in products if p["id"] == order.product_id), None)

    if not product:
        return {"error": "Product not found"}
    
    if not product["in_stock"]:
        return {"error": f"{product['name']} is out of stock"}
    
    new_order = {
        "order_id": len(orders) + 1,
        "product": product["name"],
        "quantity": order.quantity,
        "total_price": product["price"] * order.quantity,
        "status": "pending"   # IMPORTANT CHANGE
    }
    orders.append(new_order)

    return {
        "message": "Order placed successfully",
        "order": new_order
    }

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}

    return {"error": "Order not found"}

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"

            return {
                "message": "Order confirmed",
                "order": order
            }

    return {"error": "Order not found"}

#---------------------------------------------Day 3-----------------------------------------------

#--------------------------------------------- Q 1 -----------------------------------------------
from fastapi import HTTPException, status, Response

class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


@app.post("/products", status_code=status.HTTP_201_CREATED)
def add_product(product: NewProduct):

    # check duplicate name
    for p in products:
        if p["name"].lower() == product.name.lower():
            raise HTTPException(
                status_code=400,
                detail="Product with this name already exists"
            )

    # correct ID generation
    new_id = max(p["id"] for p in products) + 1 if products else 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {
        "message": "Product added",
        "product": new_product
    }

#----------------------------------------- Bonus Question -------------------------------------------
from fastapi import Query

@app.put("/products/discount")
def bulk_discount(
    category: str = Query(..., description="Category to discount"),
    discount_percent: int = Query(..., ge=1, le=99, description="Discount percent")
):

    updated = []

    for p in products:

        # case-insensitive category match
        if p["category"].lower() == category.lower():

            # apply discount
            new_price = int(p["price"] * (1 - discount_percent / 100))

            p["price"] = new_price

            updated.append({
                "id": p["id"],
                "name": p["name"],
                "new_price": new_price
            })

    if not updated:
        return {
            "message": f"No products found in category: {category}"
        }

    return {
        "message": f"{discount_percent}% discount applied to {category}",
        "updated_count": len(updated),
        "updated_products": updated
    }

#--------------------------------------------- Q 5 -----------------------------------------------
@app.get("/products/audit")
def product_audit():

    # products in stock
    in_stock_list = [p for p in products if p["in_stock"]]

    # products out of stock
    out_stock_list = [p for p in products if not p["in_stock"]]

    # total inventory value (assuming 10 units each)
    stock_value = sum(p["price"] * 10 for p in in_stock_list)

    # most expensive product
    priciest = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive": {
            "name": priciest["name"],
            "price": priciest["price"]
        }
    }

#--------------------------------------------- Q 2 -----------------------------------------------
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    price: int = Query(None, gt=0),
    in_stock: bool = Query(None)
):

    for product in products:
        if product["id"] == product_id:

            # update price if provided
            if price is not None:
                product["price"] = price

            # update stock if provided
            if in_stock is not None:
                product["in_stock"] = in_stock

            return {
                "message": "Product updated",
                "product": product
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )

#--------------------------------------------- Q 3 -----------------------------------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):

    # find product
    for product in products:
        if product["id"] == product_id:

            # remove product
            products.remove(product)

            return {
                "message": f"Product '{product['name']}' deleted"
            }

    # product not found
    response.status_code = status.HTTP_404_NOT_FOUND

    return {
        "error": "Product not found"
    }

