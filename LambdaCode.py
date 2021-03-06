import json
import boto3

def lambda_handler(event, context):    
    # print(event) # Debug, writes input to CloudWatch log
    
    # 200 is the HTTP status code for "ok".
    status_code = 200
    retVal= {}
    retVal["data"] = []
    
    try: 
        # Data is sent to Lambda via a HTTPS POST call. We want to get to the payload send by Snowflake
        event_body = event["body"]
        payload = json.loads(event_body)
        
        for row in payload["data"]:
            sflkRowRef = row[0] # This is how Snowflake keeps track of data as it gets returned
            content = row[1]    # The data passed in from Snowflake that the input row contains.
                                # If the passed in data was a Variant, it lands here as a dictionary. Handy!
            
            # Extract anything needed from the row
            emailSubject = content['Subject']
            emailBody = content['Body']
            
            message = {"foo": "bar"} # SNS doesn't use this part for emails, but you MUST HAVE IT or the publish call will error
            client = boto3.client('sns')
            snsResponse = client.publish(
                TargetArn='<<Your Amazon SNS Topic ARN here>>',
                Message=json.dumps({'default': json.dumps(message),
                                    'email': emailBody}),
                Subject=emailSubject,
                MessageStructure='json'
            )
            
            sflkResponse={}
            sflkResponse["snsResponse"] = snsResponse #['snsResponse']['messageId']
    
            retVal["data"].append([sflkRowRef,sflkResponse])
            
        json_compatible_string_to_return = json.dumps(retVal)
    
        ## Debug, writes output to CloudWatch log
        # print('--- RESPONSE FROM LAMBDA ---')
        # print(retVal)
        
    except Exception as err:
        # 400 implies some type of error.
        status_code = 400
        # Tell caller what this function could not handle.
        json_compatible_string_to_return = event_body
        
    return {
        'statusCode': status_code, 
        'body': json_compatible_string_to_return
    }
