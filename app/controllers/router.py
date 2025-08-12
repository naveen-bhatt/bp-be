"""Central router with all endpoints organized by section."""

from fastapi import FastAPI, APIRouter

from . import auth_controller, product_controller, cart_controller, checkout_controller, oauth_controller
from app.schemas.common import PaginatedResponse
from app.schemas.product import ProductDetail
from app.schemas.auth import AnonymousTokenResponse

# Create main API router
api_router = APIRouter(prefix="/api/v1")

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
api_router.add_api_route('/auth/google/callback', oauth_controller.google_callback, methods=["GET"], tags=["Auth", "OAuth"])

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
api_router.add_api_route('/cart', cart_controller.get_cart, methods=["GET"], tags=["Cart"])
api_router.add_api_route('/cart/summary', cart_controller.get_cart_summary, methods=["GET"], tags=["Cart"])
api_router.add_api_route('/cart/items', cart_controller.add_to_cart, methods=["POST"], tags=["Cart"])
api_router.add_api_route('/cart/items/{item_id}', cart_controller.update_cart_item, methods=["PATCH"], tags=["Cart"])
api_router.add_api_route('/cart/items/{item_id}', cart_controller.remove_cart_item, methods=["DELETE"], tags=["Cart"])
api_router.add_api_route('/cart/merge', cart_controller.merge_guest_cart, methods=["POST"], tags=["Cart"])
api_router.add_api_route('/cart/clear', cart_controller.clear_cart, methods=["POST"], tags=["Cart"])

# =============================================================================
# PAYMENT ENDPOINTS
# =============================================================================
api_router.add_api_route('/checkout/orders', checkout_controller.create_order, methods=["POST"], tags=["Payment"])
api_router.add_api_route('/checkout/orders', checkout_controller.list_orders, methods=["GET"], tags=["Payment"])
api_router.add_api_route('/checkout/orders/{order_id}', checkout_controller.get_order, methods=["GET"], tags=["Payment"])
api_router.add_api_route('/checkout/payment-intent', checkout_controller.create_payment_intent, methods=["POST"], tags=["Payment"])
api_router.add_api_route('/checkout/payments/{payment_id}', checkout_controller.get_payment, methods=["GET"], tags=["Payment"])
api_router.add_api_route('/checkout/payments/{payment_id}/status', checkout_controller.get_payment_status, methods=["GET"], tags=["Payment"])
api_router.add_api_route('/checkout/webhook/stripe', checkout_controller.stripe_webhook, methods=["POST"], tags=["Payment"])
api_router.add_api_route('/checkout/webhook/razorpay', checkout_controller.razorpay_webhook, methods=["POST"], tags=["Payment"])


def include_routes(app: FastAPI) -> None:
    """
    Include all API routes in the FastAPI application.
    
    Args:
        app: FastAPI application instance.
    """
    app.include_router(api_router)