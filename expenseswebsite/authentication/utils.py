from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AppTokenGenerator(PasswordResetTokenGenerator):
    
    def _make_hash_value(self, user, timestamp):
        # Ensure the result is a string and includes relevant user state
        # user.pk and user.password are commonly included to invalidate the token
        # if the user's password changes or the account is deleted
        return (
            str(user.pk) + str(timestamp) +
            str(user.is_active)  # Custom user model field
        )

# Create an instance of your generator
token_generator = AppTokenGenerator()
