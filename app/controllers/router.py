"""Central router with all endpoints organized by section."""

from email.headerregistry import Address
from typing import List
from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse

from . import auth_controller, product_controller, cart_controller, checkout_controller, oauth_controller, wishlist_controller, address_controller, admin_controller
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.product import ProductDetail
from app.schemas.auth import AnonymousTokenResponse, GoogleOneTapResponse
from app.schemas.cart import CartPublic, CartSummary
from app.schemas.wishlist import WishlistResponse
from app.schemas.address import AddressListResponse, Address
from app.schemas.order import OrderSummary, OrderListResponse
from app.schemas.admin import (
    AdminOrderListResponse, BulkShipResponse, OrderCancelResponse, 
    ShippedOrdersAddressList, AdminStats
)

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Add OPTIONS handler for CORS preflight requests
@api_router.options("/{path:path}")
async def options_handler():
    """Handle OPTIONS requests for CORS preflight."""
    return {"message": "OK"}

# =============================================================================
# AUTH ENDPOINTS
# =============================================================================
api_router.add_api_route('/auth/anonymous', auth_controller.create_anonymous_user, methods=["POST"], tags=["Auth"], response_model=AnonymousTokenResponse)
api_router.add_api_route('/auth/register', auth_controller.register, methods=["POST"], tags=["Auth"])
api_router.add_api_route('/auth/login', auth_controller.login, methods=["POST"], tags=["Auth"])
api_router.add_api_route('/auth/refresh', auth_controller.refresh_token, methods=["POST"], tags=["Auth"])
api_router.add_api_route('/auth/social', auth_controller.social_login, methods=["POST"], tags=["Auth"])
api_router.add_api_route('/auth/me', auth_controller.get_current_user, methods=["GET"], tags=["Auth"])
api_router.add_api_route('/auth/logout', auth_controller.logout, methods=["POST"], tags=["Auth"])

# Google OAuth endpoints
api_router.add_api_route('/auth/google/start', oauth_controller.google_start, methods=["GET"], tags=["Auth", "OAuth"])
api_router.add_api_route('/auth/google/callback', oauth_controller.google_callback, methods=["GET"], tags=["Auth", "OAuth"], response_class=RedirectResponse)
api_router.add_api_route('/auth/google/one-tap', oauth_controller.google_one_tap, methods=["POST"], tags=["Auth", "OAuth"], response_model=GoogleOneTapResponse)

# =============================================================================
# PRODUCT ENDPOINTS
# =============================================================================
api_router.add_api_route('/products', product_controller.list_products, methods=["GET"], tags=["Products"], response_model=PaginatedResponse)
api_router.add_api_route('/products/{slug}', product_controller.get_product_by_slug, methods=["GET"], tags=["Products"], response_model=ProductDetail)
api_router.add_api_route('/products', product_controller.create_product, methods=["POST"], tags=["Products"])
api_router.add_api_route('/products/{product_id}', product_controller.update_product, methods=["PUT"], tags=["Products"])
api_router.add_api_route('/products/{product_id}/stock', product_controller.update_product_stock, methods=["PATCH"], tags=["Products"])
api_router.add_api_route('/products/{product_id}', product_controller.delete_product, methods=["DELETE"], tags=["Products"])

# =============================================================================
# CART ENDPOINTS
# =============================================================================
api_router.add_api_route('/cart', cart_controller.get_cart, methods=["GET"], tags=["Cart"], response_model=CartPublic)
# api_router.add_api_route('/cart/summary', cart_controller.get_cart_summary, methods=["GET"], tags=["Cart"], response_model=CartSummary)
api_router.add_api_route('/cart/items', cart_controller.add_to_cart, methods=["POST"], tags=["Cart"], response_model=CartPublic)
api_router.add_api_route('/cart/items/{product_id}', cart_controller.update_cart_item, methods=["PATCH"], tags=["Cart"], response_model=CartPublic)
api_router.add_api_route('/cart/items/{product_id}', cart_controller.remove_cart_item, methods=["DELETE"], tags=["Cart"], response_model=CartPublic)
api_router.add_api_route('/cart/items/{product_id}/clear', cart_controller.clear_a_product_from_cart, methods=["DELETE"], tags=["Cart"], response_model=CartPublic)
# api_router.add_api_route('/cart/clear', cart_controller.clear_cart, methods=["POST"], tags=["Cart"], response_model=SuccessResponse)

