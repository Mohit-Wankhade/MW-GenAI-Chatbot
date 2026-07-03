from better_profanity import profanity
def validate_input (text):
    if not text:
        return False
    if len(text.strip()) == 0:
        return False
    if len(text) > 500:
        return False
    
    return True
def contains_profanity(text):
    return profanity.contains_profanity(text) 