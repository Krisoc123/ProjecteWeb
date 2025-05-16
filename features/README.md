# End-to-End Tests for Book Application

This directory contains end-to-end tests for the book application using Behave and Splinter.

## Test Features

1. **Add to Havelist** (`add_to_havelist.feature`)
   - Add books to havelist when logged in
   - Redirect to login when not authenticated

2. **Add to Wishlist** (`add_to_wishlist.feature`)
   - Add books to wishlist when logged in
   - Redirect to login when not authenticated

3. **Add Reviews** (`add_reviews.feature`)
   - Create new reviews for books
   - Redirect to login when not authenticated

4. **Update Reviews** (`update_reviews.feature`)
   - Edit your own reviews
   - Prevent editing of others' reviews

5. **Delete Reviews** (`delete_reviews.feature`)
   - Delete your own reviews
   - Prevent deletion of others' reviews

## Running Tests

To run all tests:
```bash
python manage.py behave
```

To run a specific feature:
```bash
python manage.py behave features/add_to_havelist.feature
```

## Requirements

- behave-django
- splinter
- Chrome browser with ChromeDriver

## Notes

- Tests use a headless Chrome browser by default. To see the browser UI during testing, modify the `headless` parameter in `environment.py` to `False`.
- Each test starts with a clean database state.
