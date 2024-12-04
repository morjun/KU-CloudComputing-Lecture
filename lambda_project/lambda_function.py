import boto3
from textblob import TextBlob
import datetime

# Python runtime: 3.13

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('reviews-2021320133')
ses = boto3.client('ses')

def lambda_handler(event, context):
    user_name = event['user_name']
    review_text = event['review']
    timestamp = datetime.datetime.now().isoformat()
    sentiment = ""

    if not user_name:
        return {"statusCode": 400, "body": "User name is required"}

    if not review_text:
        return {"statusCode": 400, "body": "Review text is required"}

    print(f"Lambda Function ARN: {context.invoked_function_arn}")
    print(f"Request ID: {context.aws_request_id}")
    remaining_time = context.get_remaining_time_in_millis() / 1000  # ms -> s
    print(f"Remaining time: {remaining_time} seconds")
    print(f"Log Group: {context.log_group_name}, Log Stream: {context.log_stream_name}")

    # Sentiment Analysis
    polarity = TextBlob(review_text).sentiment.polarity
    '''
    Todo1: Use the Polarity value to determine the sentiment of the review, 
    with the standard set to 0.
    '''
    if polarity >= 0:
        sentiment = "Positive"
    elif polarity < 0:
        sentiment = "Negative"

    # Save to DynamoDB
    try:
        table.put_item(
            Item={
                "user_name": user_name,
                "review": review_text,
                "sentiment": sentiment,
                "timestamp": timestamp,
            }
        )
    except KeyError as e:
        print(f"Error saving review to DynamoDB: {e}")
        return {"statusCode": 500, "body": "Error saving review to DynamoDB"}

    # Send Email for Positive Reviews (SES 서비스 활용)
    if sentiment == "Positive":
        ses.send_email(
            Source="junmo@korea.ac.kr",
            Destination={"ToAddresses": ["junmo@korea.ac.kr"]}, # 같은 이메일 써도 됨
            Message={
                "Subject": {"Data": f"Positive Review from {user_name}"},
                "Body": {"Text": {"Data": f"{user_name} wrote: {review_text}"}}
            }
        )

    return {"statusCode": 200, "body": f"Review processed for {user_name}"}
