from django.dispatch import Signal

# Signals that a model has completed its clean() method
post_clean = Signal()

# Sent after objects of a given model are created via raw save.
# Provides pks (list) of the created objects.
post_raw_create = Signal()
