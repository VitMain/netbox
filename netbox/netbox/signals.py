from django.dispatch import Signal

# Signals that a model has completed its clean() method
post_clean = Signal()

# Sent after objects of a given model are created via raw save.
# Expected call signature: post_raw_create.send(sender=MyModel, pks=[...])
# Provides: pks (list) - PKs of the newly created objects.
post_raw_create = Signal()
