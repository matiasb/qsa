from __future__ import unicode_literals

from django import template

register = template.Library()


@register.inclusion_tag('qsaui/_rating.html')
def rating_as_stars(item, max_rating=10):
    if item.rating is None:
        return

    rating = item.rating
    assert 0 <= rating and rating <= max_rating

    stars = [True if i <= round(rating) else False
             for i in range(1, max_rating + 1)]

    return dict(stars=stars, rating=rating, rating_count=item.rating_count)
