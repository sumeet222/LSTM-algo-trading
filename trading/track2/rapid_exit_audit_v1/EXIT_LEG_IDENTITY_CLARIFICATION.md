# Source-schema clarification before outcome extraction

The archive has 3,978 rows sharing a case/cohort/effective-minute key.
They are distinct internal and external attribution portions of physical
netting. The full original row has no duplicates. The sealed row index
plus archive SHA256 is the stable identity. Deduplicating only by minute
would discard real shares and alter the denominator. Retain each portion
once, with its external flag, quantity, raw reference and attributed fill.
No future-reference value was read to make this schema correction.
