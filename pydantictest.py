import requests
from rich.console import Console
from pydantic import BaseModel, field_validator, ValidationError

console = Console() 

def get_data():
    resp = requests.get("https://allbirds.co.uk/products.json")
    if resp.status_code == 200:
        return resp.json()["products"]
    else:
        raise Exception("Failed to fetch products")

class Variant(BaseModel):
    title: str
    sku: str 
    price: str
    grams: int

    @field_validator('sku')
    def check_sku_len(cls, value):
        required_length = 10
        if len(value) != required_length: 
            raise ValueError("SKU must be 10 chars long")
        return value
    
    @field_validator('sku')
    def check_sku_even_digits(cls, value):
        # Conta o número de dígitos numéricos no SKU
        digit_count = sum(c.isdigit() for c in value)
        # Verifica se o número de dígitos numéricos é par
        if digit_count % 2 != 0: 
            raise ValueError("SKU must have an even number of digits")
        return value


class Product(BaseModel):
    id: int
    title: str
    variants: list[Variant]

def main():
    products_data = get_data()
    valid_products = []
    valid_products_count = 0
    invalid_products_count = 0
    for product_data in products_data:
        try:
            product = Product(**product_data)
            valid_products.append(product.model_dump())
            console.print(product.model_dump())
            valid_products_count += 1
        except ValidationError as e:
            for error in e.errors():
                invalid_products_count += 1
                error_message = f"Error in product {product_data.get('id', 'Unknown')} - " \
                                f"Field: {' -> '.join(map(str, error['loc']))}, " \
                                f"Error: {error['msg']}, " \
                                f"Value: {error.get('input', 'N/A')}"
                console.print(error_message, style="red")

    console.print(f"Total valid products: {valid_products_count}", style="green")
    console.print(f"Total invalid products: {invalid_products_count}", style="red")

if __name__ == "__main__":
    products = get_data()
    valid_products = []
    main()
