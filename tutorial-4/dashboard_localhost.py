import boto3
import webbrowser

# Replace these values with your own
AWS_ACCESS_KEY_ID = 'YOUR_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'YOUR_SECRET_ACCESS_KEY'
AWS_SESSION_TOKEN = 'YOUR_SESSION_TOKEN'

# Connect to AWS
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name='us-east-1'  # Change this to your desired region
)

# Get the AWS account ID
sts_client = session.client('sts')
aws_account_id = sts_client.get_caller_identity().get('Account')

# Connect to QuickSight
quicksight = session.client('quicksight')

# Get list of dashboards
response = quicksight.list_dashboards(AwsAccountId=aws_account_id)

# Generate URL for each dashboard
for dashboard in response['DashboardSummaryList']:
    dashboard_id = dashboard['DashboardId']
    url = quicksight.get_dashboard_embed_url(
        AwsAccountId=aws_account_id,
        DashboardId=dashboard_id,
        IdentityType='IAM',
        SessionLifetimeInMinutes=60,
        UndoRedoDisabled=True
    )['EmbedUrl']

    # Open dashboard in browser
    webbrowser.open(url)
