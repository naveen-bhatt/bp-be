"""Cart repository for database operations."""

from typing import Optional, List
from decimal import Decimal
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_

from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.core.logging import get_logger

logger = get_logger(__name__)


class CartRepository:
    """Repository for Cart and CartItem model database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session.
        """
        self.db = db
    
    def create_cart(self, user_id: Optional[str] = None, cart_token: Optional[str] = None) -> Cart:
        """
        Create a new cart.
        
        Args:
            user_id: User ID for authenticated carts.
            cart_token: Cart token for guest carts.
            
        Returns:
            Cart: Created cart instance.
        """
        cart = Cart(user_id=user_id, cart_token=cart_token)
        
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        
        identifier = f"user {user_id}" if user_id else f"guest {cart_token}"
        logger.info(f"Created cart for {identifier}")
        return cart
    
    def get_cart_by_id(self, cart_id: str) -> Optional[Cart]:
        """
        Get cart by ID with items loaded.
        
        Args:
            cart_id: Cart ID to search for.
            
        Returns:
            Optional[Cart]: Cart if found, None otherwise.
        """
        return self.db.query(Cart).options(
            selectinload(Cart.items).selectinload(CartItem.product)
        ).filter(Cart.id == cart_id).first()
    
    def get_cart_by_user(self, user_id: str) -> Optional[Cart]:
        """
        Get active cart for a user.
        
        Args:
            user_id: User ID to search for.
            
        Returns:
            Optional[Cart]: User's cart if found, None otherwise.
        """
        return self.db.query(Cart).options(
            selectinload(Cart.items).selectinload(CartItem.product)
        ).filter(Cart.user_id == user_id).first()
    
    def get_cart_by_token(self, cart_token: str) -> Optional[Cart]:
        """
        Get cart by cart token (for guest carts).
        
        Args:
            cart_token: Cart token to search for.
            
        Returns:
            Optional[Cart]: Cart if found, None otherwise.
        """
        return self.db.query(Cart).options(
            selectinload(Cart.items).selectinload(CartItem.product)
        ).filter(Cart.cart_token == cart_token).first()
    
    def get_or_create_cart(
        self,
        user_id: Optional[str] = None,
        cart_token: Optional[str] = None
    ) -> Cart:
        """
        Get existing cart or create new one.
        
        Args:
            user_id: User ID for authenticated carts.
            cart_token: Cart token for guest carts.
            
        Returns:
            Cart: Existing or newly created cart.
        """
        if user_id:
            cart = self.get_cart_by_user(user_id)
        elif cart_token:
            cart = self.get_cart_by_token(cart_token)
        else:
            cart = None
        
        if not cart:
            cart = self.create_cart(user_id=user_id, cart_token=cart_token)
        
        return cart
    
    def add_item(
        self,
        cart: Cart,
        product_id: str,
        quantity: int,
        unit_price: Decimal
    ) -> CartItem:
        """
        Add item to cart or update quantity if exists.
        
        Args:
            cart: Cart to add item to.
            product_id: Product ID to add.
            quantity: Quantity to add.
            unit_price: Price per unit.
            
        Returns:
            CartItem: Created or updated cart item.
        """
        # Check if item already exists in cart
        existing_item = self.db.query(CartItem).filter(
            and_(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id
            )
        ).first()
        
        if existing_item:
            # Update existing item
            existing_item.quantity += quantity
            existing_item.unit_price = unit_price  # Update price in case it changed
            self.db.commit()
            self.db.refresh(existing_item)
            
            logger.info(f"Updated cart item: product {product_id}, new qty {existing_item.quantity}")
            return existing_item
        else:
            # Create new item
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price
            )
            
            self.db.add(cart_item)
            self.db.commit()
            self.db.refresh(cart_item)
            
            logger.info(f"Added cart item: product {product_id}, qty {quantity}")
            return cart_item
    
    def update_item_quantity(self, cart_item: CartItem, new_quantity: int) -> CartItem:
        """
        Update cart item quantity.
        
        Args:
            cart_item: Cart item to update.
            new_quantity: New quantity.
            
        Returns:
            CartItem: Updated cart item.
        """
        cart_item.quantity = new_quantity
        self.db.commit()
        self.db.refresh(cart_item)
        
        logger.info(f"Updated cart item quantity: {cart_item.product_id}, qty {new_quantity}")
        return cart_item
    
    def remove_item(self, cart_item: CartItem) -> None:
        """
        Remove item from cart.
        
        Args:
            cart_item: Cart item to remove.
        """
        product_id = cart_item.product_id
        self.db.delete(cart_item)
        self.db.commit()
        
        logger.info(f"Removed cart item: product {product_id}")
    
    def get_cart_item(self, cart_id: str, product_id: str) -> Optional[CartItem]:
        """
        Get specific cart item.
        
        Args:
            cart_id: Cart ID.
            product_id: Product ID.
            
        Returns:
            Optional[CartItem]: Cart item if found, None otherwise.
        """
        return self.db.query(CartItem).filter(
            and_(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id
            )
        ).first()
    
    def clear_cart(self, cart: Cart) -> None:
        """
        Remove all items from cart.
        
        Args:
            cart: Cart to clear.
        """
        self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        self.db.commit()
        
        logger.info(f"Cleared cart: {cart.id}")
    
    def delete_cart(self, cart: Cart) -> None:
        """
        Delete cart and all its items.
        
        Args:
            cart: Cart to delete.
        """
        cart_id = cart.id
        self.db.delete(cart)
        self.db.commit()
        
        logger.info(f"Deleted cart: {cart_id}")
    
    def calculate_cart_totals(self, cart: Cart) -> dict:
        """
        Calculate cart totals.
        
        Args:
            cart: Cart to calculate totals for.
            
        Returns:
            dict: Dictionary with total_amount, total_items, and currency.
        """
        total_amount = Decimal('0.00')
        total_items = 0
        currency = "USD"  # Default currency
        
        for item in cart.items:
            total_amount += item.subtotal
            total_items += item.quantity
            if item.product and item.product.currency:
                currency = item.product.currency
        
        return {
            "total_amount": total_amount,
            "total_items": total_items,
            "currency": currency
        }
    
    def merge_carts(self, source_cart: Cart, target_cart: Cart) -> Cart:
        """
        Merge source cart into target cart (e.g., guest cart to user cart on login).
        
        Args:
            source_cart: Cart to merge from.
            target_cart: Cart to merge into.
            
        Returns:
            Cart: Updated target cart.
        """
        for source_item in source_cart.items:
            # Check if target cart already has this product
            target_item = self.get_cart_item(target_cart.id, source_item.product_id)
            
            if target_item:
                # Merge quantities
                target_item.quantity += source_item.quantity
                # Update price to latest
                target_item.unit_price = source_item.unit_price
            else:
                # Move item to target cart
                source_item.cart_id = target_cart.id
        
        # Delete source cart
        self.delete_cart(source_cart)
        
        self.db.commit()
        self.db.refresh(target_cart)
        
        logger.info(f"Merged cart {source_cart.id} into {target_cart.id}")
        return target_cart