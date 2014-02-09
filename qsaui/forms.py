from django import forms

from tvdbpy import TvDB


UPDATE_CHOICES = [
    (TvDB.DAY, 'Last day'),
    (TvDB.WEEK, 'Last week'),
    (TvDB.MONTH, 'Last month'),
    (TvDB.ALL, 'All'),
]


class UpdateCatalogueForm(forms.Form):

    period = forms.ChoiceField(
        required=True, choices=UPDATE_CHOICES, initial=TvDB.WEEK)
