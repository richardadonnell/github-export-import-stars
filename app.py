import logging
from github import Github, Auth
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

# Add debug logging for tokens after logger setup
logger.debug(f"Export token from env: {os.getenv('GITHUB_EXPORT_TOKEN')[:5] if os.getenv('GITHUB_EXPORT_TOKEN') else 'Not set'}...")
logger.debug(f"Import token from env: {os.getenv('GITHUB_IMPORT_TOKEN')[:5] if os.getenv('GITHUB_IMPORT_TOKEN') else 'Not set'}...")

def star_repos(user_export_token, user_import_token, dry_run=True):
    # Create Github instances for both users
    auth1 = Auth.Token(user_export_token)
    auth2 = Auth.Token(user_import_token)
    g1 = Github(auth=auth1)
    g2 = Github(auth=auth2)

    try:
        # Verify authentication for both tokens
        try:
            user1 = g1.get_user()
            user1.login  # This will raise an exception if the token is invalid
            logger.info(f"Successfully authenticated export token for user: {user1.login}")
        except Exception as e:
            logger.error(f"Failed to authenticate export token: {str(e)}")
            return

        try:
            user2 = g2.get_user()
            user2.login  # This will raise an exception if the token is invalid
            logger.info(f"Successfully authenticated import token for user: {user2.login}")
        except Exception as e:
            logger.error(f"Failed to authenticate import token: {str(e)}")
            return

        # Get starred repositories from user1
        starred_repos = list(user1.get_starred())
        logger.info(f"Found {len(starred_repos)} starred repositories")

        # If dry run, export the list of repos to a text file
        if dry_run:
            with open('repos_to_star.txt', 'w') as f:
                for repo in starred_repos:
                    f.write(f"{repo.full_name}\n")
            logger.info(f"Exported list of repos to star to 'repos_to_star.txt'")

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
    parser.add_argument("--run", action="store_true", help="Actually star repositories (default is dry run)")
    args = parser.parse_args()

    logger.debug("Script started with arguments: %s", args)

    # Modify the token reading part
    export_token = args.export_token or os.getenv('GITHUB_EXPORT_TOKEN')
    import_token = args.import_token or os.getenv('GITHUB_IMPORT_TOKEN')

    logger.debug(f"Export token: {'Set' if export_token else 'Not set'}")
    logger.debug(f"Import token: {'Set' if import_token else 'Not set'}")

    if not export_token or not import_token:
        logger.error("Both export and import tokens are required. Provide them as arguments or in the .env file.")
        exit(1)

    logger.debug(f"Export token starts with: {export_token[:5] if export_token else 'N/A'}...")
    logger.debug(f"Import token starts with: {import_token[:5] if import_token else 'N/A'}...")

    if export_token.startswith('ghp_') and import_token.startswith('ghp_'):
        star_repos(export_token, import_token, not args.run)
    else:
        logger.error(f"Invalid token format. Ensure your tokens start with 'ghp_' and are correctly set in the .env file or provided as arguments.")
        logger.debug(f"Export token prefix: {export_token[:5] if export_token else 'N/A'}")
        logger.debug(f"Import token prefix: {import_token[:5] if import_token else 'N/A'}")
        exit(1)

    logger.debug("Script completed")