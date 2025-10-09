# LF1: Lex Code Hook Lambda

- **Language**: Python 3.13
- **Purpose**: Handles intents from Amazon Lex (Greeting, ThankYou, DiningSuggestions)
- **Functionality**:
  - Normalizes slot values
  - Sends DiningSuggestionsIntent data to SQS Queue
- **External Dependencies**:
  - `boto3`