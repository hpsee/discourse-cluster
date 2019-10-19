#/bin/bash

# source secrets
source .env

# Export q-a category (default)
python export_posts.py data 

# export discussion zone
DISCOURSE_CATEGORY="Area-for-open-ended-topics-of-interest" python export_posts.py data
