import logging
from github import Github
import argparse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='debug.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Add a stream handler for console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

def star_repos(user_export_token, user_import_token, dry_run=False):
    # Create Github instances for both users
    g1 = Github(user_export_token)
    g2 = Github(user_import_token)

    try:
        # Verify authentication for both tokens
        try:
            user1 = g1.get_user()
            user1.login  # This will raise an exception if the token is invalid
            logger.info(f"Exporting stars from user: {user1.login}")
        except Exception as e:
            logger.error(f"Failed to authenticate export token: {str(e)}")
            return

        try:
            user2 = g2.get_user()
            user2.login  # This will raise an exception if the token is invalid
            logger.info(f"Importing stars to user: {user2.login}")
        except Exception as e:
            logger.error(f"Failed to authenticate import token: {str(e)}")
            return

        # Get starred repositories from user1
        starred_repos = list(user1.get_starred())
        logger.info(f"Found {len(starred_repos)} starred repositories")

        # Star the same repositories for user2
        for repo in starred_repos:
            try:
                if not dry_run:
                    user2.add_to_starred(repo.full_name)
                logger.info(f"{'Would star' if dry_run else 'Starred'} {repo.full_name}")
            except Exception as e:
                logger.error(f"Failed to star {repo.full_name}: {str(e)}")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
    finally:
        # Close the connections
        g1.close()
        g2.close()
        logger.debug("Closed Github connections")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Star GitHub repositories from one account to another.")
    parser.add_argument("--export-token", help="Access token for the account to export stars from")
    parser.add_argument("--import-token", help="Access token for the account to import stars to")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without actually starring repositories")
    args = parser.parse_args()

    logger.debug("Script started with arguments: %s", args)

    # Use environment variables if tokens are not provided as arguments
    export_token = args.export_token or os.getenv('GITHUB_EXPORT_TOKEN')
    import_token = args.import_token or os.getenv('GITHUB_IMPORT_TOKEN')

    if not export_token or not import_token:
        logger.error("Both export and import tokens are required. Provide them as arguments or in the .env file.")
        exit(1)

    if export_token == "your_export_token_here" or import_token == "your_import_token_here":
        logger.error("Please replace the placeholder tokens in the .env file with your actual GitHub tokens.")
        exit(1)

    star_repos(export_token, import_token, args.dry_run)

    logger.debug("Script completed")