# =============================================================================
# WISHLIST ENDPOINTS
# =============================================================================
api_router.add_api_route('/wishlist', wishlist_controller.get_wishlist, methods=["GET"], tags=["Wishlist"], response_model=WishlistResponse)
api_router.add_api_route('/wishlist/items/{product_id}', wishlist_controller.toggle_wishlist, methods=["PATCH"], tags=["Wishlist"], response_model=WishlistResponse)
# api_router.add_api_route('/wishlist/clear', wishlist_controller.clear_wishlist, methods=["POST"], tags=["Wishlist"], response_model=SuccessResponse)

# =============================================================================
# ADDRESS ENDPOINTS
# =============================================================================
api_router.add_api_route('/addresses', address_controller.list_addresses, methods=["GET"], tags=["Address"], response_model=AddressListResponse)
api_router.add_api_route('/addresses', address_controller.create_address, methods=["POST"], tags=["Address"], response_model=Address)
api_router.add_api_route('/addresses/{address_id}', address_controller.get_address, methods=["GET"], tags=["Address"], response_model=Address)
api_router.add_api_route('/addresses/{address_id}', address_controller.update_address, methods=["PUT"], tags=["Address"], response_model=Address)
api_router.add_api_route('/addresses/{address_id}', address_controller.delete_address, methods=["DELETE"], tags=["Address"], response_model=SuccessResponse)


# =============================================================================
# PAYMENT ENDPOINTS
# =============================================================================
api_router.add_api_route('/checkout/orders', checkout_controller.create_order, methods=["POST"], tags=["Payment"], response_model=OrderSummary)
api_router.add_api_route('/checkout/orders', checkout_controller.list_orders, methods=["GET"], tags=["Payment"], response_model=OrderListResponse)
api_router.add_api_route('/checkout/orders/{order_id}', checkout_controller.get_order, methods=["GET"], tags=["Payment"], response_model=OrderSummary)
api_router.add_api_route('/checkout/payment-intent', checkout_controller.create_payment_intent, methods=["POST"], tags=["Payment"])
api_router.add_api_route('/checkout/payments/{payment_id}', checkout_controller.get_payment, methods=["GET"], tags=["Payment"])
api_router.add_api_route('/checkout/payments/{payment_id}/status', checkout_controller.get_payment_status, methods=["GET"], tags=["Payment"])
api_router.add_api_route('/checkout/webhook/stripe', checkout_controller.stripe_webhook, methods=["POST"], tags=["Payment"])
api_router.add_api_route('/checkout/webhook/razorpay', checkout_controller.razorpay_webhook, methods=["POST"], tags=["Payment"])


# =============================================================================
# ADMIN ENDPOINTS (Admin/Superadmin only)
# =============================================================================
api_router.add_api_route('/admin/orders', admin_controller.get_recent_orders, methods=["GET"], tags=["Admin"], response_model=AdminOrderListResponse)
api_router.add_api_route('/admin/orders/bulk-ship', admin_controller.bulk_ship_orders, methods=["POST"], tags=["Admin"], response_model=BulkShipResponse)
api_router.add_api_route('/admin/orders/{order_id}/cancel', admin_controller.cancel_order, methods=["POST"], tags=["Admin"], response_model=OrderCancelResponse)
api_router.add_api_route('/admin/orders/shipped', admin_controller.get_shipped_orders, methods=["GET"], tags=["Admin"], response_model=List[OrderSummary])
api_router.add_api_route('/admin/orders/shipped/addresses', admin_controller.generate_shipped_orders_address_pdf, methods=["GET"], tags=["Admin"], response_model=ShippedOrdersAddressList)
api_router.add_api_route('/admin/stats', admin_controller.get_admin_stats, methods=["GET"], tags=["Admin"], response_model=AdminStats)


def include_routes(app: FastAPI) -> None:
    """
    Include all API routes in the FastAPI application.
    
    Args:
        app: FastAPI application instance.
    """
    app.include_router(api_router)