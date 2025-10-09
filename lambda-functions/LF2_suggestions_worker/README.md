# LF2: Suggestions Worker Lambda

- **Language**: Python 3.10
- **Purpose**: Polls SQS queue for dining requests, retrieves matching restaurant info, and sends suggestions via SES.

---

## 🔧 Functionality

1. **Triggered by CloudWatch Event** every minute.
2. **Pulls messages from SQS** (containing cuisine, location, email, etc.).
3. **Queries ElasticSearch** to find restaurant IDs matching the requested cuisine.
4. **Fetches details** from DynamoDB (`yelp-restaurants` table).
5. **Formats recommendations** and **sends email** to user via Amazon SES.
6. **Handles errors** and integrates with **Dead Letter Queue (DLQ)** for failed emails.