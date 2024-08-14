from isbnlib import is_isbn13, is_isbn10
from email_validator import validate_email, EmailNotValidError


def is_valid_isbn(isbn):
    """Validates an ISBN-10 or ISBN-13 number.

    Args:
        isbn: The ISBN to validate.

    Returns:
        True if the ISBN is valid, False otherwise.
    """

    isbn = isbn.replace('-', '')

    if len(isbn) == 10:
        return is_isbn10(isbn)
    elif len(isbn) == 13:
        return is_isbn13(isbn)
    else:
        return False


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


if __name__ == '__main__':
    check_result = is_valid_isbn("0-8436-1072-7")
    print(check_result)
