from django.dispatch import Signal

# Signals that a model has completed its clean() method
post_clean = Signal()

# Sent after objects of a given model are created via raw save.
# Expected call signature: post_raw_create.send(sender=MyModel, pks=[...])
# Provides: pks (list) - PKs of the newly created objects.
# Callers must ensure all related objects (e.g. M2M, dependent rows) are in place
# before sending, as receivers may query related data to perform post-create work.
post_raw_create = Signal()
