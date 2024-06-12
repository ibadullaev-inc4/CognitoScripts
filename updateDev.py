import boto3
from botocore.exceptions import ClientError

class CognitoUserManager:
    def __init__(self, user_pool_id, region_name):
        self.user_pool_id = user_pool_id
        self.client = boto3.client('cognito-idp', region_name=region_name)

    def list_and_update_users(self):
        paginator = self.client.get_paginator('list_users')
        response_iterator = paginator.paginate(UserPoolId=self.user_pool_id)

        for page in response_iterator:
            for user in page['Users']:
                email_verified = self.get_user_attribute(user, 'email_verified')
                email = self.get_user_attribute(user, 'email')
                
                if email_verified == 'true' and email:
                    local_part, domain = email.split('@')
                    if any(char.isupper() for char in local_part):
                        lower_case_email = email.lower()
                        if not self.email_exists(lower_case_email):
                            print(f"Updating email for user {user['Username']} from {email} to {lower_case_email}")
                            self.update_user_email(user['Username'], lower_case_email)
                            self.print_user_info(user, lower_case_email)


    def get_user_attribute(self, user, attribute_name):
        return next((attr['Value'] for attr in user['Attributes'] if attr['Name'] == attribute_name), None)



    def email_exists(self, email):
        try:
            response = self.client.list_users(
                UserPoolId=self.user_pool_id,
                Filter=f'email = "{email}" and email_verified = "true"'
            )
            for user in response['Users']:
                user_email = self.get_user_attribute(user, 'email')
                if user_email == email:
                    print(f"Found matching email: {user_email}")
                    return True
            return False
        except ClientError as e:
            print(f"An error occurred while checking email existence: {e}")
            return False


    def update_user_email(self, username, email):
        try:
            self.client.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'email_verified', 'Value': 'true'}
                ]
            )
            print(f"Email updated successfully for user {username}.")
        except ClientError as e:
            print(f"Could not update email for {username}: {e}")



    def print_user_info(self, user, email):
        user_info = {
            'Username': user['Username'],
            'Email': email,
            'Enabled': user['Enabled'],
            'EmailVerified': self.get_user_attribute(user, 'email_verified'),
            'UserStatus': user['UserStatus']
        }
        print(user_info)

if __name__ == "__main__":
    user_pool_id = ''
    region_name = ''
    manager = CognitoUserManager(user_pool_id, region_name)
    manager.list_and_update_users()
