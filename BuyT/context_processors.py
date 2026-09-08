from .models import Wishlist


def wishlist_count(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return {
            "wishlist_count": 0
        }

    count = Wishlist.objects.filter(
        user_id=user_id
    ).count()

    return {
        "wishlist_count": count
    }